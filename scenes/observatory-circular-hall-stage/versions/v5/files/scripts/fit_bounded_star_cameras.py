import numpy as np,json,pathlib
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
P=pathlib.Path(__file__).resolve().parents[1];src=json.load(open(P/'source-diagnosis/landmarks-v1.json'));old=json.load(open(P/'qa/R06-star-fit.json'));out={}
a=-np.pi/4;Rz=Rotation.from_euler('z',a).as_matrix();scale=.8
for number,name in [(13,'SOURCE_13_high'),(21,'SOURCE_21_high')]:
 d=next(d for d in src['images'] if pathlib.Path(d['source']).stem==str(number));obs=np.array([next(x['xy'] for x in d['landmarks'] if x['id']=='S'+str(i+1)) for i in range(4)])
 world=np.array(old[name]['world']);world[:,:2]*=scale;world=world@Rz.T
 m=np.array(old[name]['matrix_world']);m[:3,:3]=Rz@m[:3,:3];m[:3,3]=Rz@((m[:3,3]-[0,0,.495])*scale+[0,0,.495]);rr=m[:3,:3].T;x0=np.r_[Rotation.from_matrix(rr).as_rotvec(),-rr@m[:3,3]];trials=[]
 for lens in [10,12,14,16,18,20,22,24,26,28,32]:
  def proj(x):
   q=world@Rotation.from_rotvec(x[:3]).as_matrix().T+x[3:];z=-q[:,2];return np.c_[596+lens/36*1192*q[:,0]/z,335.5-lens/36*1192*q[:,1]/z],z
  def fun(x):
   pp,z=proj(x);return np.r_[(pp-obs).ravel(),np.minimum(z-.05,0)*1000]
  fit=least_squares(fun,x0,max_nfev=1000);rr=Rotation.from_rotvec(fit.x[:3]).as_matrix();cam=np.eye(4);cam[:3,:3]=rr.T;cam[:3,3]=-rr.T@fit.x[3:];pp,z=proj(fit.x);err=np.linalg.norm(pp-obs,axis=1)
  trials.append({'lens':lens,'matrix_world':cam.tolist(),'errors_px':err.tolist(),'mean':float(err.mean()),'max':float(err.max()),'depth':z.tolist(),'radial':float(np.linalg.norm(cam[:2,3])),'height':float(cam[2,3]),'inside_conservative_box':bool(np.linalg.norm(cam[:2,3])<5.5 and .6<cam[2,3]<5.3)})
 eligible=[t for t in trials if t['inside_conservative_box'] and t['max']<8];chosen=min(eligible,key=lambda t:t['mean']) if eligible else None
 out[name]={'world':world.tolist(),'observed':obs.tolist(),'all_focal_trials':trials,'chosen_for_visibility_test':chosen,'limits':'No unique focal calibration. Camera bounds are model clearance hypotheses. Four point training only; all trials retained. Star radius2.4 matches conditional observed ring/star ratio approximately1.934 with inferred ring4.65. Orientation rotated-45 based image14 left/right tips relative to central doorway. Need actual occlusion and full-frame comparison.'}
 print(name,'chosen',None if not chosen else {k:chosen[k] for k in ['lens','mean','max','radial','height']})
(P/'qa/R06-bounded-fit.json').write_text(json.dumps(out,indent=2))
