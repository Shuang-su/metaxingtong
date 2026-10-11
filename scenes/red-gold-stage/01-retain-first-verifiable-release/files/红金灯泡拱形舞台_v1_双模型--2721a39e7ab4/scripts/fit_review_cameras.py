import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1';bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_textured.blend');S=bpy.context.scene;cam=S.camera;p=R+'/qa/build_facts.json';j=json.load(open(p));corners=[Vector((x,y,z)) for x in [-8,8] for y in [-7.5,4.5] for z in [-.2,6.35]];report={}
for name,v in j['views'].items():
 if name=='源图匹配':continue
 loc,target,lens=v;target=Vector((0,-1.5,2.8));direction=(Vector(loc)-Vector(v[1])).normalized();dist=(Vector(loc)-Vector(v[1])).length;cam.data.lens=lens
 for _ in range(100):
  cam.location=target+direction*dist;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();qs=[world_to_camera_view(S,cam,c) for c in corners]
  if all(.055<q.x<.945 and .055<q.y<.945 and q.z>0 for q in qs):break
  dist*=1.06
 j['views'][name]=[list(cam.location),list(target),lens];report[name]={'distance':dist,'projected_bbox':[min(q.x for q in qs),min(q.y for q in qs),max(q.x for q in qs),max(q.y for q in qs)]}
json.dump(j,open(p,'w'),ensure_ascii=False,indent=2);json.dump(report,open(R+'/qa/camera_full_bounds.json','w'),ensure_ascii=False,indent=2)
