import json,hashlib,math,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path('/workspace/shared/desert-camp-build-20261031/scenes/desert-tent-camp');OUT=Path(__file__).resolve().parent
frozen=json.load(open(ROOT/'qa/heldout_r03/frozen_geometry_anchors.json'));actual=json.load(open(ROOT/'qa/R07_actual_model_anchor_check.json'));old=json.load(open(ROOT/'qa/heldout_r03/fixed_model_camera_cases.json'));P={k:np.array(v) for k,v in frozen['actual_model_points'].items()};P.update({a['id']:np.array(a['xyz']) for a in actual['anchors']});names=['F1','F2','apex'];X=np.array([P[n] for n in names]);UV=np.array([[186,700],[283,697],[143,193]],float);sig=np.array([6,6,8]);held={'B1':np.array([85,551]),'B2':np.array([140,549])}
def basis(p):
 y,t,r=p[3:];fw=np.array([np.sin(y)*np.cos(t),np.cos(y)*np.cos(t),np.sin(t)]);rt=np.array([np.cos(y),-np.sin(y),0]);up=np.cross(rt,fw);R=np.array([np.cos(r)*rt+np.sin(r)*up,-(-np.sin(r)*rt+np.cos(r)*up),fw]);return R

def project(A,p,f):
 q=(A-p[:3])@basis(p).T;d=q[:,2];den=np.where(abs(d)<1e-5,np.sign(d+1e-20)*1e-5,d);return q[:,:2]/den[:,None]*f+[960,540],d

def seed(q):
 c=np.array(q[:3]);d=np.array([q[3],2,q[4]])-c;d/=np.linalg.norm(d);return np.r_[c,np.arctan2(d[0],d[1]),np.arcsin(d[2]),0]
lo=np.array([-100,-120,.49,-np.pi,-1.45,-np.deg2rad(5)]);hi=np.array([100,100,80,np.pi,1.45,np.deg2rad(5)])
rng=np.random.default_rng(310);results=[];started=time.monotonic()
for case in old['cases']:
 f=case['fixed_focal_px'];p0=seed(case['camera_params']);starts=[p0]
 for r in [-4,-2,2,4]:p=p0.copy();p[5]=np.deg2rad(r);starts.append(p)
 for i in range(45):
  p=p0.copy();p[:3]+=rng.normal(size=3)*[13,15,7];p[3:5]+=rng.normal(size=2)*[.4,.22];p[5]=rng.uniform(lo[5],hi[5]);starts.append(np.clip(p,lo+1e-6,hi-1e-6))
 # Opposite/front flank starts are retained; fit only sees the same three points.
 for x,y,z in [(-25,-10,8),(25,-10,8),(-20,25,12),(20,25,12),(0,-55,20),(0,30,20)]:
  d=X.mean(axis=0)-[x,y,z];d=d/np.linalg.norm(d);starts.append(np.array([x,y,z,np.arctan2(d[0],d[1]),np.arcsin(d[2]),0]))
 runs=[];branches=[]
 for i,p in enumerate(starts):
  def fun(v):return ((project(X,v,f)[0]-UV)/sig[:,None]).ravel()
  res=least_squares(fun,p,bounds=(lo,hi),max_nfev=1200,xtol=1e-11,ftol=1e-11,gtol=1e-11)
  pred,depth=project(X,res.x,f);sv=np.linalg.svd(res.jac,compute_uv=False);rr={'start':i,'cost':float(np.dot(res.fun,res.fun)),'params_xyz_yaw_pitch_roll':res.x.tolist(),'fit_residual_px':np.linalg.norm(pred-UV,axis=1).tolist(),'positive_depth':bool(np.all(depth>0)),'depths':depth.tolist(),'roll_degrees':float(np.rad2deg(res.x[5])),'roll_boundary_hit':bool(abs(abs(res.x[5])-hi[5])<1e-5),'other_parameter_boundary_hit':bool(np.any(np.minimum(res.x-lo,hi-res.x)[:5]<1e-4)),'source_front_face_visible':bool(res.x[1]<0),'source_left_face_visible':bool(res.x[0]<0),'rank':int(np.sum(sv>sv[0]*1e-8)),'singular_values':sv.tolist(),'jacobian_condition':float(sv[0]/max(sv[-1],1e-30)),'nfev':res.nfev,'solver_success':bool(res.success)}
  runs.append(rr)
  # Cluster by pose only, never heldout performance.
  existing=next((b for b in branches if np.linalg.norm(np.array(b['params_xyz_yaw_pitch_roll'])[:3]-res.x[:3])<.02 and np.linalg.norm(np.array(b['params_xyz_yaw_pitch_roll'])[3:]-res.x[3:])<.001),None)
  if existing:existing['start_ids'].append(i)
  else:bb=dict(rr);bb['start_ids']=[i];branches.append(bb)
 for b in branches:
  p=np.array(b['params_xyz_yaw_pitch_roll']);b['world_to_cv_rotation']=basis(p).tolist();b['camera_world_location']=p[:3].tolist();b['blender_camera_world_rotation_columns']=np.stack([basis(p)[0],-basis(p)[1],-basis(p)[2]],axis=1).tolist();b['heldout_checks']=[]
  for n,uv in held.items():pred,dep=project(P[n][None],p,f);b['heldout_checks'].append({'id':n,'observed':uv.tolist(),'projected':pred[0].tolist(),'depth':float(dep[0]),'residual_px':float(np.linalg.norm(pred[0]-uv)),'used_for_selection':False})
 results.append({'focal_px':f,'starts':len(starts),'runs':runs,'branches':branches});print('DONE',f,'branches',len(branches),flush=True)
out={'status':'post-failure camera-condition recheck, not fresh blinded validation; fixed R07 geometry/source1/source2 cameras unchanged','fit_points':names,'uncertainties_px':sig.tolist(),'fit_count':6,'unknown_count':6,'fixed_principal_point':[960,540],'fixed_focal_profiles':[1800,2500,3200],'roll_window_degrees':[-5,5],'roll_window_is_measured':False,'vertical_segment_added_to_fit':False,'parameterization':'camera world xyz and yaw/pitch/roll radians; forward=(sin yaw cos pitch, cos yaw cos pitch,sin pitch), roll rotates image right toward up; returned explicit CV world-to-camera R','solver_bounds':{'lower':lo.tolist(),'upper':hi.tolist(),'note':'broad search limits, not measured scene extents; boundary hits retained and flagged; positive depth/known visible box-face checks separately labelled'},'selection':'No heldout selection; cluster by camera pose only; all starts and all branches retained. Physical-view flags do not prove correctness.','rank_note':'Jacobian columns position in arbitrary working units and angles in radians, residuals weighted by6/6/8px; condition number depends on this scaling. Numerical full local rank does not remove P3P ambiguity or soft-apex uncertainty.','runtime_seconds':time.monotonic()-started,'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'qa/R07_actual_model_anchor_check.json',ROOT/'qa/heldout_r03/frozen_geometry_anchors.json',ROOT/'qa/heldout_r03/fixed_model_camera_cases.json']},'profiles':results}
(OUT/'audit_all_branches.json').write_text(json.dumps(out,indent=2));summary=[]
for pr in results:
 physical=[b for b in pr['branches'] if b['positive_depth'] and b['source_front_face_visible'] and b['source_left_face_visible']]
 summary.append({'focal':pr['focal_px'],'all_branches':len(pr['branches']),'physical_front_left_branches':[{'pose':b['params_xyz_yaw_pitch_roll'],'fit_residual_px':b['fit_residual_px'],'roll_deg':b['roll_degrees'],'roll_boundary':b['roll_boundary_hit'],'rank':b['rank'],'condition':b['jacobian_condition'],'heldout_px':[q['residual_px'] for q in b['heldout_checks']],'starts':b['start_ids']} for b in physical]})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
