import bpy,pathlib,json
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parents[1];j=json.load(open(R/'qa/R09-4k-camera-training.json'));t=j['trials'][j['chosen_trial']]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/('models/R08_'+mode+'.blend')))
 old=bpy.data.objects['SOURCE_F_top'];c=old.copy();c.data=old.data.copy();c.name='SOURCE_G_4K_top';bpy.context.scene.collection.objects.link(c)
 m=Matrix(t['camera_to_world']).to_4x4();m.translation=Vector(t['parameters'][:3]);c.matrix_world=m;c['source_width']=3840;c['source_height']=2160;c['source_time']=503.06141;c['source_video']='BV11jCEBiEwE';c['role']='new observed 4K source: conditional manual training pose, FAILED';c.data.lens=50;c.data.sensor_width=36
 bpy.ops.wm.save_as_mainfile(filepath=str(R/('models/R09_'+mode+'.blend')));bpy.ops.export_scene.gltf(filepath=str(R/('models/R09_'+mode+'.glb')),export_format='GLB',export_apply=True,export_cameras=True)
