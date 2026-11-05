import bpy,os
from mathutils import Vector
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');s=bpy.context.scene
 for n,loc,t,lens in [('UMBRELLA_FRONT_DIAG',(6.4,-5.5,4),(6.4,1.15,3.65),42),('UMBRELLA_UNDERSIDE_DIAG',(10,-3,2.4),(6.4,1.15,3.5),48)]:
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=lens
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
