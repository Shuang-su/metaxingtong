"""Conditional fixed-geometry camera fit. All seen-source annotations retained, no blind test claim."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
D=Path(__file__).resolve().parents[1]
ann=json.load(open(D/'sources/landmarks-v1/landmarks-v1.json'));cams=json.load(open(D/'qa/R09-baseline-camera-parameters.json'))['cameras'];results=[]
theta=np.arange(512)*2*np.pi/512
circles={k:np.c_[r*np.cos(theta),1.25+r*np.sin(theta),np.full(512,z)] for k,r,z in [('seat',.315,.903),('base',.301,0),('waist',.098,.455)]}
def pose(loc,target):
 f=np.array(target)-loc;f=f/np.linalg.norm(f);r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f);return np.r_[loc,Rotation.from_matrix(np.column_stack([r,u,-f])).as_rotvec()]
def dist_curve(uv,poly):
 a=poly;b=np.roll(a,-1,axis=0);ab=b-a;t=np.clip(((uv-a)*ab).sum(1)/(ab*ab).sum(1),0,1);near=a+t[:,None]*ab;idx=np.argmin(((near-uv)**2).sum(1));return float(np.linalg.norm(near[idx]-uv)),near[idx]
for key,name in [('D','SOURCE_D_low'),('E','SOURCE_E_oblique'),('F','SOURCE_F_fan4k')]:
 frame=ann['frames'][key];cam=next(c for c in cams if c['name']==name);lm={l['name']:l for l in frame['landmarks']};initial=np.r_[cam['location'],Rotation.from_matrix(cam['rotation_matrix']).as_rotvec()];w,h=frame['native_dimensions'];f=cam['focal_px']
 def project(p,pts):
  q=(np.asarray(pts)-p[:3])@Rotation.from_rotvec(p[3:]).as_matrix();z=-q[:,2];return np.c_[w/2+f*q[:,0]/np.maximum(z,.01),h/2-f*q[:,1]/np.maximum(z,.01)]
 training=[]
 for n in ['seat_left','seat_right','seat_rear','seat_front','base_left','base_right','base_front']:
  if n in lm:training.append({'id':lm[n]['id'],'kind':'curve','curve':n.split('_')[0],'xy':lm[n]['xy_native'],'sigma_px':lm[n]['uncertainty_radius_px'],'original_names':[n]})
 # E/F use paired-edge middle line only; width is reserved as a geometry diagnostic.
 if key=='D':
  for n in ['mullion_right_a','mullion_right_b','mullion_right_c']:
   a=lm[n];training.append({'id':a['id'],'kind':'line','x_world':1.455,'xy':a['xy_native'],'sigma_px':a['uncertainty_radius_px'],'original_names':[n]})
 else:
  for suffix in ['a','b']:
   a,b=lm['mullion_left_'+suffix],lm['mullion_right_'+suffix];training.append({'id':a['id']+'+'+b['id'],'kind':'line','x_world':1.4,'xy':((np.array(a['xy_native'])+b['xy_native'])/2).tolist(),'sigma_px':max(a['uncertainty_radius_px'],b['uncertainty_radius_px']),'original_names':[a['name'],b['name']]})
 def residual_detail(p,entry):
  uv=np.array(entry['xy']);
  if entry['kind']=='curve':return dist_curve(uv,project(p,circles[entry['curve']]))
  a,b=project(p,[[entry['x_world'],4.98,.18],[entry['x_world'],4.98,6.438]]);v=b-a;v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]]);signed=float((uv-a)@normal);return signed,uv-signed*normal
 def residual(p):return np.array([residual_detail(p,e)[0]/e['sigma_px'] for e in training])
 lower=np.r_[[-6.3,-6.8,.2],initial[3:]-1.2];upper=np.r_[[6.3,0,5],initial[3:]+1.2]
 starts=[initial,pose(np.array([3.,-4.,1.5]),[0,2,1.5]),pose(np.array([-3.,-4.,1.5]),[0,2,1.5])];runs=[]
 for start in starts:
  start=np.clip(start,lower+1e-6,upper-1e-6);fit=least_squares(residual,start,bounds=(lower,upper),loss='soft_l1',f_scale=1,max_nfev=1500,xtol=1e-11,ftol=1e-11,gtol=1e-11,x_scale=[3,3,2,.5,.5,.5]);sv=np.linalg.svd(fit.jac@np.diag([3,3,2,.5,.5,.5]),compute_uv=False)
  runs.append({'start':start.tolist(),'solution':fit.x.tolist(),'cost':float(fit.cost),'success':bool(fit.success),'nfev':int(fit.nfev),'bound_hit':bool(np.any(np.minimum(fit.x-lower,upper-fit.x)<1e-4)),'normalized_jacobian_singular_values':sv.tolist(),'rank_relative_1e_6':int(np.sum(sv>sv[0]*1e-6)),'condition_number':float(sv[0]/sv[-1]) if sv[-1]>0 else None})
 best=min(runs,key=lambda x:x['cost']);p=np.array(best['solution']);rows=[]
 for e in training:
  a,pa=residual_detail(initial,e);b,pb=residual_detail(p,e);rows.append(dict(e,before_error_px=abs(a),after_error_px=abs(b),before_nearest_projection=pa.tolist(),after_nearest_projection=pb.tolist()))
 diagnostics=[]
 # All untrained annotations remain in the record. Undefined 2D-to-3D correspondences are not assigned fabricated errors.
 used={n for e in training for n in e['original_names']}
 for a in frame['landmarks']:
  n=a['name'];rec=dict(a)
  if n in used:rec['use']='training input (or paired-line component)'
  elif n in ['waist_left','waist_right']:
   rec['use']='not-fitted curve diagnostic; waist-circle approximation, silhouette height view-dependent';rec['before_error_px']=dist_curve(np.array(a['xy_native']),project(initial,circles['waist']))[0];rec['after_error_px']=dist_curve(np.array(a['xy_native']),project(p,circles['waist']))[0]
  else:rec['use']='retained visual diagnostic, no justified fixed 3D correspondence; no fabricated scalar error'
  if 'mullion_left_' in n or 'mullion_right_' in n:
   x=1.345 if 'left' in n else 1.455;e={'kind':'line','x_world':x,'xy':a['xy_native']};rec['edge_diagnostic_before_px']=abs(residual_detail(initial,e)[0]);rec['edge_diagnostic_after_px']=abs(residual_detail(p,e)[0]);rec['edge_diagnostic_note']='Full original edge checked separately even when only middle line trained.'
  diagnostics.append(rec)
 results.append({'camera':name,'frame_key':key,'source_file':frame['source_file'],'source_sha256':frame['source_sha256'],'source_time_seconds':{'D':1214.175651,'E':1356.934381,'F':55.048960}[key],'width':w,'height':h,'fixed_lens_mm':cam['lens_mm'],'fixed_focal_px':f,'initial':initial.tolist(),'fitted':p.tolist(),'rotation_matrix':Rotation.from_rotvec(p[3:]).as_matrix().tolist(),'bounds':{'lower':lower.tolist(),'upper':upper.tolist()},'runs':runs,'selected_run':runs.index(best),'training':rows,'all_first_annotations':diagnostics,'not_marked':frame['not_marked'],'before_mean_px':float(np.mean([r['before_error_px'] for r in rows])),'after_mean_px':float(np.mean([r['after_error_px'] for r in rows])),'after_max_px':float(max(r['after_error_px'] for r in rows)),'limits':'Conditional fixed-R08-geometry camera solve. All points seen/manual; no blind validation. Circles are exact named R08 rings, not proof the visible source edge has same physical profile. Line center derived only from visible paired edges. Sigma subjective, not statistical. Multi-start solutions and invalid/ambiguous points retained.'})
out={'method_version':'r09-circle-line-pose-v1','scales_for_jacobian':'Residual / manual pixel uncertainty; parameter increments scaled by [3,3,2,.5,.5,.5] working units/radians. Condition number is local under these chosen scales.','solver':'scipy least_squares soft_l1 f_scale=1, fixed focal/shift, three documented starts; no geometry change','circle_hypotheses':{'seat':{'r':.315,'z':.903},'base':{'r':.301,'z':0},'waist_diagnostic':{'r':.098,'z':.455}},'results':results}
(D/'qa/R09-camera-fit.json').write_text(json.dumps(out,indent=2));print([(r['camera'],r['before_mean_px'],r['after_mean_px'],r['after_max_px'],r['fitted'][:3],r['runs'][r['selected_run']]['condition_number']) for r in results])
