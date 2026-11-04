"""Run one R06 leaf-only trial after the actual original BLEND is recovered.

This refuses reconstructed or wrong input bytes. No automatic download, scene
regeneration, camera fitting, visibility edit, high-resolution suite or overwrite.
"""
import bpy, bmesh, pathlib, sys, json, argparse, hashlib, struct, datetime, math
from dataclasses import asdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from leaf_local_warp import Parameters, forward, inverse

EXPECTED_SHA='4af868869ee7f7eebf0c8569b16cef356143c5425c888e98a4f56dee25449a12'
CAMERAS=['SOURCE_092142973_SIDE','SOURCE_100762992_TOP','SOURCE_108755584_OBLIQUE','AUX_006585758_REAR']
TARGETS=['LEAF_001_ThinConcaveShell','LEAF_002_CentralMidrib']+[
    'LEAF_003_Branch_%02d_%s'%(i,side) for i in range(9) for side in ['L','R']]
p=argparse.ArgumentParser()
p.add_argument('--input',required=True)
p.add_argument('--output',required=True)
p.add_argument('--trial',required=True)
p.add_argument('--belly-dz',type=float,default=0)
p.add_argument('--shoulder-fraction',type=float,default=0)
p.add_argument('--render',action='store_true')
p.add_argument('--checkpoint-name',default=None,help='Optional new .blend basename in the original models directory, never an original filename.')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
model=pathlib.Path(a.input).resolve();out=pathlib.Path(a.output).resolve()
assert model.is_file(),'Original R06 BLEND still unavailable; stop without regenerating it.'
assert hashlib.sha256(model.read_bytes()).hexdigest()==EXPECTED_SHA,'Input is not the exact archived original.'
assert not out.exists(),'Preserve previous trials: select a new output directory.'
params=Parameters(belly_dz=a.belly_dz,shoulder_fraction=a.shoulder_fraction);params.validate()
assert not (params.belly_dz and params.shoulder_fraction),'First experiments must be single-variable.'
bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene
assert len([o for o in s.objects if o.type=='MESH'])==2704
assert len([o for o in s.objects if o.type=='CAMERA'])==13
assert set(o.name for o in s.objects if o.name.startswith('LEAF_'))==set(TARGETS)
for name in TARGETS:
    o=s.objects[name];assert o.type=='MESH' and not o.modifiers
    assert o.data.users==1,'Shared target mesh requires explicit review; do not mutate another instance.'
dependencies=[]
for im in bpy.data.images:
    if im.source=='FILE':
        q=pathlib.Path(bpy.path.abspath(im.filepath))
        assert q.is_file() or im.packed_file,'Missing texture: '+str(q)
        dependencies.append(dict(name=im.name,path=im.filepath,sha256=hashlib.sha256(q.read_bytes()).hexdigest() if q.is_file() else None))

def snapshot():
    dg=bpy.context.evaluated_depsgraph_get();meshes={};camera={};lights={};visibility={}
    for o in s.objects:
        visibility[o.name]=[o.hide_render,o.hide_viewport,o.hide_get()]
        if o.type=='MESH':
            e=o.evaluated_get(dg);m=e.to_mesh();h=hashlib.sha256()
            for v in m.vertices:h.update(struct.pack('<3d',*(o.matrix_world@v.co)))
            for f in m.polygons:
                h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
            meshes[o.name]=h.hexdigest();e.to_mesh_clear()
        elif o.type=='CAMERA':
            d=o.data;camera[o.name]=dict(matrix=[list(r) for r in o.matrix_world],type=d.type,lens=d.lens,
                sensor_fit=d.sensor_fit,sensor_width=d.sensor_width,sensor_height=d.sensor_height,
                shift_x=d.shift_x,shift_y=d.shift_y,clip_start=d.clip_start,clip_end=d.clip_end)
        elif o.type=='LIGHT':
            lights[o.name]=dict(matrix=[list(r) for r in o.matrix_world],type=o.data.type,
                energy=o.data.energy,color=list(o.data.color))
    return dict(meshes=meshes,cameras=camera,lights=lights,visibility=visibility,
        collections={c.name:[c.hide_render,c.hide_viewport] for c in bpy.data.collections})

before=snapshot();inverse_errors=[]
for name in TARGETS:
    o=s.objects[name];inv=o.matrix_world.inverted()
    for v in o.data.vertices:
        old=o.matrix_world@v.co;new=forward(old,params)
        inverse_errors.append(max(abs(inverse(new,params)[i]-old[i]) for i in range(3)))
        v.co=inv@Vector(new)
    o.data.update()
bpy.context.view_layer.update();after=snapshot()
assert set(before['meshes'])==set(after['meshes'])
changed=[k for k in before['meshes'] if before['meshes'][k]!=after['meshes'][k]]
assert set(changed)<=set(TARGETS)
if params==Parameters():assert not changed,'Zero-parameter baseline unexpectedly changed a mesh.'
for k in ['cameras','lights','visibility','collections']:assert before[k]==after[k]
assert max(inverse_errors)<1e-10
topology=[]
for name in TARGETS:
    bm=bmesh.new();bm.from_mesh(s.objects[name].data);bm.normal_update()
    row=dict(name=name,boundary_edges=sum(e.is_boundary for e in bm.edges),
        nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
        zero_area_faces=sum(f.calc_area()<1e-12 for f in bm.faces),signed_volume=bm.calc_volume(signed=True))
    bm.free();assert not row['boundary_edges'] and not row['nonmanifold_edges'] and not row['zero_area_faces']
    if name==TARGETS[0]:assert row['signed_volume']>0
    topology.append(row)

# Test the new finite mesh samples, mapped back into the original analytic XY
# domain. This does not establish continuous tube-shell collisions or contact.
def width(u):return 1.58*max(0,1-u*u)**.72*(1+.06*math.sin(3*math.pi*u))
footprints=[]
for name in TARGETS[1:]:
    o=s.objects[name];m=o.data;points=[o.matrix_world@v.co for v in m.vertices]
    probes=points+[(points[e.vertices[0]]+points[e.vertices[1]])*.5 for e in m.edges]+[
        sum((points[i] for i in f.vertices),Vector())/len(f.vertices) for f in m.polygons]
    bad=[];vals=[]
    for i,v in enumerate(probes):
        x,y,z=inverse(v,params);u=x/4.65;w=width(u);q=y/w if w else None
        if abs(u)>=1 or q is None or abs(q)>=1:bad.append(i)
        elif q is not None:vals.append(abs(q))
    assert not bad,'Finite vein footprint samples escaped: '+name
    footprints.append(dict(name=name,samples=len(probes),outside_sample_count=len(bad),max_abs_normalized_width=max(vals)))

# Real, bounded shell-only vertical ray probes. They exclude the water and do
# not measure normal thickness, metric scale, buoyancy or source correctness.
o=s.objects[TARGETS[0]];m=o.data;vv=[o.matrix_world@v.co for v in m.vertices]
tree=BVHTree.FromPolygons(vv,[list(f.vertices) for f in m.polygons]);rays=[]
for i in range(25):
    u=-.9+1.8*i/24
    for j in range(9):
        q=forward((4.65*u,width(u)*(-.85+1.7*j/8),8),params)
        origin=Vector((q[0],q[1],8));direction=Vector((0,0,-1))
        loc,normal,index,d=tree.ray_cast(origin,direction,20)
        assert loc is not None
        loc2,normal2,index2,d2=tree.ray_cast(loc+direction*1e-5,direction,20)
        assert loc2 is not None and d2>0
        rays.append(dict(x=q[0],y=q[1],vertical_thickness=d2+1e-5))

out.mkdir(parents=True)
report=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),trial=a.trial,
    input_path=str(model),input_sha256=EXPECTED_SHA,parameters=asdict(params),
    changed_meshes=changed,unchanged_mesh_count=len(before['meshes'])-len(changed),
    outside_target_geometry_unchanged=True,cameras_lights_visibility_unchanged=True,
    before=before,after=after,topology=topology,finite_vein_footprints=footprints,
    shell_vertical_ray_scope='225 bounded shell-only vertical double hits, not normal or metric thickness',
    shell_vertical_rays=rays,max_point_inverse_error=max(inverse_errors),dependencies=dependencies,
    scope='One globally shared leaf-only deformation, three primary camera hypotheses and one auxiliary. No camera-conditioned geometry.',
    source_accepted=False,source_outline_metrics='Pending actual source-edge annotations and comparison.',
    not_proved=['normal-direction shell thickness','continuous mesh intersections','water contact/buoyancy','source camera calibration','source fidelity'])
if a.checkpoint_name:
    assert '/' not in a.checkpoint_name and a.checkpoint_name.endswith('.blend') and a.checkpoint_name.startswith('lakeleaf-r07-')
    checkpoint=model.parent/a.checkpoint_name;assert not checkpoint.exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint));assert checkpoint.stat().st_size<100*1024*1024
    report['checkpoint']=dict(path=str(checkpoint),bytes=checkpoint.stat().st_size,sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest())
if a.render:
    s.render.engine='CYCLES';s.cycles.samples=6;s.cycles.use_denoising=False
    s.render.threads_mode='FIXED';s.render.threads=2;assert s.render.threads==2,'Use CLI -t 2 for this preview.'
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
    s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=25
    report['renders']=[]
    for name in CAMERAS:
        s.camera=s.objects[name];dest=out/(name+'.png');s.render.filepath=str(dest)
        bpy.ops.render.render(write_still=True)
        row=dict(camera=name,size=[960,540],percentage=25,samples=6,threads=s.render.threads,denoising=False,
            input_sha256=EXPECTED_SHA,trial_parameters=asdict(params),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
        dest.with_suffix('.json').write_text(json.dumps(row,indent=2)+'\n');report['renders'].append(row)
    assert snapshot()==after,'A render changed geometry, cameras, lighting or visibility.'
assert hashlib.sha256(model.read_bytes()).hexdigest()==EXPECTED_SHA
(out/'trial-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Guarded trial complete; original file unchanged; source acceptance remains false.')
