import json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
p=Path('classroom_motion_validation_20261010');a=json.load(open(p/'qa/B_camera_identity_exploration.json'))['front16_two_wall_fit'];X1=np.array(a['world_points']);Y1=np.array(a['source_points']);ks=np.repeat([6,5,4,3,2],2);zs=np.tile([1.827585,.65312],5);Y2=np.array([[55,113],[58,557],[350,136],[345,546],[590,158],[586,537],[806,178],[800,526],[982,196],[970,520]],float);Y2[:,1]-=47
T1=np.array([[391,664],[273,629]],float)-[0,47];T2=np.array([[1065,660],[933,611]],float)-[0,47]
def proj(X,v):
 q=(X-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix();return np.stack([590+v[6]*q[:,0]/-q[:,2],332-v[6]*q[:,1]/-q[:,2]],1)
def res(v):
 pitch=v[14];X=X1.copy();X[-1,1]=.791384+pitch;Z=np.stack([np.full(10,4.050608),.791384+ks*pitch,zs],1);Q=np.array([[v[15],v[16],v[19]],[v[17],v[18],v[19]]]);return np.r_[(proj(X,v[:7])-Y1).ravel(),(proj(Z,v[7:14])-Y2).ravel(),(proj(Q,v[:7])-T1).ravel(),(proj(Q,v[7:14])-T2).ravel()]
c=next(x for x in json.load(open(p/'qa/B_joint_pitch_fit.json'))['shared_focal_sensitivity_not_assumed_truth'] if x['shared_lens_mm']==28);v0=np.r_[c['front16_camera'],c['intro14_camera'],c['pitch'],[2.5,3.15,2.85,3.3,.7]];lo=[-3,0,.5,1,-.3,-3,400]*2+[.45,1,1,1,1,.4];hi=[3.9,10,2,2,.3,0,2300]*2+[.95,4,6,4,6,1.1];f=least_squares(res,v0,bounds=(lo,hi),max_nfev=8000);v=f.x;e=res(v);out={'status':'EXPLORATORY_SHARED_STATIC_DESK_LINK','front_pitch':v[14],'pier_y':.791384+6*v[14],'front16_camera':v[:7].tolist(),'front19_camera':v[7:14].tolist(),'shared_T1_cup_base':[v[15],v[16],v[19]],'shared_T1_case_base':[v[17],v[18],v[19]],'rms_front16_arch':float(np.sqrt(np.mean(e[:14]**2)*2)),'rms_front19_arch':float(np.sqrt(np.mean(e[14:34]**2)*2)),'rms_shared_desk_points':float(np.sqrt(np.mean(e[34:]**2)*2)),'residuals':e.tolist(),'source_T1_points':[T1.tolist(),T2.tolist()],'caveat':'Manual blurred frame/jamb picks 3-8px, cup/case base5-10px. Both points assumed at common tabletop height. Model building dimensions otherwise fixed. This is calibration hypothesis, not accepted furniture/model.'};(p/'qa/B_linked_bundle.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
# Test a pure-pan camera segment with one centre and one focal. This is a hypothesis, not video metadata.
def expand(z):return np.r_[z[:3],z[3:6],z[9],z[:3],z[6:9],z[9],z[10:]]
z0=np.r_[(v[:3]+v[7:10])/2,v[3:6],v[10:13],(v[6]+v[13])/2,v[14:]];z0[-1]=.695485
low=[-3,0,.5,1,-.3,-3,1,-.3,-3,400,.45,1,1,1,1,.4];high=[3.9,10,2,2,.3,0,2,.3,0,2300,.95,4,6,4,6,1.1]
f=least_squares(lambda z:res(expand(z)),z0,bounds=(low,high),max_nfev=7000);vv=expand(f.x);rr=res(vv);out['shared_center_focal_pan_hypothesis']={'front16_camera':vv[:7].tolist(),'front19_camera':vv[7:14].tolist(),'pitch':vv[14],'desk_points':[[vv[15],vv[16],vv[19]],[vv[17],vv[18],vv[19]]],'rms_front16':float(np.sqrt(np.mean(rr[:14]**2)*2)),'rms_front19':float(np.sqrt(np.mean(rr[14:34]**2)*2)),'rms_shared_points':float(np.sqrt(np.mean(rr[34:]**2)*2)),'caveat':'A pure pan has no translational triangulation baseline: shared table depth/height not identifiable. Do not interpret fitted height as measured.'};out['status']='EXPLORATORY_UNDERCONSTRAINED_STATIC_DESK_LINK';out['bound_warning']='Independent fit drives common table height to lower0.4 bound: do not accept its desk geometry.';(p/'qa/B_linked_bundle.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['shared_center_focal_pan_hypothesis'],indent=2))
# A height imported from a different time is only an explicit cross-shot hypothesis.
profiles=[]
for h in [.60,.664,.70,.75,.80]:
 z0=v[:19].copy()
 fit=least_squares(lambda z:res(np.r_[z,h]),z0,bounds=(lo[:19],hi[:19]),max_nfev=5000);vv=np.r_[fit.x,h];rr=res(vv);profiles.append({'assumed_height':h,'pitch':vv[14],'front16_camera':vv[:7].tolist(),'front19_camera':vv[7:14].tolist(),'T1_cup_base':[vv[15],vv[16],h],'T1_case_base':[vv[17],vv[18],h],'rms_front16_arch':float(np.sqrt(np.mean(rr[:14]**2)*2)),'rms_front19_arch':float(np.sqrt(np.mean(rr[14:34]**2)*2)),'rms_static':float(np.sqrt(np.mean(rr[34:]**2)*2))})
out['fixed_height_hypothesis_profile']=profiles;(p/'qa/B_linked_bundle.json').write_text(json.dumps(out,indent=2));print([(r['assumed_height'],r['pitch'],r['rms_static']) for r in profiles])
