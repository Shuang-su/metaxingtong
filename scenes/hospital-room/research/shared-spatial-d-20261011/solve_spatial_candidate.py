"""Reproduce the bounded D2 proxy experiment. Requires numpy/scipy; no rendering or source-image warping.
Training, holdouts and limitations are detailed in the adjacent report.
"""
from pathlib import Path
import numpy as np,json
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
R=Path(__file__).parent
problem=json.load(open(R/'fit_problem.json'));J={'cameras':problem['baseline_cameras'],'objects':problem['rail_anchor_objects']}
O={o['name']:o for o in problem['baseline_mesh_proxies']}
def cam(k):
 c=J['cameras'][k];m=np.array(c['matrix_world']);rt=m[:3,:3];rt=rt/np.linalg.norm(rt,axis=0);return np.r_[Rotation.from_matrix(rt).as_rotvec(),m[:3,3],np.log(c['lens'])]
def project(x,p):
 rt=Rotation.from_rotvec(x[:3]).as_matrix();q=(np.asarray(p)-x[3:6])@rt;f=np.exp(x[6])/36*1920;return np.c_[960-f*q[:,0]/q[:,2],540+f*q[:,1]/q[:,2]]

from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
D=problem['architectural_observations']
# Existing architectural lines are proxy axes with finite confidence, never exact source vertices.
obs=[]
for k in 'FGH':
 for a in D[k]:
  if a['id']=='rail_upper_edge':continue
  if a['split']=='direction_only':continue
  b=dict(a);b['view']=k;b['sigma_px']=max(6,b['sigma_px']);obs.append(b)
# Manually visually estimated SOFT contour points on native pixels, independent of model vertices.
contours=[
 ('F','Bed • observed endboard, consistent width',[[810,1076],[824,1019],[850,992],[1050,956],[1280,939],[1480,938],[1710,952],[1880,980]],15),
 ('G','Bed • observed endboard, consistent width',[[1546,972],[1544,863],[1550,824],[1573,795],[1615,777],[1712,755],[1817,742],[1918,731]],15),
 ('G','Sofa • reclined back cushion 1',[[198,925],[211,904],[241,891],[352,882],[485,878],[590,878]],18),
 ('G','Sofa • reclined back cushion 2',[[813,865],[872,865],[887,887],[909,945]],20),
 ('H','Sofa • reclined back cushion 1',[[858,830],[870,813],[897,803],[1030,797],[1188,794],[1210,817]],18),
 ('H','Sofa • reclined back cushion 2',[[1224,799],[1340,790],[1480,786],[1496,804],[1523,868]],18),
 ('G','Sofa • broad padded arm.001',[[912,944],[1005,949],[1156,962],[1166,1067]],18),
 ('H','Sofa • broad padded arm.001',[[1523,868],[1700,885],[1829,896],[1841,913],[1844,1012]],18),
]
# Historical D0 function below held out mattress and chair. Final D2 res1 later adds G/H mattress contours as low-weight training; chair and left-arm groups remain excluded.
BED0=np.array([3.8301885,-1.73290586,0.]);SOFANAMES=[n for n in O if n.startswith('Sofa')]
# q = 3 pose6, bed dx/dy/y-scale/z-scale, rail dx/dy/dz. Focal fixed per hypothesis.
def unpack(q,lenses):
 C={k:np.r_[q[i*6:(i+1)*6],np.log(lenses[i])] for i,k in enumerate('FGH')};return C
def geo(q,n,v):
 p=np.asarray(v).copy()
 if n.startswith('Bed'):
  p-=BED0;p[:,1]*=np.exp(q[20]);p[:,2]*=np.exp(q[21]);p+=BED0;p[:,0]+=q[18];p[:,1]+=q[19]
 if n.startswith('Curtain rail'):p+=q[22:25]
 return p
cache={}
# Use convex contour on convex cushion/rounded board upper; full projected mesh ensures no bbox corner substitution.
for k,n,pts,sig in contours:cache[n]=np.array(O[n]['vertices'])
def dist_to_hull(qxy,p):
 try:h=ConvexHull(qxy);poly=qxy[h.vertices]
 except:return np.ones(len(p))*10000
 a=poly;b=np.roll(poly,-1,axis=0);v=b-a;P=np.asarray(p);t=np.clip(((P[:,None,:]-a)*v).sum(2)/(v*v).sum(1),0,1);cp=a[None,:,:]+t[:,:,None]*v[None,:,:];dd=((P[:,None,:]-cp)**2).sum(2);idx=dd.argmin(1);return np.sqrt(dd[np.arange(len(P)),idx])
xbase=np.concatenate([cam(k)[:6] for k in 'FGH']);q0=np.r_[xbase,0.,0.,0.,0.,0.,0.,0.]
lo=q0-np.r_[np.tile([.5,.5,.5,2.5,2.5,1.0],3),1.8,.7,.45,.65,1.,1.,.3]
hi=q0+np.r_[np.tile([.5,.5,.5,2.5,2.5,1.8],3),1.,.7,.45,.65,1.,1.,.3]
# Keep all camera positions above floor; do not invent subterranean fitting views.
for i in range(3):lo[i*6+5]=.1

def residual(q,lenses,regularize=True):
 C=unpack(q,lenses);ee=[]
 for a in obs:
  k=a['view'];n=a['object_id'];p=geo(q,n,np.array(a['xyz']).reshape(-1,3));qq=project(C[k],p);uv=np.array(a['observed'])
  if a['kind']=='point':e=qq[0]-uv
  else:
   v=qq[1]-qq[0];nn=np.array([-v[1],v[0]])/np.linalg.norm(v);e=(uv-qq[0])@nn
  ee.extend(e/a['sigma_px'])
 for k,n,uv,sig in contours:
  p=geo(q,n,cache[n]);qq=project(C[k],p);ee.extend(dist_to_hull(qq,uv)/sig)
 # Near fixed rail upper visible edge, same definition in F/G.
 for k,uv in [('F',[[258,60],[620,9]]),('G',[[1016,48],[1134,2]])]:
  n='Curtain rail • forward overhead beam';p=np.array([J['objects'][0]['points'].get('origin',[0,0,0])])
  jo=next(o for o in J['objects'] if o['name']==n);p=np.array([jo['points']['bbox_2'],jo['points']['bbox_1']]);qq=project(C[k],geo(q,n,p));v=qq[1]-qq[0];nn=np.array([-v[1],v[0]])/np.linalg.norm(v);ee.extend((np.array(uv)-qq[0])@nn/12)
 # F sofa should stay outside image except the source's bottom border; use soft exclusion.
 for n in ['Sofa • broad padded arm.001','Sofa • reclined back cushion 2']:
  qq=project(C['F'],np.array(O[n]['vertices']));valid=(qq[:,0]>0)&(qq[:,0]<1920)
  if valid.any():ee.append(max(0,1080-qq[valid,1].min())/18)
  else:ee.append(0)
 if regularize:
  # Weak pose priors, meaningful metric unit only relative to B model scale.
  ee.extend((q[:18]-q0[:18])/np.tile([.25,.25,.25,1.5,1.5,.8],3))
  ee.extend(q[18:]/np.array([1.2,.5,.3,.4,.5,.5,.15]))
 return np.asarray(ee)

import copy
anns=json.load(open(R/'annotations_native_1920x1080.json'))['features'];af={a['id']:a for a in anns}
# D0 failure is retained: H chair regression; rail ended above ceiling; shared bed height wrongly raised mattress.
# D1 explicitly fixes H camera, separates bed support height from endboard form, and constrains rail inside shell.
contours=[c for c in contours if not c[0]=='H' and not c[1].startswith('Bed')]
for k,ids in [('F',['F_bed_upper_left_visible','F_bed_upper_right_visible']),('G',['G_bed_upper_visible'])]:
 for id in ids:contours.append((k,'Bed • observed endboard, consistent width',af[id]['source_xy'],10))
for k in 'FG':contours.append((k,'Bed end • moulded central recess',af[k+'_central_recess_visible_envelope']['source_xy'],10))
contours.extend([('G','Bed • mattress and sheet',[[1260,1058],[1400,1024],[1590,971],[1710,985],[1850,1000],[1919,1007]],15),('H','Bed • mattress and sheet',[[1210,1079],[1490,1054],[1730,1026],[1919,995]],18)])
# C-style rounded outline is an explicitly retained, unaccepted shared geometry hypothesis. Use analytic contour for screening.
for n in ['Bed end • moulded central recess','Bed end • cream inset face']:
 b=np.array(O[n]['bounds']);cx,cy,cz=b.mean(1);a,w,h=(b[:,1]-b[:,0])/2;pp=[]
 for x in [cx-a,cx+a]:
  for side,start in [(1,-np.pi/2),(-1,np.pi/2)]:
   for ang in np.linspace(start,start+np.pi,33):pp.append([x,cy+side*(w-h)+h*np.cos(ang),cz+h*np.sin(ang)])
 O[n]['vertices']=pp
cache={n:np.array(O[n]['vertices']) for k,n,uv,sig in contours}
# 0:18 poses (H fixed); 18 dx, 19 dy, 20 log width, 21 log board z, 22 rail x, 23 rail y fixed, 24 rail z;
# 25 log body z, 26 broad upper arch depression, 27 mid-board lift, 28 bed yaw.
def geo(q,n,v):
 p=np.asarray(v).copy()
 if n.startswith('Bed'):
  is_board=any(t in n for t in ['endboard','Bed end'])
  yy=p[:,1]+1.73290586;xx=p[:,0]-3.8301885
  u=np.clip(abs(yy)/1.1375,0,1)
  if is_board:
   t=np.clip((p[:,2]-.15125)/(.82125-.15125),0,1)
   p[:,2]+=q[27]*4*t*(1-t)
   if 'endboard' in n:p[:,2]-=q[26]*u*u*np.clip((p[:,2]-.61)/(.82125-.61),0,1)
   p[:,2]*=np.exp(q[21])
  else:p[:,2]*=np.exp(q[25])
  yy*=np.exp(q[20])
  if not is_board:yy*=np.exp(q[29]);xx*=np.exp(q[30])
  a=q[28]
  p[:,0]=3.8301885+xx*np.cos(a)-yy*np.sin(a)+q[18];p[:,1]=-1.73290586+xx*np.sin(a)+yy*np.cos(a)+q[19]
 if n.startswith('Curtain rail'):p+=q[22:25]
 return p
qinit=np.r_[problem['D1_initial_parameters'],np.log(.8),np.log(.85)]
qinit[12:18]=q0[12:18];qinit[24]=0.
lo=np.r_[lo,-.7,0.,0.,-.25,np.log(.5),np.log(.55)];hi=np.r_[hi,.4,.20,.20,.25,0.,0.];hi[24]=.015;lo[24]=-.25;hi[27]=.14
free=np.array([i for i in range(31) if i not in list(range(12,18))])
def full(y):q=qinit.copy();q[free]=y;return q
lenses=[np.exp(cam(k)[6]) for k in 'FGH']
def res1(q,reg=True):
 C=unpack(q,lenses);ee=[]
 for a in obs:
  if a['view']=='H':continue
  n=a['object_id'];qq=project(C[a['view']],geo(q,n,np.array(a['xyz']).reshape(-1,3)));uv=np.array(a['observed'])
  if a['kind']=='point':e=qq[0]-uv
  else:
   v=qq[1]-qq[0];nn=np.array([-v[1],v[0]])/np.linalg.norm(v);e=(uv-qq[0])@nn
  ee.extend(e/a['sigma_px'])
 for k,n,uv,sig in contours:ee.extend(dist_to_hull(project(C[k],geo(q,n,cache[n])),uv)/sig)
 for k,uv in [('F',[[258,60],[620,9]]),('G',[[1016,48],[1134,2]])]:
  n='Curtain rail • forward overhead beam';jo=next(o for o in J['objects'] if o['name']==n);p=np.array([jo['points']['bbox_2'],jo['points']['bbox_1']]);qq=project(C[k],geo(q,n,p));v=qq[1]-qq[0];nn=np.array([-v[1],v[0]])/np.linalg.norm(v);ee.extend((np.array(uv)-qq[0])@nn/12)
  target=np.array([254,61] if k=='F' else [1016,46]);ee.extend((qq[0]-target)/15)
 for n in ['Sofa • broad padded arm.001','Sofa • reclined back cushion 2']:
  qq=project(C['F'],O[n]['vertices']);valid=(qq[:,0]>0)&(qq[:,0]<1920);ee.append(max(0,1080-qq[valid,1].min())/18 if valid.any() else 0)
 # Conservative shared sofa separation: all bed-body geometry stays behind sofa's nearest envelope when X overlaps.
 for n in O:
  if n.startswith('Bed') and not any(t in n for t in ['endboard','Bed end']):
   pp=geo(q,n,O[n]['vertices']);ee.append(max(0,pp[:,1].max()+1.415)/.006 if pp[:,0].min()<1.02 else 0)
 if reg:
  ee.extend((q[:12]-q0[:12])/np.tile([.25,.25,.25,1.5,1.5,.8],2));ee.extend(q[18:]/np.array([1.2,.5,.3,.4,.5,.5,.15,.4,.1,.15,.15,.3,.3]))
 return np.array(ee)
if __name__=='__main__':
 fits=[];rng=np.random.default_rng(6112)
 for k in range(3):
  start=np.clip(qinit[free]+(rng.normal(0,.01,len(free)) if k else 0),lo[free]+1e-7,hi[free]-1e-7)
  sol=least_squares(lambda y:res1(full(y)),start,bounds=(lo[free],hi[free]),loss='soft_l1',max_nfev=900,ftol=1e-8,xtol=1e-8,gtol=1e-8);fits.append(sol);print(k,sol.cost,flush=True)
 best=min(fits,key=lambda s:s.cost);q=full(best.x);raw=res1(q,False)
 out={'name':'D2_fixed_H_separate_body_clearance','params':q.tolist(),'lenses':lenses,'cost':best.cost,'data_rms_sigma':float(np.sqrt(np.mean(raw**2))),'max_sigma':float(max(abs(raw))),'cameras':{k:v.tolist() for k,v in unpack(q,lenses).items()},'bound_parameters':[int(free[i]) for i in range(len(free)) if abs(best.x[i]-lo[free][i])<1e-3 or abs(best.x[i]-hi[free][i])<1e-3],'fit_contours':[{'view':k,'object':n,'uv':uv,'sigma_px':sig} for k,n,uv,sig in contours]}
 (R/'joint_fit_d2_result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out,flush=True)
