import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pathlib import Path
p=Path('classroom_motion_validation_20261010');j=json.load(open(p/'qa/B_camera_identity_exploration.json'));c=j['six_bay_B_window_only_free_lens'];v0=np.r_[c['location'],c['rotation'],c['lens_mm']/36*1180]
X=[];Y=[]
for k,upper,lower in [(6,[228,110],[232,545]),(5,[480,128],[474,542]),(4,[712,143],[706,540]),(3,[928,159],[920,534]),(2,[1119,173],[1112,530])]:
 for z,uv in [(1.827585,upper),(.65312,lower)]:X.append([4.050608,.791384+k*.5816229295,z]);Y.append([uv[0],uv[1]-47])
X=np.array(X);Y=np.array(Y)
def proj(v):
 q=(X-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix();return np.stack([590+v[6]*q[:,0]/-q[:,2],332-v[6]*q[:,1]/-q[:,2]],1)
v0=np.array([1.31,4.3,1.18,1.57,0,-1.7,30/36*1180]);fit=least_squares(lambda v:(proj(v)-Y).ravel(),v0,bounds=([-3,0,.5,1,-.3,-3,300],[3.9,10,2,2,.3,0,2500]),max_nfev=5000);v=fit.x;R=Rotation.from_euler('xyz',v[3:6]).as_matrix();out={'camera':{'location':v[:3].tolist(),'rotation':v[3:6].tolist(),'lens_mm':float(v[6]*36/1180)},'fit_rms_px':float(np.sqrt(np.mean(np.sum((proj(v)-Y)**2,axis=1)))),'world_anchors':X.tolist(),'source_anchors':Y.tolist(),'desks':{}}
for n,pts in {'T1':[[906,609],[1090,599],[1179,649]],'T2':[[349,637],[575,615],[628,710],[341,710]]}.items():
 out['desks'][n]=[]
 for u,w in pts:
  ray=R@np.array([(u-590)/v[6],-(w-47-332)/v[6],-1]);pt=v[:3]+(.695485-v[2])/ray[2]*ray;out['desks'][n].append({'raw_px':[u,w],'world_at_model_height':pt.tolist()})
out['caveat']='Blurred screenshot. Last two T2 coordinates are frame intersections, not desk corners. Window-only fit has focal-distance ambiguity; metric furniture locations are conditional, no model object has moved.';(p/'qa/B_intro14_three_desk_constraints.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
