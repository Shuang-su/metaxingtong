import numpy as np,json
from pathlib import Path
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];V=json.loads((R/'analysis/joint_constraints.json').read_text());ks=['A','B','D']
def old(k):
 a=json.loads((R.parent/'analysis'/f'{k}_camera_fit.json').read_text())['params'];return np.array(a[:3]+[a[3],0,a[4],a[5]])
def project(cam,p):
 c=(p-cam[:3])@Rotation.from_euler('xyz',cam[3:6]).as_matrix();f=cam[6]*1180/36;return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
def transform(p,n,g):
 p=np.array(p,float).copy();p[:,1]=5.44+g[0]*(p[:,1]-5.44)
 if n.startswith('ceiling') or 'round' in n:p[:,2]+=g[1]
 if n.startswith('rack'):p[:,2]+=g[2]
 return p
def residual(cam,k,g,split,weighted=True):
 rr=[];detail=[]
 for p in V[k]['points']:
  if p['split']!=split:continue
  q=project(cam,transform([p['world']],p['name'],g))[0];e=q-p['source'];rr.extend(e/(p['sigma_px'] if weighted else 1));detail.append({'name':p['name'],'error_px':float(np.linalg.norm(e)),'projected':q.tolist(),'source':p['source']})
 if split=='fit':
  for l in V[k]['lines']:
   a,b=project(cam,transform(l['world'],l['name'],g));d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d);e=(np.array(l['source'])-a)@n;rr.extend(e/(l['sigma_px'] if weighted else 1));detail.append({'name':l['name'],'errors_px':e.tolist()})
 return np.array(rr),detail
base=np.concatenate([old(k) for k in ks]);lower=np.tile([-1.45,-5.5,.7,1.2,-.1,-.1,14],3);upper=np.tile([1.45,4,2.1,1.95,.1,.7,40],3)
res={}
for label,initial,lo,hi in [('camera_only',[],[],[]),('shared_y_roof_rack',[1,0,0],[.75,-.06,-.18],[1.3,.22,.12])]:
 def g(x):return x[-3:] if initial else np.array([1,0,0])
 def fun(x):return np.concatenate([residual(x[j*7:j*7+7],k,g(x),'fit')[0] for j,k in enumerate(ks)])
 s=least_squares(fun,np.r_[base,initial],bounds=(np.r_[lower,lo],np.r_[upper,hi]),loss='soft_l1',f_scale=2,max_nfev=2500)
 out={'shared_y_scale_roof_dz_rack_dz':g(s.x).tolist(),'cameras':{},'active_bounds':np.where(np.minimum(abs(s.x-np.r_[lower,lo]),abs(s.x-np.r_[upper,hi]))<.001)[0].tolist(),'singular_values':np.linalg.svd(s.jac,compute_uv=False).tolist()}
 for j,k in enumerate(ks):
  c=s.x[j*7:j*7+7];out['cameras'][k]={'camera':c.tolist(),'fit_details':residual(c,k,g(s.x),'fit')[1],'check_details':residual(c,k,g(s.x),'check')[1],'old_check_details':residual(old(k),k,[1,0,0],'check')[1]};print(label,k,c,[(q['name'],round(q['error_px'],1)) for q in out['cameras'][k]['check_details']],flush=True)
 res[label]=out;print('shared',g(s.x),'bounds',out['active_bounds'],flush=True)
(R/'analysis/front_edge_fit_results.json').write_text(json.dumps(res,indent=2))
