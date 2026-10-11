import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def fit(label,pairs,initial):
 P=np.array([p for n,p,q in pairs]);Q=np.array([q for n,p,q in pairs])
 def project(v):
  rot=Rotation.from_euler('xyz',[v[3],0,v[4]]).as_matrix();cam=(P-v[:3])@rot;f=v[5]*1180/36
  return np.array([590+f*cam[:,0]/-cam[:,2],332-f*cam[:,1]/-cam[:,2]]).T
 sol=least_squares(lambda v:(project(v)-Q).ravel(),initial,bounds=([-1.4,-7,.8,1.4,-.1,23.9999],[1.4,-3,1.9,1.95,.6,24.0001]),loss='soft_l1',f_scale=12,max_nfev=2000)
 out={'params':sol.x.tolist(),'rmse_px':float(np.sqrt(np.mean((project(sol.x)-Q)**2))),'landmarks':[{'name':n,'world':p,'source':q,'projected':r.tolist(),'error_px':float(np.linalg.norm(r-q))} for (n,p,q),r in zip(pairs,project(sol.x))],'caveat':'Sparse hand landmarks, fixed 24mm working lens; unresolved geometry/occlusion separately reported.'};(R/'analysis'/f'{label}_camera_fit.json').write_text(json.dumps(out,indent=2));print(label,sol.x,'RMSE',out['rmse_px'])
# A2 corresponding source, same layout as D2/B2. All target y excludes 27px black border.
a=[]
for i,(y,q) in enumerate(zip([-3.23,-1.88,-.53,.82,2.17],[(394,11),(522,188),(579,266),(608,308),(631,335)])):a.append((f'round{i}',[0,y,2.565],q))
a += [('signL',[-.415,5.432,2.475],[620,384]),('signR',[.415,5.432,2.475],[685,384]),('nearR',[.4425,-3.72,1.28],[409,551]),('midR',[.4425,-1.92,1.28],[600,497])]
fit('A',a,[.93,-5,1.43,1.73,.18,24])
d=[]
for i,(y,q) in enumerate(zip([-1.88,-.53,.82,2.17,3.52,4.87],[(726,113),(747,186),(761,225),(770,252),(777,269),(782,281)])):d.append((f'round{i}',[0,y,2.565],q))
d += [('signL',[-.415,5.432,2.475],[741,297]),('signR',[.415,5.432,2.475],[813,297]),('nearR',[.4425,-1.92,1.28],[798,500]),('midR',[.4425,-.12,1.28],[804,422])]
fit('D',d,[.3,-5,1.5,1.58,.28,24])
b=[]
for i,(y,q) in enumerate(zip([-1.88,-.53,.82,2.17,3.52,4.87],[(366,22),(427,135),(457,196),(481,233),(491,257),(503,274)])):b.append((f'round{i}',[0,y,2.565],q))
b += [('nearR',[.4425,-3.72,1.28],[253,303])]
fit('B',b,[.89,-4.82,1.18,1.629,0,24])
