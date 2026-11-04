"""Conditional two-view diagnostic, NOT reconstruction or held-out validation."""
from pathlib import Path
import json,hashlib,numpy as np
from scipy.optimize import least_squares
OUT=Path(__file__).resolve().parent;R=OUT/'inputs'
files=[R/'R05-camera-training.json',R/'R09-4k-camera-training.json'];js=[json.load(open(p)) for p in files];sizes=[(1920,1080),(3840,2160)];annot=[20,40];cams=[]
assert js[0]['ids']==js[1]['ids']
for j,(w,h) in zip(js,sizes):
 t=j['trials'][j['chosen_trial']];cams.append((np.array(t['parameters'][:3]),np.array(t['camera_to_world']),j['focal_mm']/j['sensor_width_mm']*w,w/2,h/2))
def project(x,c):
 o,R,f,cx,cy=c;q=(x-o)@R;z=-q[2];safe=max(z,.001);return np.array([cx+f*q[0]/safe,cy-f*q[1]/safe]),z
rows=[]
for i,name in enumerate(js[0]['ids']):
 uv=[np.array(j['source_pixels'][i],dtype=float) for j in js];rays=[]
 for c,v in zip(cams,uv):
  o,R,f,cx,cy=c;d=R@np.array([(v[0]-cx)/f,-(v[1]-cy)/f,-1]);rays.append(d/np.linalg.norm(d))
 A=np.column_stack([rays[0],-rays[1]]);depth=np.linalg.lstsq(A,cams[1][0]-cams[0][0],rcond=None)[0];p=[cams[k][0]+depth[k]*rays[k] for k in [0,1]];mid=(p[0]+p[1])/2;sv=np.linalg.svd(A,compute_uv=False)
 def fun(x):
  parts=[]
  for k in [0,1]:
   v,d=project(x,cams[k]);parts.extend((v-uv[k])/annot[k]);parts.append(min(d-.1,0)*100)
  return np.array(parts)
 fit=least_squares(fun,mid,max_nfev=1000);before=np.array(js[0]['world_hypotheses'][i]);errors=[]
 for k in [0,1]:
  a,da=project(before,cams[k]);b,db=project(fit.x,cams[k]);errors.append({'view':'F' if k==0 else 'G','original_error_px':float(np.linalg.norm(a-uv[k])),'conditional_fit_error_px':float(np.linalg.norm(b-uv[k])),'residual_px':(b-uv[k]).tolist(),'positive_depth':float(db)})
 rows.append({'id':name,'raw_manual_pixels':[x.tolist() for x in uv],'ray_parallax_deg':float(np.degrees(np.arccos(np.clip(np.dot(*rays),-1,1)))),'closest_ray_parameters':depth.tolist(),'closest_ray_gap_working_units':float(np.linalg.norm(p[0]-p[1])),'ray_system_condition_number':float(sv[0]/sv[-1]),'conditional_world_point_not_applied':fit.x.tolist(),'original_world_hypothesis':before.tolist(),'displacement_not_applied':(fit.x-before).tolist(),'errors':errors,'solver_success':bool(fit.success)})
out={'method':'same provisional IDs, fixed stored conditional F/G cameras and intrinsics; linear closest rays then normalized nonlinear reprojection, no model edit','source_inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_image_sha256':j['source_sha256']} for p,j in zip(files,js)],'annotation_scales_px':annot,'scale_note':'subjective approximate annotation scales from prior reports, NOT statistical confidence','rows':rows,'limits':['Source frames not restored locally; identities and annotations not independently re-read in this run','F/G different timestamps/edit timelines, same rigid world state NOT proved','Cameras already trained on same eleven hypotheses, all data in-sample','Computed points are diagnostics only, never applied to scene, not measured geometry','No visibility, occlusion or material/shape acceptance; former G tree occlusion remains','Depth/units arbitrary; no physical metric inference']};(OUT/'fixed-pose-correspondence-check.json').write_text(json.dumps(out,indent=2))
print([(x['id'],round(x['ray_parallax_deg'],2),round(x['closest_ray_gap_working_units'],3),round(x['conditional_world_point_not_applied'][2],3)) for x in rows]);print('mean errors',[[float(np.mean([x['errors'][k][field] for x in rows])) for field in ['original_error_px','conditional_fit_error_px']] for k in [0,1]])
