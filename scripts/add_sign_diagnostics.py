import bpy,os
from mathutils import Vector
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');s=bpy.context.scene
 for n,loc,t,lens in [('SIGN_FRONT_DIAG',(0,-3.8,3.5),(0,3.16,3.3),48),('SIGN_LEFT_OBLIQUE',(-4.2,-.4,4.2),(-1.5,3.16,3.3),62)]:
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=lens
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
