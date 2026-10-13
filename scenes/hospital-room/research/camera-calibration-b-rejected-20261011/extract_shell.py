import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080
ob=bpy.data.objects['ROOM_SHELL__joined_solid__hidden_extents_inferred'];out=[]
for v in ob.data.vertices:
 p=ob.matrix_world@v.co
 if p.z<2.5:continue
 rec={'vertex':v.index,'xyz':list(p)}
 for tag,n in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed')]:
  q=world_to_camera_view(s,bpy.data.objects[n],p);rec[tag]=[q.x*1920,(1-q.y)*1080]
 out.append(rec)
open('/workspace/scratch/fa58bfcf0425/hospital_object_audit/camera_calibration_b/shell_vertices.json','w').write(json.dumps(out,indent=2))
