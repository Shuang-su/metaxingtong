import numpy as np,json
from scipy.optimize import least_squares
p='seaside-arch-candidate-20261105/qa/landmarks.json';d=json.load(open(p));pts=d['cameras']['SOURCE04 conditional'];pts=[p for p in pts if p['source_pixel'] is not None and p['name'] not in ['outer_left','outer_right','inner_apex']]
X=np.array([p['model_world'] for p in pts]);obs=np.array([p['source_pixel'] for p in pts])
def project(a):
 loc=np.array(a[:3]);target=np.array([a[3],2.5,a[4]]);fwd=(target-loc);fwd/=np.linalg.norm(fwd);right=np.cross(fwd,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,fwd);v=X-loc;f=a[5]*1192/36;return np.column_stack([596+f*(v@right)/(v@fwd),335.5-f*(v@up)/(v@fwd)])
r=least_squares(lambda a:(project(a)-obs).ravel(),[2.7,-12.4,3.25,.9,2.85,37],bounds=([0,-20,2,-1,1,30],[4,-10,4.5,3,4,65]),max_nfev=1000)
print(r.x);print(project(r.x));print(obs);print('rms',np.sqrt(np.mean((project(r.x)-obs)**2)));json.dump({'parameters':r.x.tolist(),'method':'scipy least_squares conditional 6DOF camera, weak same-state near-frontal observations, no geometry change','source_points':pts,'predicted':project(r.x).tolist(),'rms_pixels':float(np.sqrt(np.mean((project(r.x)-obs)**2)))},open('seaside-arch-candidate-20261105/qa/camera-fit04.json','w'),indent=2)
