import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
P=Path(__file__).resolve().parents[1];F=json.loads((P/'qa/camera_fit.json').read_text());PROP=json.loads((P/'qa/shared_prop_fit.json').read_text());exec((P/'scripts/fit_cameras.py').read_text().split('order=')[0]);K=F['k']
def ray(c,uv):
 x,y,z,tx,tz,f,roll=c;pos=np.array([x,y,z]);fw=np.array([tx,3,tz])-pos;fw/=np.linalg.norm(fw);rt=np.cross(fw,[0,0,1]);rt/=np.linalg.norm(rt);up=np.cross(rt,fw);u=(uv[0]-590)/f;v=(331.5-uv[1])/f;co,si=np.cos(roll),np.sin(roll);u,v=co*u+si*v,-si*u+co*v;return pos,fw+u*rt+v*up
keys=list(PROP['lamps']);rays={n:ray(F['cameras']['C']['params'],PROP['lamps'][n]['observations']['C'])for n in keys}
x0=F['cameras']['A']['params']+F['cameras']['B']['params']+[9.5]*len(keys)+[2.4,-3.2,4,-.5,2.5]
lo=[-9,-18,.4,-7,.1,350,-.22]*2+[5]*len(keys)+[0,-5,1,-4,1];hi=[9,-2,5,7,4.5,1800,.22]*2+[14]*len(keys)+[5,0,6,3,5]
v=star(K)
def fun(p):
 out=[]
 for ci,ck in enumerate(['A','B']):
  c=p[ci*7:ci*7+7];uv=proj(v,c)
  for ix,xy in F['observations'][ck].items():out.extend((uv[int(ix)]-xy)*.65)
  for ni,n in enumerate(keys):
   ob=PROP['lamps'][n]['observations']
   if ck not in ob:continue
   pos,r=rays[n];pt=pos+p[14+ni]*r;out.extend(proj(pt[None],c)[0]-ob[ck])
 # Shared floor disk center and resting ball constrain tilt/height beyond star outline.
 floorobs={'A':[550,690],'B':[580,655]}
 ballobs={'A':[1117,603],'B':[846,493],'C':[1030,548]}
 neonobs={'A':[1110,202],'B':[1100,225],'C':[1120,250]}
 ball=np.array([[p[-5],p[-4],.455]]);neon=np.array([p[-3:]])
 for i,ck in enumerate(['A','B']):out.extend((proj(np.array([[0,-4,.16]]),p[i*7:i*7+7])[0]-floorobs[ck])*.7)
 for ck in ['A','B','C']:
  c=F['cameras']['C']['params'] if ck=='C' else p[(0 if ck=='A' else 7):(7 if ck=='A' else 14)]
  out.extend((proj(ball,c)[0]-ballobs[ck])*.9)
  out.extend((proj(neon,c)[0]-neonobs[ck])*.7)
 return out
r=least_squares(fun,x0,bounds=(lo,hi),max_nfev=12000,loss='soft_l1',f_scale=12)
(P/'qa/camera_fit_before_shared_props.json').write_text(json.dumps(F,indent=2))
for i,key in enumerate(['A','B']):
 c=r.x[7*i:7*i+7];F['cameras'][key]['params']=c.tolist();uv=proj(v,c);errs=[np.linalg.norm(uv[int(j)]-xy)for j,xy in F['observations'][key].items()];F['cameras'][key]['predicted']=uv.tolist();F['cameras'][key]['mean_sparse_error_px']=float(np.mean(errs));F['cameras'][key]['max_sparse_error_px']=float(max(errs))
F['prop_joint_refinement']='C camera held, A/B common star silhouette and seven shared lamp centers jointly fit. Residuals explicitly retained.'
for i,n in enumerate(keys):
 pos,rr=rays[n];pt=pos+r.x[14+i]*rr;PROP['lamps'][n]['point']=pt.tolist();PROP['lamps'][n]['residuals_px']={}
 for k,xy in PROP['lamps'][n]['observations'].items():PROP['lamps'][n]['residuals_px'][k]=(proj(pt[None],F['cameras'][k]['params'])[0]-xy).tolist()
PROP['ball']={'xyz':[r.x[-5],r.x[-4],.455],'radius':.30};PROP['neon_center']=r.x[-3:].tolist()
(P/'qa/camera_fit.json').write_text(json.dumps(F,indent=2));(P/'qa/shared_prop_fit.json').write_text(json.dumps(PROP,ensure_ascii=False,indent=2));print('Mean abs weighted pixel residual',np.mean(np.abs(fun(r.x))))
for k in ['A','B']:print(k,F['cameras'][k]['params'],F['cameras'][k]['mean_sparse_error_px'])
for n in keys:print(n,PROP['lamps'][n]['point'],PROP['lamps'][n]['residuals_px'])
