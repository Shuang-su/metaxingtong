import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/ferris-cabin-build-20261030/scenes/ferris-wheel-cabin/models/ferris_cabin_r07_material.blend');s=bpy.context.scene;c=bpy.data.objects['SRC_high_bitrate'];print('CAM',list(c.location),'screen_right_world',list(c.matrix_world.col[0].xyz),'forward',list(-c.matrix_world.col[2].xyz))
for name in ['cream_bezel_1_0','cream_bezel_2_0','cream_bezel_2_1','cream_bezel_3_0','cream_bezel_5_0','cream_bezel_6_0','cream_bezel_6_1','cream_bezel_7_0']:
 o=bpy.data.objects[name];v=[o.matrix_world@x.co for x in o.data.vertices[:36]];a=(v[17]+v[18])/2;b=(v[35]+v[0])/2;ctr=(a+b)/2
 def pro(p):
  q=world_to_camera_view(s,c,p);return [round(q.x*1920,2),round((1-q.y)*1080,2),round(q.z,3)]
 print(name,'center_world',list(ctr),'image',pro(ctr),'u-negative17/18',pro(a),'u-positive35/0',pro(b))
