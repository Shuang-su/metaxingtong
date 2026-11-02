import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/front-camera-diagnostic';j=json.loads((Q/'fit-report.json').read_text());assert j['training_improved_ge25percent'];p=j['selected_pose'];f=j['selected_lens_mm'];rv=Vector(p[3:]);rotation=Matrix.Rotation(rv.length,3,rv.normalized());CV=Matrix.Diagonal((1,-1,-1));CW=(rotation.transposed()@CV).to_4x4();CW.translation=Vector(p[:3]);checks=[]
def geo():
 return {o.name:hashlib.sha256(b''.join(struct.pack('<3d',*(o.matrix_world@v.co)) for v in o.data.vertices)+str([list(p.vertices) for p in o.data.polygons]).encode()).hexdigest() for o in bpy.context.scene.objects if o.type=='MESH'}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/ferris_remake_R04_{mode}.blend'));before=geo();others={o.name:[list(r) for r in o.matrix_world] for o in bpy.context.scene.objects if o.type=='CAMERA' and o.name!='SRC_front'};c=bpy.data.objects['SRC_front'];old=[list(r) for r in c.matrix_world];c.matrix_world=CW;c.data.lens=f;bpy.context.view_layer.update();assert geo()==before;assert others=={o.name:[list(r) for r in o.matrix_world] for o in bpy.context.scene.objects if o.type=='CAMERA' and o.name!='SRC_front'}
 bpy.context.scene['revision']='R05 ONLY front conditional camera; R04 geometry exact, scene source FAIL';bpy.ops.wm.save_as_mainfile(filepath=str(R/f'models/ferris_remake_R05_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(R/f'models/ferris_remake_R05_{mode}.glb'),export_format='GLB',export_apply=True)
 checks.append({'mode':mode,'R04_geometry_worldvertex_face_hash_equal':True,'mesh_hashes':before,'all_other_cameras_equal':True,'front_old_matrix':old,'front_new_matrix':[list(r) for r in c.matrix_world],'lens':f})
 s=bpy.context.scene;s.camera=c;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=24 if mode=='material' else 12;s.cycles.use_denoising=False;s.render.filepath=str(R/f'renders/R05_native_{mode}_SRC_front.png');bpy.ops.render.render(write_still=True)
(Q/'R05-change-verification.json').write_text(json.dumps(checks,indent=2));print('R05_FRONT_DONE')
