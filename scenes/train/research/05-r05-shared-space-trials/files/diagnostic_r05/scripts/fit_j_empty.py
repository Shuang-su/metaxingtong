import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1]
# Local side-plane gauge only: left/right side and absolute bay remain unresolved.
# Straight lower side reveals are visible; upper corners behind curtains are NOT observations.
lines=[('top',[[422,293],[825,290]]),('bottom',[[381,590],[910,589]]),('left',[[350,463],[352,537]]),('right',[[926,446],[925,537]])]
lines=[(n,np.array(q)-[0,27]) for n,q in lines]
def project(cam,p):
 c=(np.array(p)-cam[:3])@Rotation.from_euler('xyz',cam[3:6]).as_matrix();f=24*1180/36;return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
def wline(name,top,bottom):
 if name in ['top','bottom']:return [[-1.49,-1.516,top if name=='top' else bottom],[-1.49,-.284,top if name=='top' else bottom]]
 return [[-1.49,-1.516 if name=='left' else -.284,bottom],[-1.49,-1.516 if name=='left' else -.284,top]]
def residual(x,free):
 cam=x[:6];top,bottom=x[6:] if free else [2.0975,.9625];rr=[]
 for n,q in lines:
  a,b=project(cam,wline(n,top,bottom));d=b-a;normal=np.array([-d[1],d[0]])/np.linalg.norm(d);rr.extend((q-a)@normal/3)
 # Photometric bar center is a separately fitted shared fixture height, not a window edge.
 rr.extend((project(cam,[[-1.368,-.9,1.785]])[0]-[625,231])/4)
 # Front rack longitudinal rail can be identified above curtain; retain as weak check, not fitted.
 return np.array(rr)
out={}
for free in [False,True]:
 x0=[.2,-.9,1.5,1.57,0,1.57]+([1.71,1.08] if free else []);lo=[-1,-2,.7,1.2,-.2,1.3]+([1.45,.8] if free else []);hi=[1.4,0,2.2,1.95,.2,1.85]+([2.15,1.45] if free else [])
 s=least_squares(lambda x:residual(x,free),x0,bounds=(lo,hi),loss='soft_l1',f_scale=2,max_nfev=2000);cam=s.x[:6];top,bottom=s.x[6:] if free else [2.0975,.9625]
 rr={'camera_24mm_gauge':cam.tolist(),'window_top':float(top),'window_bottom':float(bottom),'window_height':float(top-bottom),'width_over_height':float(1.232/(top-bottom)),'weighted_residuals':residual(s.x,free).tolist(),'fit':[],'check':{}}
 for n,q in lines:
  a,b=project(cam,wline(n,top,bottom));d=b-a;normal=np.array([-d[1],d[0]])/np.linalg.norm(d);rr['fit'].append({'name':n,'source':q.tolist(),'projection':[a.tolist(),b.tolist()],'signed_distances':((q-a)@normal).tolist()})
 for n,p in [('rack_front',[-.88,-.9,2.19]),('old_sash',[-1.466,-.9,1.59]),('head_strip',[-1.368,-.9,1.785]),('hook',[-1.4375,.15,1.9])]:rr['check'][n]=project(cam,[p])[0].tolist()
 out['compressed_window' if free else 'r03_window']=rr;print('free',free,'cam',cam,'top/bottom',top,bottom,'ratio',rr['width_over_height'],'residual',residual(s.x,free),flush=True)
(R/'analysis/J_empty_plane_fit.json').write_text(json.dumps(out,indent=2))
