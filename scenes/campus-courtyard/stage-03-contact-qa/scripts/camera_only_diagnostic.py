"""Frozen shared geometry, camera-only trial. Manual image picks with uncertainty.
These trials do NOT replace delivered cameras. No image warping or character anchors.
"""
import json,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[2];D=R/'stage-03-contact-qa';Q=D/'qa'
cams=json.loads((D/'camera_parameters.json').read_text())
markers={
 'doorLT':([20,4.925,2.6],[1353,286],7),
 'doorLB':([20,4.925,.4],[1353,486],6),
 'doorRT':([20,1.675,2.6],[1488,276],12),
 'doorRB':([20,1.675,.4],[1487,481],12),
}
data={
 'SRC02':{'fit':{**{k:markers[k] for k in ['doorLT','doorLB']},'tree_rim':([3.9,-5.34,.39],[741,710],25),'bench':([3.6,8.8,0],[166,542],20),'hoop_base':([17,-5.1,.07],[1508,590],15),'rack':([14.3,2.1,0],[1140,608],18)},'heldout':{k:markers[k] for k in ['doorRT','doorRB']}},
 'SRC04':{'fit':{'boardLT':([16.05,-6.065,8.055],[1243,58],5),'boardRT':([17.95,-6.065,8.055],[1385,75],5),'boardRB':([17.95,-6.065,6.805],[1381,205],7),'hoop_base':([17,-5.1,.07],[1190,507],15),'bench':([3.6,8.8,0],[250,450],20),'tree_rim':([3.9,-5.34,.39],[558,688],30)},'heldout':{'boardLB':([16.05,-6.065,6.805],[1241,198],5),'door_bottom':([20,3.3,.4],[1100,412],25)}}
}
def project(p,xyz):
 x,y,z,a,e,l=p;forward=np.array([math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)]);right=np.array([math.cos(a),-math.sin(a),0]);up=np.cross(right,forward);v=np.array(xyz)-[x,y,z];dep=v@forward;f=l*1920/36
 return np.c_[960+f*(v@right)/dep,540-f*(v@up)/dep]
results={}
for cid,sets in data.items():
 c=cams[cid];pos=np.array(c['location']);v=np.array(c['target'])-pos;p0=np.r_[pos,math.atan2(v[0],v[1]),math.atan2(v[2],np.linalg.norm(v[:2])),c['lens_mm']]
 vals=list(sets['fit'].values());xyz=np.array([p[0] for p in vals]);xy=np.array([p[1] for p in vals]);sigma=np.array([p[2] for p in vals])
 def residual(p):return ((project(p,xyz)-xy)/sigma[:,None]).ravel()
 fit=least_squares(residual,p0,bounds=([-50,-80,.6,.15,-.5,25],[10,-5,15,1.5,.3,150]),loss='soft_l1',f_scale=2,max_nfev=1500)
 p=fit.x;fwd=np.array([math.sin(p[3])*math.cos(p[4]),math.cos(p[3])*math.cos(p[4]),math.sin(p[4])]);rows=[]
 for group,points in sets.items():
  for name,(world,source,uncertainty) in points.items():
   before=project(p0,[world])[0];after=project(p,[world])[0];rows.append({'name':name,'role':group,'world':world,'source_xy':source,'source_uncertainty_px':uncertainty,'before_xy':before.tolist(),'trial_xy':after.tolist(),'before_error':float(np.linalg.norm(before-source)),'trial_error':float(np.linalg.norm(after-source))})
 results[cid]={'frozen_geometry':True,'adopted':False,'location':p[:3].tolist(),'target':(p[:3]+fwd*50).tolist(),'lens_mm':float(p[5]),'constraints':'approximate independent-review frame corners + existing approximate ground anchors; no character dimensions','limitations':'right door corners partially occluded; ground point identities approximate; heldout points weak; does not calibrate scene','points':rows}
(Q/'camera_only_trials.json').write_text(json.dumps(results,indent=2))
print(json.dumps({k:{'lens_mm':v['lens_mm'],'z':v['location'][2],'before_fit_mean':float(np.mean([x['before_error'] for x in v['points'] if x['role']=='fit'])),'trial_fit_mean':float(np.mean([x['trial_error'] for x in v['points'] if x['role']=='fit'])),'heldout_before':[round(x['before_error'],1) for x in v['points'] if x['role']=='heldout'],'heldout_after':[round(x['trial_error'],1) for x in v['points'] if x['role']=='heldout']} for k,v in results.items()},indent=2))
