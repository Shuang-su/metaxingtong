import numpy as np,json,pathlib
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
P=pathlib.Path(__file__).resolve().parents[1];src=json.load(open(P/'source-diagnosis/landmarks-v1.json'));seeds=json.load(open(P/'qa/R05-camera-seeds.json'));out={}
world=np.array([[-1,1,0],[1,1,0],[1,-1,0],[-1,-1,0]],float);world[:,:2]*=3/np.sqrt(2);world[:,2]=.495
inside=np.array([[-.85,0,.495],[0,.85,.495],[.85,0,.495],[0,-.85,.495]])
for number,name in [(13,'SOURCE_13_high'),(21,'SOURCE_21_high')]:
 d=next(d for d in src['images'] if pathlib.Path(d['source']).stem==str(number));obs=np.array([next(x['xy'] for x in d['landmarks'] if x['id']=='S'+str(i+1)) for i in range(4)])
 m=np.array(seeds[name]['matrix_world']);rot=Rotation.from_matrix(m[:3,:3].T).as_rotvec();t=-m[:3,:3].T@m[:3,3];x0=np.r_[rot,t,22.]
 def proj(x,points=world):
  v=points@Rotation.from_rotvec(x[:3]).as_matrix().T+x[3:6];z=-v[:,2];return np.c_[596+x[6]/36*1192*v[:,0]/z,335.5-x[6]/36*1192*v[:,1]/z],z
 def fun(x):
  pp,z=proj(x);return np.r_[(pp-obs).ravel(),np.minimum(z-.05,0)*1000]
 fit=least_squares(fun,x0,bounds=(np.r_[[-np.inf]*6,12],np.r_[[np.inf]*6,80]),max_nfev=3000,xtol=1e-13,ftol=1e-13,gtol=1e-13)
 r=Rotation.from_rotvec(fit.x[:3]).as_matrix();cam=np.eye(4);cam[:3,:3]=r.T;cam[:3,3]=-r.T@fit.x[3:6];pp,z=proj(fit.x)
 cs=[x for x in d['landmarks'] if x['id'] in ('C1','C2','C3','C4')];ic=proj(fit.x,inside)[0];cobs=np.array([next(x['xy'] for x in cs if x['id']=='C'+str(i+1)) for i in range(4)]) if len(cs)==4 else None
 out[name]={'source_number':number,'source_sha256':d['sha256'],'training':'four manually observed star outer tips, world identity/orientation and shape assumed, not calibrated/held-out','world':world.tolist(),'observed':obs.tolist(),'matrix_world':cam.tolist(),'lens_mm':float(fit.x[6]),'baseline_error_px':np.linalg.norm(proj(x0)[0]-obs,axis=1).tolist(),'fit_error_px':np.linalg.norm(pp-obs,axis=1).tolist(),'depth':z.tolist(),'camera_radial':float(np.linalg.norm(cam[:2,3])),'camera_z':float(cam[2,3]),'inner_assumption_diagnostic_error_px':None if cobs is None else np.linalg.norm(ic-cobs,axis=1).tolist(),'constraint_limit':'7 camera parameters fit 8 scalar measurements of one plane. No independent scale or wall validation. Must inspect actual visibility and full-image mismatch; no geometry changed.'}
print(json.dumps(out,indent=2));(P/'qa/R06-star-fit.json').write_text(json.dumps(out,indent=2))
