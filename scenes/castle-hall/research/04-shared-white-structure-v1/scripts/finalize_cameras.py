import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
for basename in ['CastleHall_Shared_Structure_Candidate','CastleHall_Shared_White_Candidate']:
 P=R/'models'/f'{basename}.blend';bpy.ops.wm.open_mainfile(filepath=str(P));S=bpy.context.scene
 for name,path in [('HOLDOUT_HD_4527_SIDE','holdout_camera_4527.json'),('HOLDOUT_HD_4509_FRONT','holdout_camera_4509.json')]:
  data=json.loads((R/'qa'/path).read_text());d=bpy.data.cameras.new(name);d.lens=data['lens_mm'];d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.clip_start=.03;d.clip_end=200;o=bpy.data.objects.new(name,d);bpy.data.collections['09_Cameras'].objects.link(o);rr=Vector(data['right']);up=Vector(data['up']);fw=Vector(data['forward']);o.matrix_world=Matrix((rr,up,-fw)).transposed().to_4x4();o.location=data['location'];o['role']=data['role']
 S.camera=bpy.data.objects['CANDIDATE_NORMAL_MAIN'];S.render.resolution_percentage=100;S.cycles.samples=16
 bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
 if 'White' in basename:bpy.ops.export_scene.gltf(filepath=str(R/'models'/f'{basename}.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=False,export_extras=True)
print('CAMERAS_FINALIZED')
