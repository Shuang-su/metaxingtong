import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
Q=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(Q/'frozen/models/material.blend'));s=bpy.context.scene;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();out={}
for n in ['SIGN_L_curl_proxy','SIGN_R_curl_proxy']:
 o=bpy.data.objects[n];o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];pts=[sum((vs[i] for i in t.vertices),Vector())/3 for t in o.data.loop_triangles];out[n]={}
 for cn in ['SOURCE03 conditional','SOURCE04 conditional','SIGN_FRONT_DIAG','SIGN_LEFT_OBLIQUE']:
  c=bpy.data.objects[cn];cnt={'triangle_centroids':len(pts),'inframe_positive':0,'visible_target_within_1e-4':0,'first_hit_objects':{},'same_object_but_nearer_surface':0}
  for p in pts:
   q=world_to_camera_view(s,c,p)
   if not(q.z>0 and 0<=q.x<=1 and 0<=q.y<=1):continue
   cnt['inframe_positive']+=1;d=p-c.matrix_world.translation;hit,loc,_,_,obj,_=s.ray_cast(dep,c.matrix_world.translation,d.normalized(),distance=d.length+.002);name=obj.name if hit else 'NO_HIT';cnt['first_hit_objects'][name]=cnt['first_hit_objects'].get(name,0)+1
   vis=hit and abs((loc-c.matrix_world.translation).length-d.length)<1e-4
   if vis:cnt['visible_target_within_1e-4']+=1
   if hit and name==n and not vis:cnt['same_object_but_nearer_surface']+=1
  out[n][cn]=cnt
(Q/'curl_visibility.json').write_text(json.dumps(out,indent=2));print('DONE')
