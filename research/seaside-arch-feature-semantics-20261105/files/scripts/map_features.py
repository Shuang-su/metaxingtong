import bpy,os,json,hashlib,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));p='/workspace/scratch/fa58bfcf0425/seaside-arch-candidate-20261105/models/material.blend';bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene;cam=bpy.data.objects['SOURCE04 conditional'];dep=bpy.context.evaluated_depsgraph_get()
def project(v):q=world_to_camera_view(s,cam,v);return [1192*q.x,671*(1-q.y)],q.z
def describe(label,object_name,v,source,vertex=None):
 v=Vector(v);pixel,z=project(v);d=v-cam.location;hit,loc,n,idx,obj,mat=s.ray_cast(dep,cam.location,d.normalized(),distance=d.length+.01)
 return {'label':label,'object':object_name,'mesh_vertex_index':vertex,'world':list(v),'projected_pixel':pixel,'positive_depth':z>0,'depth':z,'source_pixel_unchanged':source,'conditional_euclidean_residual':math.dist(pixel,source),'first_hit':obj.name if hit else None,'first_hit_distance':(loc-cam.location).length if hit else None,'target_distance':d.length,'boundary_ray_caution':'Exact edge/vertex rays are numerically ambiguous; first hit is a finite test, not continuous visible silhouette proof.'}
old=json.load(open(r+'/source/old-fit04-unchanged.json'))['source_points'];out={'model_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'camera_unchanged':True,'geometry_unchanged':True,'fit_performed':False,'old_source_and_world_records_verbatim':old,'features':[]}
for point in old:
 n=point['name'];src=point['source_pixel'];record={'old_name':n,'old_source_pixel':src,'old_world':point['model_world'],'old_world_under_current_camera':describe('old author representative point',None,point['model_world'],src),'actual_mesh_candidates':[]}
 if n.startswith('round_'):
  idx={'round_left':0,'round_middle':1,'round_right':2}[n];o=bpy.data.objects['W02 round diffuser '+str(idx)];vs=[o.matrix_world@v.co for v in o.data.vertices];my=min(v.y for v in vs);front=[(i,v) for i,v in enumerate(vs) if abs(v.y-my)<1e-5];center=sum((v for i,v in front),Vector())/len(front);record['actual_mesh_candidates'].append(describe('front cap geometric centre (mean of actual cap boundary; a surface point, not fabricated mesh vertex)',o.name,center,src));record['front_cap_boundary_vertex_indices']=[i for i,v in front]
 elif n=='middle_apex':
  o=bpy.data.objects['A01 vertical arch solid'];vs=[o.matrix_world@v.co for v in o.data.vertices];mz=max(v.z for v in vs)
  for i,v in enumerate(vs):
   if abs(v.z-mz)<1e-5:record['actual_mesh_candidates'].append(describe('actual outer-radius maximum world-z vertex; front/back distinguished by world-y',o.name,v,src,i))
  i=min(range(len(vs)),key=lambda i:project(vs[i])[0][1]);record['actual_mesh_candidates'].append(describe('actual vertex with smallest projected image-y for this camera; view-dependent silhouette feature',o.name,vs[i],src,i))
 elif n.startswith('upper_'):
  o=bpy.data.objects['W03 upper coping'];vs=[o.matrix_world@v.co for v in o.data.vertices];xx=(min if n=='upper_left' else max)(v.x for v in vs);mz=max(v.z for v in vs)
  for i,v in enumerate(vs):
   if abs(v.x-xx)<1e-5 and abs(v.z-mz)<1e-5:record['actual_mesh_candidates'].append(describe('actual coping extreme-x top-z vertex, front/back candidate not uniquely identified in source',o.name,v,src,i))
 out['features'].append(record)
# Additional separately observed source04 complete lower disc, not quietly added to the old fit.
o=bpy.data.objects['W08 lower circle 0'];vs=[o.matrix_world@v.co for v in o.data.vertices];my=min(v.y for v in vs);v=sum((v for v in vs if abs(v.y-my)<1e-5),Vector())/sum(abs(v.y-my)<1e-5 for v in vs);out['additional_source_feature_not_in_old_fit']=describe('lower circle0 exact front cap centre; source04 full circular outline independently annotated',o.name,v,[262,420]);json.dump(out,open(r+'/qa/features.json','w'),indent=2)
print('FEATURE_MAP_COMPLETE')
