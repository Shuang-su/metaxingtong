from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1]
exec((R/'scripts/fit_source_cameras.py').read_text().split('out={}')[0])
# White-candidate holdout: camera only from unchanged column axes, not new opening or stairs.
world=np.array([[-4.25,6,.51],[-4.25,12,.51],[-4.25,18,.51],[4.25,6,.51],[4.25,12,.51],[4.25,18,.51],[-4.25,18,7.36],[4.25,18,7.36]])
uv=np.array([[223,405],[345,367],[420,353],[1006,378],[846,366],[774,350],[420,95],[774,100]],float)
weights=np.array([[5,16],[5,10],[5,12],[5,8],[5,12],[5,12],[6,6],[6,6]])
def res(p):return np.r_[((project(world,p)-uv)/weights).ravel(),p[0]/3,p[5]/.03]
s=least_squares(res,[0,-5,1.7,0,-.04,0,950],bounds=([-3,-16,.4,-.2,-.3,-.08,400],[3,-.5,3.5,.2,.3,.08,1600]),max_nfev=2000);p=s.x;M,C,f=matrix(p)
out={'role':'Held-out frontal image; camera only fitted to unchanged column axes with explicit manual-observation uncertainty. New arch/stairs never used. No feedback to geometry.','source':'hall_B_4509_paused_core.png','time':4509.25218,'parameters':p.tolist(),'location':C.tolist(),'right':M[0].tolist(),'up':M[1].tolist(),'forward':M[2].tolist(),'focal_pixels':float(f),'lens_mm':float(f*36/1180),'observations':uv.tolist(),'world_anchors':world.tolist(),'projected':project(world,p).tolist(),'anchor_error_px':np.linalg.norm(project(world,p)-uv,axis=1).tolist(),'caveat':'This local column-camera calibration is not a whole-room source-fit acceptance.'};(R/'qa/holdout_camera_4509.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
