import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def fit(label,pairs,initial,bounds):
 P=np.array([p for n,p,q in pairs]);Q=np.array([q for n,p,q in pairs])
 def project(v):
  rot=Rotation.from_euler('xyz',[v[3],0,v[4]]).as_matrix();cam=(P-v[:3])@rot;f=v[5]*1180/36
  return np.array([590+f*cam[:,0]/-cam[:,2],332-f*cam[:,1]/-cam[:,2]]).T
 sol=least_squares(lambda v:(project(v)-Q).ravel(),initial,bounds=bounds,loss='soft_l1',f_scale=15,max_nfev=2000)
 out={'params':sol.x.tolist(),'rmse_px':float(np.sqrt(np.mean((project(sol.x)-Q)**2))),'landmarks':[{'name':n,'world':p,'source':q,'projected':r.tolist(),'error_px':float(np.linalg.norm(r-q))} for (n,p,q),r in zip(pairs,project(sol.x))],'caveat':'Sparse plane-based camera initialization only; multi-surface residual remains.'};(R/'analysis'/f'{label}_camera_fit.json').write_text(json.dumps(out,indent=2));print(label,sol.x,'RMSE',out['rmse_px'])
# Front-end close and performance have clear frame and signage, independent of animated performer.
i=[('signL',[-.445,5.472,2.475],[478,136]),('signR',[.445,5.472,2.475],[715,136]),('doorTL',[-.477,5.44,2.314],[469,174]),('doorTR',[.477,5.44,2.314],[727,174]),('windowTL',[-.275,5.43,2.08],[523,237]),('windowBR',[.275,5.43,1.28],[669,472])]
fit('I',i,[0,2.4,1.7,1.6,0,24],([-1,0,.8,1.2,-.3,23.9999],[1,4,2,1.9,.3,24.0001]))
f=[('signL',[-.445,5.472,2.475],[488,81]),('signR',[.445,5.472,2.475],[659,81]),('doorTL',[-.477,5.44,2.314],[477,109]),('doorTR',[.477,5.44,2.314],[664,109]),('windowTL',[-.275,5.43,2.08],[520,157])]
fit('F',f,[0,1.3,1.4,1.5,0,24],([-1,-1,.8,1.2,-.3,23.9999],[1,4,2,1.9,.3,24.0001]))
h=[('signL',[-.445,5.472,2.475],[994,104]),('signR',[.445,5.472,2.475],[1078,104]),('doorTL',[-.477,5.44,2.314],[987,119]),('doorTR',[.477,5.44,2.314],[1084,119]),('windowTL',[-.275,5.43,2.08],[1008,138]),('windowBR',[.275,5.43,1.28],[1059,211])]
fit('H',h,[.9,-2.3,1.55,1.55,.63,24],([-1.4,-5,.8,1.2,.3,23.9999],[1.4,1,2,1.9,.95,24.0001]))
# Side window J: side identity assumed left and longitudinal bay identity unresolved.
j=[('windowTL',[-1.49,-.9-.616,2.0975],[387,252]),('windowTR',[-1.49,-.9+.616,2.0975],[993,252]),('windowBL',[-1.49,-.9-.616,.9625],[387,567]),('windowBR',[-1.49,-.9+.616,.9625],[993,567])]
fit('J',j,[(.4),-.9,1.8,1.65,1.57,24],([-1,-2,1.2,1.2,1.1,18],[1.4,0,2.2,1.9,2,30]))
