import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1];V=json.loads((R/'analysis/constraints.json').read_text())
def oldcam(k):
 a=json.loads((R.parent/'analysis'/f'{k}_camera_fit.json').read_text())['params'];return np.array(a[:3]+[a[3],0,a[4],a[5]])
def project(cam,p):
 p=np.asarray(p,float);c=(p-cam[:3])@Rotation.from_euler('xyz',cam[3:6]).as_matrix();f=cam[6]*1180/36
 return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
def line_errors(cam,item,roofscale=1,roofdz=0,rackdx=0,rackdz=0):
 p=np.array(item['world'],float)
 if item['name'].startswith('ceiling'):p[:,0]*=roofscale;p[:,2]+=roofdz
 if item['name'].startswith('rack'):p[:,0]+=np.sign(p[:,0])*rackdx;p[:,2]+=rackdz
 a,b=project(cam,p);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)
 return (np.array(item['source'])-a)@n

def residual(cam,k,split='fit',weighted=False,roofscale=1,roofdz=0):
 rr=[]
 for p in V[k]['points']:
  if p['split']==split:
   e=(project(cam,[p['world']])[0]-p['source']);rr.extend(e/(p['sigma_px'] if weighted else 1))
 for l in V[k]['lines']:
  if l['split']==split:rr.extend(line_errors(cam,l,roofscale,roofdz)/(l['sigma_px'] if weighted else 1))
 return np.array(rr)
def detail(cam,k,roofscale=1,roofdz=0):
 o=[]
 for p in V[k]['points']:
  pr=project(cam,[p['world']])[0];o.append({'name':p['name'],'split':p['split'],'error_px':float(np.linalg.norm(pr-p['source'])),'projected':pr.tolist()})
 for l in V[k]['lines']:o.append({'name':l['name'],'split':l['split'],'errors_px':line_errors(cam,l,roofscale,roofdz).tolist()})
 return o
bounds=(np.array([-2.5,-14,.3,1.1,-.18,-.3,12]),np.array([2.5,4.8,2.5,2.1,.18,1.2,50]))
out={}
for k in ['A','D','H','I','F']:
 base=oldcam(k);sol=least_squares(lambda x:residual(x,k,weighted=True),np.clip(base,bounds[0]+1e-4,bounds[1]-1e-4),bounds=bounds,loss='soft_l1',f_scale=2,max_nfev=3000)
 vals=[]
 for f in [14,16,18,20,24,28,32,36,40,45]:
  s=least_squares(lambda x:residual(np.r_[x,f],k,weighted=True),sol.x[:6],bounds=(bounds[0][:6],bounds[1][:6]),loss='soft_l1',f_scale=2,max_nfev=1500)
  vals.append({'focal_mm_working':f,'fit_rms_px_components':float(np.sqrt(np.mean(residual(np.r_[s.x,f],k)**2))),'camera':np.r_[s.x,f].tolist()})
 singular=np.linalg.svd(sol.jac,compute_uv=False)
 out[k]={'old_camera':base.tolist(),'camera_only':sol.x.tolist(),'old':detail(base,k),'new':detail(sol.x,k),'fit_rms_old':float(np.sqrt(np.mean(residual(base,k)**2))),'fit_rms_new':float(np.sqrt(np.mean(residual(sol.x,k)**2))),'check_rms_old':float(np.sqrt(np.mean(residual(base,k,'check')**2))),'check_rms_new':float(np.sqrt(np.mean(residual(sol.x,k,'check')**2))),'singular_values_weighted_jacobian':singular.tolist(),'focal_profile':vals}
 print(k,'cam',sol.x.round(3),'fit',out[k]['fit_rms_old'],out[k]['fit_rms_new'],'holdout',out[k]['check_rms_old'],out[k]['check_rms_new'],'sv',singular[-1])
(R/'analysis/camera_only_results.json').write_text(json.dumps(out,indent=2))
# Joint A/D/H with one shared central ceiling width and height; full car shell untouched in hypothesis.
ks=['A','D','H'];init=np.r_[np.concatenate([out[k]['camera_only'] for k in ks]),1,0]
lo=np.r_[np.tile(bounds[0],3),.65,-.25];hi=np.r_[np.tile(bounds[1],3),1.6,.25]
def jr(x):return np.concatenate([residual(x[j*7:j*7+7],k,weighted=True,roofscale=x[-2],roofdz=x[-1]) for j,k in enumerate(ks)])
sol=least_squares(jr,init,bounds=(lo,hi),loss='soft_l1',f_scale=2,max_nfev=3000)
jo={'shared_roof_width_scale':sol.x[-2],'shared_roof_height_delta':sol.x[-1],'singular_values':np.linalg.svd(sol.jac,compute_uv=False).tolist(),'cameras':{},'warning':'Diagnostic latent variables only. No geometry edit authorized by a lower objective alone.'}
for j,k in enumerate(ks):jo['cameras'][k]={'camera':sol.x[j*7:j*7+7].tolist(),'detail':detail(sol.x[j*7:j*7+7],k,*sol.x[-2:])}
(R/'analysis/joint_roof_diagnostic.json').write_text(json.dumps(jo,indent=2));print('jointroof',sol.x[-2:],jo['singular_values'][-3:])
