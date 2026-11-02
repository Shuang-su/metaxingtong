import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'stages/r01-core-white';Q=O/'preflight';Q.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'harbor-core-r01-white.blend'))
sc=bpy.context.scene
obs=[o for o in sc.objects if o.type=='MESH'];report=[];bvhs={};worldverts={};boxes={}
for ob in obs:
    bm=bmesh.new();bm.from_mesh(ob.data)
    report.append({'id':ob.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)})
    bm.transform(ob.matrix_world);bvhs[ob.name]=BVHTree.FromBMesh(bm,epsilon=1e-7);bm.free()
    vs=[ob.matrix_world@v.co for v in ob.data.vertices];worldverts[ob.name]=vs;boxes[ob.name]=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
(Q/'per-object-topology.json').write_text(json.dumps(report,indent=2))
def inside(p,bvh):
    nearest=bvh.find_nearest(p)
    if nearest[0] is None or nearest[3]<2e-5:return False,0.0
    votes=0
    for d in [Vector((1,.137,.213)).normalized(),Vector((.173,1,.271)).normalized(),Vector((.19,.31,1)).normalized()]:
        q=p.copy();hits=0
        for _ in range(100):
            hit,n,idx,dist=bvh.ray_cast(q,d,100)
            if hit is None:break
            hits+=1;q=hit+d*1e-5
        votes+=(hits%2)
    return votes>=2,nearest[3]
pairs=[]
for i,a in enumerate(obs):
 for b in obs[i+1:]:
    aa,bb=boxes[a.name],boxes[b.name]
    if any(aa[1][k]<bb[0][k]-1e-5 or bb[1][k]<aa[0][k]-1e-5 for k in range(3)):continue
    overlap=bvhs[a.name].overlap(bvhs[b.name]);pen=[]
    for left,right in [(a,b),(b,a)]:
        # All source vertices, not a thumbnail proxy. Contacts under2e-5 ignored.
        ds=[dist for p in worldverts[left.name] for yes,dist in [inside(p,bvhs[right.name])] if yes]
        if ds:pen.append({'vertices_from':left.name,'inside_count':len(ds),'max_depth_model_units':max(ds)})
    if overlap or pen:pairs.append({'a':a.name,'b':b.name,'triangle_overlap_count':len(overlap),'interior_vertices':pen,'classification':'review needed: contact and intentional joints not automatically failures'})
(Q/'assembly-contact-candidates.json').write_text(json.dumps({'method':'world-space closed-mesh BVH overlap plus all-vertex 3-direction odd-ray containment; detects many interpenetrations, not a complete continuous collision proof','pairs':pairs},indent=2))
sc.render.resolution_x=512;sc.render.resolution_y=320;sc.cycles.samples=8;sc.cycles.use_denoising=False
for i in range(8):
    name='CHECK_%02d_%03d'%(i+1,i*45);sc.camera=bpy.data.objects[name];sc.render.filepath=str(Q/(name+'.png'));bpy.ops.render.render(write_still=True)
# Additional source-front conditional diagnostic, no source acceptance claimed.
sc.render.resolution_x=640;sc.render.resolution_y=360;sc.camera=bpy.data.objects['SOURCE_PREVIEW_FRONT_CONDITIONAL'];sc.render.filepath=str(Q/'SOURCE_FRONT_UNCALIBRATED.png');bpy.ops.render.render(write_still=True)
before={o.name:boxes[o.name] for o in obs}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(O/'harbor-core-r01-white.glb'))
after={}
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
    vs=[ob.matrix_world@v.co for v in ob.data.vertices];after[ob.name]=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
diff=[]
for name in sorted(before.keys()&after.keys()):
    delta=max(abs(before[name][j][k]-after[name][j][k]) for j in range(2) for k in range(3));diff.append({'id':name,'max_bbox_delta':delta})
(Q/'actual-glb-reimport.json').write_text(json.dumps({'actual_import_run':True,'source_mesh_objects':len(before),'import_mesh_objects':len(after),'missing':sorted(before.keys()-after.keys()),'extra':sorted(after.keys()-before.keys()),'bbox_deltas':diff,'material_and_render_equivalence':'not yet checked; GLB import is not source acceptance'},indent=2))
print('PREFLIGHT_COMPLETE',len(report),len(pairs))
