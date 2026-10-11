import numpy as np,json
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1];V=json.loads((R/'analysis/base_constraints.json').read_text());ks=['A','B','D']
extra={'A':[(-1,-2.7,[49,367],'fit'),(-1,-.9,[341,419],'check'),(-1,.9,[451,440],'check'),(-1,2.7,[512,452],'check'),(-1,4.5,[549,460],'check'),(1,-2.7,[919,350],'fit'),(1,-.9,[829,412],'check')], 'B':[(-1,-.9,[161,293],'fit'),(1,-2.7,[791,176],'fit')], 'D':[(-1,-2.7,[295,303],'fit'),(1,-.9,[1011,332],'fit'),(1,.9,[945,351],'check'),(1,2.7,[913,363],'check')]}
for p in V['A']['points']:
 if p['name']=='legacy_hypothesis_nearR':p['source']=[438,556];p['sigma_px']=8;p['source_correction']='Old409,551 marked dark bevel side, not the visible upper green contour; corrected on unchanged original A2 crop.'
for p in V['D']['points']:
 if p['name']=='legacy_hypothesis_nearR':p['world'][1]=-3.72;p['source']=[800,506];p['sigma_px']=8
 if p['name']=='legacy_hypothesis_midR':p['world'][1]=-1.92
for k,pts in extra.items():
 for side,y,q,split in pts:V[k]['points'].append({'name':f'wall_head_{side}_{y}','world':[side*1.368,y,2.107],'source':[q[0],q[1]-27],'split':split,'sigma_px':4,'identity':'Bay hypothesis from r03 closest visible head-strip order. Confirmed object class, bay not a measured index.'})
 for p in V[k]['points']:
  if p['name']=='legacy_hypothesis_nearR':p['split']='fit';p['sigma_px']=8
(R/'analysis/seat_contour_refined_constraints.json').write_text(json.dumps(V,indent=2))
def old(k):
 a=json.loads((R.parent/'analysis'/f'{k}_camera_fit.json').read_text())['params'];return np.array(a[:3]+[a[3],0,a[4],a[5]])
def project(cam,p):
 c=(p-cam[:3])@Rotation.from_euler('xyz',cam[3:6]).as_matrix();f=cam[6]*1180/36;return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
def res(cam,k,z,split='fit',details=False,rackz=2.19,rackx=.88):
 rr=[];dd=[]
 for p in V[k]['points']:
  if p['split']!=split:continue
  w=np.array([p['world']],float)
  if p['name'].startswith('wall_head'):w[:,2]=z
  pr=project(cam,w)[0];e=pr-p['source'];rr.extend(e/p['sigma_px']);dd.append({'name':p['name'],'projected':pr.tolist(),'source':p['source'],'error_px':float(np.linalg.norm(e))})
 if split=='fit':
  for l in V[k]['lines']:
   if not l['name'].startswith(('ceiling','rack')):continue
   w=np.array(l['world'],float)
   if l['name'].startswith('rack'):w[:,2]=rackz;w[:,0]=np.sign(w[:,0])*rackx
   a,b=project(cam,w);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d);e=(np.array(l['source'])-a)@n;rr.extend(e/l['sigma_px']);dd.append({'name':l['name'],'errors_px':e.tolist()})
 return dd if details else np.array(rr)
base=np.concatenate([old(k) for k in ks]);lo=np.tile([-1.4,-8,.6,1.15,-.10,-.3,14],3);hi=np.tile([1.4,3,2.2,2,.1,.8,40],3);out={}
for label,zvar in [('shared_head_and_rack_height',True)]:
 init=np.r_[base,1.85,2.0,1.1] if zvar else base;lower=np.r_[lo,1.6,1.75,.70] if zvar else lo;upper=np.r_[hi,2.2,2.3,1.4] if zvar else hi
 def f(x):return np.concatenate([res(x[j*7:j*7+7],k,x[-3] if zvar else 2.107,rackz=x[-2],rackx=x[-1]) for j,k in enumerate(ks)])
 s=least_squares(f,init,bounds=(lower,upper),loss='soft_l1',f_scale=2,max_nfev=2500);z=s.x[-3] if zvar else 2.107
 o={'rack_inner_x':float(s.x[-1]),'rack_height':float(s.x[-2]),'headlight_height':float(z),'active_bounds':np.where(np.minimum(abs(s.x-lower),abs(s.x-upper))<.001)[0].tolist(),'cameras':{}}
 for j,k in enumerate(ks):
  c=s.x[j*7:j*7+7];o['cameras'][k]={'camera':c.tolist(),'fit':res(c,k,z,'fit',True,rackz=s.x[-2],rackx=s.x[-1]),'check':res(c,k,z,'check',True),'old_check':res(old(k),k,2.107,'check',True)};print(label,k,c.round(3),[(a['name'],round(a['error_px'],1)) for a in o['cameras'][k]['check']],flush=True)
 out[label]=o;print('height',z,'bounds',o['active_bounds'],flush=True)
(R/'analysis/seat_contour_refined_fit.json').write_text(json.dumps(out,indent=2))
