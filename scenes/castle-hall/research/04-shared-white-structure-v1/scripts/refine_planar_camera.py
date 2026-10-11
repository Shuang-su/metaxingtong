from pathlib import Path
import json,numpy as np,math
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];V=R.parent/'castlehall_hd_verification_20261010/references'
# Import definitions without executing previous fitter.
code=(R/'scripts/fit_source_cameras.py').read_text().split('out={}')[0];exec(code)
fits=json.loads((R/'qa/source_camera_fits.json').read_text());p29=np.array(fits['fit_4529']['parameters']);p28=np.array(fits['fit_4528']['parameters'])
matches=json.loads((R/'qa/static_wall_patch_matches.json').read_text())['matches']
pa=np.array([x[:2] for x in matches],float);pb=np.array([x[2:4] for x in matches],float)
M,C,f=matrix(p29)
def backproject_wall(uv,wall=7):
 dirs=np.stack(((uv[:,0]-590)/f,(332-uv[:,1])/f,np.ones(len(uv))),axis=-1)@M
 t=(wall-C[0])/dirs[:,0];return C+dirs*t[:,None]
points=backproject_wall(pb)
def res(p):
 rr=((project(points,p)-pa)/1.5).ravel().tolist()
 # Same static geometry, approximate external field of view. Keep gross priors weak.
 rr += [(p[-1]-p29[-1])/400,(p[2]-p29[2])/.8,p[5]/.12]
 return rr
sol=least_squares(res,p28,bounds=([-7,-18,.3,-.1,-.4,-.15,450],[5,3,4,1.6,.4,.15,2000]),max_nfev=2000)
p=sol.x;pr=project(points,p);err=np.linalg.norm(pr-pa,axis=1)
M,C,f=matrix(p)
result={'method':'Static right-wall Harris/NCC patch correspondences → wall-plane backprojection in the 4529 baseline camera → true perspective camera fit in 4528. Homography selects inliers only; neither reference image is warped. The nominal existing wall X=7 and 4529 camera remain uncertain reconstruction priors.','num_correspondences':len(pa),'point_residual_median_px':float(np.median(err)),'point_residual_max_px':float(max(err)),'parameters':p.tolist(),'location':C.tolist(),'right':M[0].tolist(),'up':M[1].tolist(),'forward':M[2].tolist(),'focal_pixels':float(f),'lens_mm':float(f*36/1180),'source_points_4528':pa.tolist(),'source_points_4529':pb.tolist(),'world_wall_points':points.tolist(),'projected_columns':{str(j):col(j,p) for j in [1,2,3,4]}}
(R/'qa/planar_camera_fit_4528.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['source_points_4528','source_points_4529','world_wall_points']},indent=2))
