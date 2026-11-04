import bpy,pathlib,json,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-portal-semantic-qa-20261105');f=P/'models/R09_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();r={'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'cameras':{}}
for cn in ['SOURCE_13_high','SOURCE_14_front','SOURCE_15_exterior']:
 c=bpy.data.objects[cn];out={'position':list(c.matrix_world.translation),'door_samples':{}}
 for k in [0,8]:
  n=f'DOOR_{k:02d}_gold_arch';o=bpy.data.objects[n];vs=[o.matrix_world@v.co for v in o.data.vertices];samples=[]
  for i in sorted(set([min(range(len(vs)),key=lambda i:vs[i].x),max(range(len(vs)),key=lambda i:vs[i].x),max(range(len(vs)),key=lambda i:vs[i].z)])):
   p=vs[i];uv=world_to_camera_view(s,c,p);vec=p-c.matrix_world.translation;hit,loc,no,fi,obj,mat=s.ray_cast(dg,c.matrix_world.translation,vec.normalized(),distance=vec.length+.001)
   samples.append({'vertex':i,'world':list(p),'pixel':[uv.x*1192,(1-uv.y)*671],'positive_depth':uv.z>0,'in_image':0<=uv.x<=1 and 0<=uv.y<=1,'nearest_object':obj.name if hit else None,'hit_world':list(loc)if hit else None,'target_distance':vec.length,'hit_distance':(loc-c.matrix_world.translation).length if hit else None})
  out['door_samples'][n]=samples
 r['cameras'][cn]=out
(Q/'model-door-rays.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
