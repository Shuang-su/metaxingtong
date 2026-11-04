import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
V=Path(__file__).resolve().parents[1];R=V.parents[1]
f=json.load(open(R/'qa/camera-fit.json'));T=Matrix(f['rotation']).to_4x4();T.translation=Vector(f['translation']);a=Matrix.Rotation(math.radians(45),4,'X');a.translation=Vector((0,.6,-.025))+a.to_3x3()@Vector((0,-.6,0))
for variant in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'versions/V03/models/phone-{variant}.blend'));s=bpy.context.scene;o=bpy.data.objects['P04_rear_leaf_unseen_geometry_INFERRED'];o.matrix_world=T@a;o['conditional_angle_degrees']=45;o['angle_status']='Only a representative conditional fit to one uncertain visible middle edge; not a recovered physical angle.';bpy.context.view_layer.update()
 s.camera=bpy.data.objects['SOURCE7_CONDITIONAL_NOT_CALIBRATED'];s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=16;s.cycles.use_denoising=False
 state=json.load(open(R/f'versions/V03/qa/{variant}-scene-state.json'));state['source_version']='f8b81787d488c7341ca51304e507e5ec746793c1';state['geometry_change']={'only_object':o.name,'angle_degrees':45,'pivot_local':[0,.6,-.025],'matrix_world':[list(row) for row in o.matrix_world],'status':'SOURCE_FAILED overall; middle-edge conditional improvement only, unknown bottom/ground/back/true angle.'}
 json.dump(state,open(V/f'qa/{variant}-scene-state.json','w'),indent=2)
 bpy.ops.wm.save_as_mainfile(filepath=str(V/f'models/phone-{variant}.blend'))
 bpy.ops.object.select_all(action='DESELECT')
 for ob in s.objects:
  if ob.type in ['MESH','CAMERA']:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(V/f'models/phone-{variant}.glb'),export_format='GLB',use_selection=True,export_cameras=True,export_lights=False)
