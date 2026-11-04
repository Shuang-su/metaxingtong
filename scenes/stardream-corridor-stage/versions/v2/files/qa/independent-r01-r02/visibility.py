import bpy,json,pathlib,numpy as np
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105');bpy.ops.wm.open_mainfile(filepath=str(P/'models/R02_material.blend'));s=bpy.context.scene;d=bpy.context.evaluated_depsgraph_get();out={}
for name,r in json.load(open(P/'qa/R02-line-fit.json')).items():
 c=bpy.data.objects[name];C=np.array(c.location);rot=np.array(c.matrix_world)[:3,:3];f=c.data.lens/36*1192;lst=[]
 for key,w in r['world_line_assumptions'].items():
  a,b=np.array(w);v=b-a
  for obs in r['observed_segments'][key]:
   dr=rot@np.array([(obs[0]-596)/f,(335.5-obs[1])/f,-1]);dr/=np.linalg.norm(dr);A=np.column_stack([dr,-v]);t,u=np.linalg.lstsq(A,a-C,rcond=None)[0];p=a+u*v;ray=Vector(p-C);length=ray.length;hit,loc,n,idx,obj,m=s.ray_cast(d,Vector(C),ray.normalized(),distance=length+.001)
   lst.append({'line':key,'observed':obs,'closest_ray_depth':float(t),'line_parameter':float(u),'within_finite_line':bool(0<=u<=1),'ray_line_gap_working_units':float(np.linalg.norm(C+t*dr-p)),'first_hit_object':obj.name if hit else None,'hit_before_target_distance':float(length-(loc-Vector(C)).length) if hit else None})
 out[name]=lst
(Q/'line-finite-visibility.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
