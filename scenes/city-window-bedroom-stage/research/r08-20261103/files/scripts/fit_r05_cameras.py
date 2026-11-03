import json,numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
D=Path(__file__).resolve().parents[1]
params=json.load(open(D/'qa/R04-camera-parameters.json'))
# Human marked approximate visible landmarks, uncertainty +/- 10 native pixels.
landmarks={'SOURCE_A':[
 ('stool_base',[0,1.25,.007],[990,804]),('stool_rim',[0,1.25,.91],[995,657]),
 ('window_mullion_bottom',[1.4,5.06,.24],[1140,729]),('bar_left_upper_front',[2.2,2.25,1.55],[1294,590]),
 ('wood_stool1_seat',[3,1.76,1.12],[1442,665]),('wood_stool2_seat',[4.45,1.76,1.12],[1661,667]),
 ('lamp_shade_bottom',[-5.45,2.8,2.5],[151,437])],
'SOURCE_B':[
 ('stool_base',[0,1.25,.007],[984,1061]),('stool_rim',[0,1.25,.91],[986,777]),
 ('window_mullion_bottom',[1.4,5.06,.24],[1150,868]),('bar_left_upper_front',[2.2,2.25,1.55],[1500,638]),
 ('curtain_left_tie',[-2.35,4.68,2.658],[500,484])],
'SOURCE_C':[
 ('window_mullion_bottom',[1.4,5.06,.24],[1140,581]),('bar_left_upper_front',[2.2,2.25,1.55],[1390,565]),
 ('wood_stool1_seat',[3,1.76,1.12],[1520,656]),('wood_stool2_seat',[4.45,1.76,1.12],[1760,642]),
 ('curtain_left_tie',[-2.35,4.68,2.658],[488,320])]}
results=[]
for cam in params:
 name=cam['name']; anchors=landmarks[name];xyz=np.array([x[1] for x in anchors]);uv=np.array([x[2] for x in anchors]);R=np.array(cam['rotation_matrix']);rv=Rotation.from_matrix(R).as_rotvec();initial=np.r_[cam['location'],rv];f=cam['focal_px']
 def project(p):
  R=Rotation.from_rotvec(p[3:]).as_matrix();c=(xyz-p[:3])@R;z=-c[:,2];return np.column_stack([960+f*c[:,0]/z,540-f*c[:,1]/z])
 def resid(p):return (project(p)-uv).ravel()
 # Fixed focal length, bounded camera-only solve. This is conditional, not an identified metric calibration.
 lower=initial-np.array([2,2,1.5,.45,.45,.45]);upper=initial+np.array([2,2,1.5,.45,.45,.45]);lower[2]=max(.25,lower[2]);upper[2]=min(6.5,upper[2])
 fit=least_squares(resid,initial,bounds=(lower,upper),loss='soft_l1',f_scale=12,max_nfev=400)
 before=np.linalg.norm(project(initial)-uv,axis=1);after=np.linalg.norm(project(fit.x)-uv,axis=1)
 results.append({'camera':name,'fixed_focal_px':f,'initial':initial.tolist(),'fitted':fit.x.tolist(),'rotation_matrix':Rotation.from_rotvec(fit.x[3:]).as_matrix().tolist(),
 'before_mean_px':float(before.mean()),'after_mean_px':float(after.mean()),'after_max_px':float(after.max()),'bound_hit':bool(np.any(np.minimum(fit.x-lower,upper-fit.x)<1e-4)),
 'anchors':[{'id':a[0],'world_hypothesis':a[1],'manual_source_pixel':a[2],'before_error_px':float(b),'after_error_px':float(c),'fitted_projection':p.tolist()} for a,b,c,p in zip(anchors,before,after,project(fit.x))],
 'status':'Training-only conditional camera fit; manually marked anchors on hypothesized geometry, +/-10px input uncertainty. Not withheld validation or source acceptance.'})
(D/'qa/R05-camera-fit.json').write_text(json.dumps(results,indent=2));print([(x['camera'],x['before_mean_px'],x['after_mean_px'],x['after_max_px'],x['bound_hit']) for x in results])
