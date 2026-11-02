"""Only two parasol poles and three surfboard contacts change; core/cameras frozen."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];BASE=R/'stages/r03-source-review';O=R/'stages/r03b-mounted-review';O.mkdir(exist_ok=True)
def snapshot():
    out={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        h=hashlib.sha256()
        for v in ob.data.vertices:h.update(struct.pack('<3d',*(ob.matrix_world@v.co)))
        for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
        out[ob.name]=h.hexdigest()
    return out
states={};change_records={};camera_rows={}
allowed={'UMBRELLA_L_POLE','UMBRELLA_R_POLE','SURFBOARD_0','SURFBOARD_1','SURFBOARD_2'}
for state in ['white','material']:
    bpy.ops.wm.open_mainfile(filepath=str(BASE/('harbor-r03-review-'+state+'.blend')));sc=bpy.context.scene;before=snapshot();cams_before={o.name:list(sum(([float(v) for v in row] for row in o.matrix_world),[]))+[o.data.lens,o.data.shift_x,o.data.shift_y] for o in sc.objects if o.type=='CAMERA'}
    changes=[]
    for name in ['UMBRELLA_L_POLE','UMBRELLA_R_POLE']:
        ob=bpy.data.objects[name];old=[ob.matrix_world@v.co for v in ob.data.vertices]
        for v,c in zip(ob.data.vertices,old):c.z*=3.285/3.2;v.co=c
        ob.matrix_world=Matrix.Identity(4);ob['mount_fix']='pole end3.285 enters canopy thickness; hidden joint inferred, not source-confirmed';changes.append({'id':name,'old_top':3.2,'new_top':3.285,'reason':'remove unintended pole/canopy gap with slight inferred embedded joint'})
    for i in range(3):
        ob=bpy.data.objects['SURFBOARD_'+str(i)];bottom=min((ob.matrix_world@v.co).z for v in ob.data.vertices);ob.location.z-=bottom;bpy.context.view_layer.update();ob['mount_fix']='lowest actual mesh vertex placed at sand z0; rear lean support still unknown';changes.append({'id':ob.name,'old_min_world_z':bottom,'translation_z':-bottom,'new_min_world_z':min((ob.matrix_world@v.co).z for v in ob.data.vertices),'reason':'remove unintentional board-ground gap; not a physics/stability claim'})
    after=snapshot();changed={k for k in before if before[k]!=after[k]};assert changed==allowed,(changed,allowed)
    cams_after={o.name:list(sum(([float(v) for v in row] for row in o.matrix_world),[]))+[o.data.lens,o.data.shift_x,o.data.shift_y] for o in sc.objects if o.type=='CAMERA'};assert cams_before==cams_after
    sc['technical_mount_stage']='r03b only five accessory mount contacts corrected, core and cameras unchanged'
    bpy.ops.wm.save_as_mainfile(filepath=str(O/('harbor-r03b-'+state+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(O/('harbor-r03b-'+state+'.glb')),export_format='GLB',export_cameras=True,export_lights=False,export_extras=True)
    states[state]=after;change_records[state]=changes;camera_rows[state]=cams_after
assert states['white']==states['material'];assert camera_rows['white']==camera_rows['material']
(O/'geometry-identity.json').write_text(json.dumps({'white_material_exact_world_geometry_match':True,'changed_from_r03':sorted(allowed),'unchanged_object_count':len(states['white'])-len(allowed),'camera_poses_lens_shifts_unchanged':True,'object_hashes':states['white']},indent=2))
(O/'mount-fixes.json').write_text(json.dumps(change_records,indent=2))
(O/'source-cameras.json').write_bytes((BASE/'source-cameras.json').read_bytes())
print('R03B_MOUNTS_READY',len(states['white']),change_records['white'])
