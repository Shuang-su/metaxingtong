import bpy,json,math,pathlib,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104');f=P/'models/R06_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();d=json.load(open(P/'qa/R06-bounded-fit.json'));R={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'resolution':[s.render.resolution_x,s.render.resolution_y],'sources':{}}
star=bpy.data.objects['FLOOR_four_point_inlay'];vs=[star.matrix_world@v.co for v in star.data.vertices]
for n,e in d.items():
 cam=bpy.data.objects[n];pts=[]
 for pt,obs in zip(e['world'],e['observed']):
  p=Vector(pt);uv=world_to_camera_view(s,cam,p);pix=[uv.x*s.render.resolution_x,(1-uv.y)*s.render.resolution_y];direction=p-cam.matrix_world.translation;hit,loc,norm,idx,obj,mat=s.ray_cast(deps,cam.matrix_world.translation,direction.normalized(),distance=direction.length+.002)
  pts.append({'world':pt,'actual_star_nearest_vertex':min((p-v).length for v in vs),'observed':obs,'projected':pix,'error_px':math.dist(pix,obs),'forward_depth':uv.z,'first_hit':obj.name if hit else None,'hit_distance':(loc-cam.matrix_world.translation).length if hit else None,'target_distance':direction.length})
 R['sources'][n]={'lens':cam.data.lens,'radial':math.hypot(cam.location.x,cam.location.y),'points':pts,'mean':sum(p['error_px'] for p in pts)/len(pts),'max':max(p['error_px'] for p in pts)}
R['limits']='Same four training points, not held-out validation. Rays only to these eight tips, not full-image visibility or free-space camera volume. Manual pixel uncertainty is subjective.'
(Q/'R06-projection-check.json').write_text(json.dumps(R,indent=2));print('DONE',[(n,v['mean'],v['max'],[p['first_hit'] for p in v['points']]) for n,v in R['sources'].items()])
