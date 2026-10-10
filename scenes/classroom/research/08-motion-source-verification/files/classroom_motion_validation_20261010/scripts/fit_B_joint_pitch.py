import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pathlib import Path
p=Path('classroom_motion_validation_20261010');j=json.load(open(p/'qa/B_camera_identity_exploration.json'));a=j['front16_two_wall_fit'];b=json.load(open(p/'qa/B_intro14_three_desk_constraints.json'));X1=np.array(a['world_points']);Y1=np.array(a['source_points']);Y2=np.array(b['source_anchors']);ks=np.repeat([6,5,4,3,2],2);zs=np.tile([1.827585,.65312],5)
def proj(X,v):
 q=(X-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix();return np.stack([590+v[6]*q[:,0]/-q[:,2],332-v[6]*q[:,1]/-q[:,2]],1)
def pts(pitch):
 X=X1.copy();X[-1,1]=.791384+pitch;Z=np.stack([np.full(10,4.050608),.791384+ks*pitch,zs],1);return X,Z
def residual(v):
 X,Z=pts(v[-1]);return np.r_[(proj(X,v[:7])-Y1).ravel(),(proj(Z,v[7:14])-Y2).ravel()]
v0=np.r_[a['location'],a['rotation'],a['lens_mm']/36*1180,[1.31,4.3,1.18,1.57,0,-1.7,30/36*1180],.7]
lo=[-3,0,.5,1,-.3,-3,300]*2+[.4];hi=[3.9,10,2,2,.3,0,2500]*2+[1.2];f=least_squares(residual,v0,bounds=(lo,hi),max_nfev=6000);v=f.x;err=residual(v);out={'pitch':v[-1],'front_pier_y':.791384+6*v[-1],'front16_camera':v[:7].tolist(),'intro14_camera':v[7:14].tolist(),'front16_rms':float(np.sqrt(np.mean(err[:14]**2)*2)),'intro14_rms':float(np.sqrt(np.mean(err[14:]**2)*2)),'parameter_units':'camera[x,y,z,eulerx,y,z,focalpixels], pitch in inferred original model units','notes':'Joint two-wall + window-plane fit; two independent focal lengths. Existing wall/board/bookcase dimensions and window heights held. All source anchors manually picked; inferred pitch is conditional, no geometry edited.'};(p/'qa/B_joint_pitch_fit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
profiles=[]
for lens in [20,24,28,30,32,38.41616,45,55]:
 focal=lens/36*1180
 def expand(z):return np.r_[z[:6],focal,z[6:12],focal,z[-1]]
 z0=np.r_[v[:6],v[7:13],v[-1]];flo=[-3,0,.5,1,-.3,-3]*2+[.4];fhi=[3.9,10,2,2,.3,0]*2+[1.2];f=least_squares(lambda z:residual(expand(z)),z0,bounds=(flo,fhi),max_nfev=3000);vv=expand(f.x);rr=residual(vv);profiles.append({'shared_lens_mm':lens,'pitch':float(vv[-1]),'pier_y':float(.791384+6*vv[-1]),'front16_rms':float(np.sqrt(np.mean(rr[:14]**2)*2)),'intro14_rms':float(np.sqrt(np.mean(rr[14:]**2)*2)),'front16_camera':vv[:7].tolist(),'intro14_camera':vv[7:14].tolist()})
out['shared_focal_sensitivity_not_assumed_truth']=profiles;(p/'qa/B_joint_pitch_fit.json').write_text(json.dumps(out,indent=2));print([(r['shared_lens_mm'],r['pitch'],r['front16_rms'],r['intro14_rms']) for r in profiles])
