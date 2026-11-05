import bpy,os,json
from mathutils import Vector
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/seaside-arch-candidate-20261105/models/material.blend');s=bpy.context.scene;cam=bpy.data.objects['SOURCE04 conditional'];dep=bpy.context.evaluated_depsgraph_get();d=json.load(open(r+'/qa/features.json'));out=[]
for f in d['features']:
 for item in f['actual_mesh_candidates']:
  idx=item['mesh_vertex_index']
  if idx is None:continue
  o=bpy.data.objects[item['object']];v=o.data.vertices[idx].co
  for poly in o.data.polygons:
   if idx not in poly.vertices:continue
   q=o.matrix_world@(v.lerp(poly.center,.01));ray=q-cam.location;hit,loc,n,face,obj,m=s.ray_cast(dep,cam.location,ray.normalized(),distance=ray.length+.002)
   out.append({'old_source_feature':f['old_name'],'candidate_vertex_index':idx,'object':o.name,'adjacent_polygon':poly.index,'polygon_normal':list(poly.normal),'probe_fraction_toward_polygon_center':.01,'probe_world':list(q),'first_hit':obj.name if hit else None,'first_hit_polygon':face if hit else None,'target_point_visible_within_0_0001':bool(hit and abs((loc-cam.location).length-ray.length)<.0001),'target_distance':ray.length,'hit_distance':(loc-cam.location).length if hit else None})
json.dump({'scope':'These are adjacent-face visibility probes, not substitute source pixels or fitted points. Exact silhouette vertex rays may miss numerically. No source occluders/characters modelled, so model first hit cannot prove source visibility.','probes':out},open(r+'/qa/adjacent-face-probes.json','w'),indent=2)
