import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/arcade-build-20261030/scenes/arcade-dance-machine-room/models/arcade_material_R07.blend')
s=bpy.context.scene;c=bpy.data.objects['SRC02_oblique']
print('CONFIG',s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.pixel_aspect_x,s.render.pixel_aspect_y,c.data.sensor_fit,c.data.sensor_width,c.data.sensor_height,c.data.type,c.scale[:],c.data.shift_x,c.data.shift_y)
points=[[-.99275,-.1005,1.75],[.99275,-.1005,1.75],[2.35725,-.1005,1.75],[4.34275,-.1005,1.75],[-1.332375,.03,0],[1.332375,.03,0],[4.682375,.03,0],[0,-1.05,.237],[3.35,-1.05,.237]]
for p in points:
 uv=world_to_camera_view(s,c,Vector(p)); print('PROJ',p,[uv.x*1920,(1-uv.y)*1080,uv.z])
for o in bpy.data.objects:
 if o.name.startswith(('M02','M03')) and any(t in o.name for t in ['screen_inset','plinth','pad_center_ring']):
  vs=[o.matrix_world@Vector(v) for v in o.bound_box]
  print('OBJECT',o.name,'loc',list(o.location),'bounds',[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)])
