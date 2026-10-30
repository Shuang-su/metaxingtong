"""Conditional camera fit to approximate manually picked static anchors only.
Not an independent calibration or validation: fit and residual use same points.
No source warp, character anchor or geometry change.
"""
from pathlib import Path
import numpy as np,json,math
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];Q=R/'qa'
rows=json.loads((Q/'source_landmark_residuals.json').read_text());cams=json.loads((R/'stage-02-material-candidate/camera_parameters.json').read_text())
output={}
for cid in ['SRC02','SRC04']:
    rr=[r for r in rows if r['camera']==cid];xyz=np.array([r['model_xyz'] for r in rr]);xy=np.array([r['source_xy_approx'] for r in rr]);c=cams[cid];loc=np.array(c['location']);d=np.array(c['target'])-loc;yaw=math.atan2(d[0],d[1]);pitch=math.atan2(d[2],np.linalg.norm(d[:2]));p0=np.r_[loc,yaw,pitch,c['lens_mm']]
    def project(p):
        x,y,z,a,e,lens=p;f=lens*1920/36;forward=np.array([math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)]);right=np.array([math.cos(a),-math.sin(a),0]);up=np.cross(right,forward);v=xyz-[x,y,z];dep=v@forward
        return np.c_[960+f*(v@right)/dep,540-f*(v@up)/dep]
    def fun(p):return (project(p)-xy).ravel()
    fit=least_squares(fun,p0,bounds=([-28,-42,1,.25,-.25,35],[8,-10,6,1.5,.20,65]),max_nfev=400,loss='soft_l1',f_scale=30)
    p=fit.x;direction=np.array([math.sin(p[3])*math.cos(p[4]),math.cos(p[3])*math.cos(p[4]),math.sin(p[4])]);target=p[:3]+direction*50
    output[cid]={'location':p[:3].tolist(),'target':target.tolist(),'lens_mm':float(p[5]),'mean_fit_residual_px':float(np.mean(np.linalg.norm(project(p)-xy,axis=1))),'before_mean_px':float(np.mean(np.linalg.norm(project(p0)-xy,axis=1))),'fit_points':rr,'independent_validation':False,'status':'manual anchors, conditional diagnostic, neither source acceptance nor solved real scale'}
(Q/'conditional_camera_fit.json').write_text(json.dumps(output,indent=2));print(json.dumps({k:{'location':v['location'],'target':v['target'],'lens_mm':v['lens_mm'],'mean':v['mean_fit_residual_px'],'before':v['before_mean_px']} for k,v in output.items()},indent=2))
