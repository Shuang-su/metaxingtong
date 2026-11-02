import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_remake_R03_material.blend'));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;out=[]
for name in ['SRC_front','SRC_oblique']:
 for pt in [(0,-.229,2.635),(1.16,-.229,1.605),(0,-1.65,.202),(3.5,-.085,.16)]:
  q=world_to_camera_view(s,bpy.data.objects[name],Vector(pt));out.append({'camera':name,'world':pt,'blender_pixels':[q.x*1920,(1-q.y)*1080]})
(D/'qa/camera-new-source/blender_projection_crosscheck.json').write_text(json.dumps(out,indent=2))
