import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
root=Path(__file__).resolve().parents[1]
obs=np.array([[689,339],[882,320],[854,566],[660,576]])
p=np.array([[-.5,.6,0],[.5,.6,0],[.5,-.6,0],[-.5,-.6,0]])
def project(v):
 q=p@Rotation.from_rotvec(v[:3]).as_matrix().T+v[3:6];return np.array([540+1000*q[:,0]/-q[:,2],301.5-1000*q[:,1]/-q[:,2]]).T
r=least_squares(lambda v:(project(v)-obs).ravel(),[-.2,-.3,.06,1.2,-.75,-5],max_nfev=10000)
json.dump({'rotation':Rotation.from_rotvec(r.x[:3]).as_matrix().tolist(),'translation':r.x[3:].tolist(),'source_landmarks':obs.tolist(),'projected':project(r.x).tolist(),'rms_pixels':float(np.sqrt(np.mean((project(r.x)-obs)**2))),'focal_pixels':1000,'image_size':[1080,603],'jacobian_singular_values':np.linalg.svd(r.jac,compute_uv=False).tolist(),'jacobian_condition':float(np.linalg.cond(r.jac)),'initial_guess':[-.2,-.3,.06,1.2,-.75,-5],'method':'Uncalibrated conditional four-corner fit. Assumed 1:1.2 panel ratio and focal 1000 pixels; not camera calibration.'},open(root/'qa/camera-fit.json','w'),indent=2)
