import json,hashlib,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path('/workspace/scratch/fa58bfcf0425');OUT=Path(__file__).resolve().parent;pointfile=ROOT/'camp-remake-20261102/qa/C02_actual_points.json';source=ROOT/'recovered-source-candidates/camp/BV169Y96rEo1_P1_1566.095177.png';P={k:np.array(v,float) for k,v in json.load(open(pointfile)).items()};names=['F1','F2','apex'];X=np.array([P[n] for n in names]);UV=np.array([[186.,700.],[283.,697.],[143.,193.]]);sig=np.array([6.,6.,8.]);held={'B1':np.array([85.,551.]),'B2':np.array([140.,549.])}
assert hashlib.sha256(source.read_bytes()).hexdigest()=='947229e1fc963f73b47468f371083fe876f0dcf6458b43f0623fbb7b59c2fc7b'
def basis(p):
 y,t,r=p[3:];fw=np.array([np.sin(y)*np.cos(t),np.cos(y)*np.cos(t),np.sin(t)]);rt=np.array([np.cos(y),-np.sin(y),0]);up=np.cross(rt,fw);return np.array([np.cos(r)*rt+np.sin(r)*up,-(-np.sin(r)*rt+np.cos(r)*up),fw])
def project(A,p,f):
 q=(A-p[:3])@basis(p).T;d=q[:,2];den=np.where(abs(d)<1e-5,np.sign(d+1e-20)*1e-5,d);return q[:,:2]/den[:,None]*f+[960,540],d
lo=np.array([-100,-120,.49,-np.pi,-1.45,-np.deg2rad(5)]);hi=np.array([100,100,80,np.pi,1.45,np.deg2rad(5)])
rng=np.random.default_rng(310);results=[];started=time.monotonic()
for f in [1800,2500,3200]:
 # Fresh declared numerical start, not a recovered old camera solution.
 c=np.array([-3.,-f/100.,4.]);d=np.array([8.,2.,1.5])-c;d/=np.linalg.norm(d);p0=np.r_[c,np.arctan2(d[0],d[1]),np.arcsin(d[2]),0.];starts=[p0]
 for roll in [-4,-2,2,4]:p=p0.copy();p[5]=np.deg2rad(roll);starts.append(p)
 for i in range(45):
  p=p0.copy();p[:3]+=rng.normal(size=3)*[13,15,7];p[3:5]+=rng.normal(size=2)*[.4,.22];p[5]=rng.uniform(lo[5],hi[5]);starts.append(np.clip(p,lo+1e-6,hi-1e-6))
 for x,y,z in [(-25,-10,8),(25,-10,8),(-20,25,12),(20,25,12),(0,-55,20),(0,30,20)]:
  d=X.mean(axis=0)-[x,y,z];d=d/np.linalg.norm(d);starts.append(np.array([x,y,z,np.arctan2(d[0],d[1]),np.arcsin(d[2]),0]))
 runs=[];branches=[]
 for i,p in enumerate(starts):
  def fun(v):return ((project(X,v,f)[0]-UV)/sig[:,None]).ravel()
  res=least_squares(fun,p,bounds=(lo,hi),max_nfev=1200,xtol=1e-11,ftol=1e-11,gtol=1e-11);pred,depth=project(X,res.x,f);sv=np.linalg.svd(res.jac,compute_uv=False)
  rr={'start':i,'initial_pose':p.tolist(),'cost':float(np.dot(res.fun,res.fun)),'params_xyz_yaw_pitch_roll':res.x.tolist(),'fit_residual_px':np.linalg.norm(pred-UV,axis=1).tolist(),'positive_fit_depth':bool(np.all(depth>0)),'fit_depths':depth.tolist(),'roll_degrees':float(np.rad2deg(res.x[5])),'roll_boundary_hit':bool(abs(abs(res.x[5])-hi[5])<1e-5),'other_parameter_boundary_hit':bool(np.any(np.minimum(res.x-lo,hi-res.x)[:5]<1e-4)),'source_front_face_visible':bool(res.x[1]<0),'source_left_face_visible':bool(res.x[0]<0),'rank':int(np.sum(sv>sv[0]*1e-8)),'singular_values':sv.tolist(),'jacobian_condition':float(sv[0]/max(sv[-1],1e-30)),'nfev':res.nfev,'solver_success':bool(res.success)};runs.append(rr)
  existing=next((b for b in branches if np.linalg.norm(np.array(b['params_xyz_yaw_pitch_roll'])[:3]-res.x[:3])<.02 and np.linalg.norm(np.array(b['params_xyz_yaw_pitch_roll'])[3:]-res.x[3:])<.001),None)
  if existing:existing['start_ids'].append(i)
  else:bb=dict(rr);bb['start_ids']=[i];branches.append(bb)
 for k,b in enumerate(branches):
  p=np.array(b['params_xyz_yaw_pitch_roll']);R=basis(p);b['branch_index']=k;b['world_to_cv_rotation']=R.tolist();M=np.eye(4);M[:3,:3]=np.stack([R[0],-R[1],-R[2]],axis=1);M[:3,3]=p[:3];b['blender_matrix_world']=M.tolist();b['heldout_checks']=[]
  for n,uv in held.items():pr,dep=project(P[n][None],p,f);b['heldout_checks'].append({'id':n,'observed':uv.tolist(),'projected':pr[0].tolist(),'depth':float(dep[0]),'residual_px':float(np.linalg.norm(pr[0]-uv)),'within_6px_manual_tolerance':bool(np.linalg.norm(pr[0]-uv)<=6),'used_for_selection':False})
 results.append({'focal_px':f,'starts':len(starts),'runs':runs,'branches':branches})
out={'stage':'2026-11-02 NEW computation from C02 remake, not original Oct31 data recovery','inputs':{'actual_point_file':str(pointfile),'actual_points_sha256':hashlib.sha256(pointfile.read_bytes()).hexdigest(),'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'fixed_geometry_points':{k:v.tolist() for k,v in P.items()},'protocol':{'fit_names':names,'fit_pixels':UV.tolist(),'fit_uncertainty_px':sig.tolist(),'heldout':['B1','B2','chair remains unused'],'fixed_focal_profiles':[1800,2500,3200],'principal_point':[960,540],'unknowns':'xyz+yaw+pitch+roll =6','roll_diagnostic_window_degrees':[-5,5],'roll_window_is_measured':False,'lower_search_bounds':lo.tolist(),'upper_search_bounds':hi.tolist(),'bounds_are_scene_evidence':False,'per_profile_starts':56,'selection':'pose clustering only; no heldout-driven selection or focal search','vertical_segment_used':False,'third_seen_before':True,'fresh_blind_validation':False,'later_independent_replay':False,'scope':'source1/source2 cameras and shared model not modified','rank_scaling':'weighted pixel residuals, positions arbitrary working units, angles radians; rank6 does not establish global uniqueness or eliminate soft-apex ambiguity'},'runtime_seconds':time.monotonic()-started,'profiles':results};(OUT/'all_branches.json').write_text(json.dumps(out,indent=2))
compact=[]
for pr in results:
 for b in pr['branches']:
  if not (b['positive_fit_depth'] and b['source_front_face_visible'] and b['source_left_face_visible']):continue
  compact.append({'focal_px':pr['focal_px'],'branch_index':b['branch_index'],'matrix_world':b['blender_matrix_world'],'lens_mm':pr['focal_px']*36/1920,'sensor_width_mm':36,'sensor_fit':'HORIZONTAL','image_size':[1920,1080],'roll_degrees':b['roll_degrees'],'fit_residual_px':b['fit_residual_px'],'heldout_checks':b['heldout_checks'],'rank':b['rank'],'condition':b['jacobian_condition'],'roll_boundary_hit':b['roll_boundary_hit'],'selected_using_heldout':False})
(OUT/'cameras_for_render.json').write_text(json.dumps({'status':'all found positive-depth/front-left candidates under current box-axis assumption, no heldout selection; see full branch log','cameras':compact},indent=2));print(json.dumps(compact,indent=2))
