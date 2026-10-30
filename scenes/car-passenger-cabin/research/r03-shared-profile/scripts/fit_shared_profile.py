"""Bounded shared profile trial; no new bounds after seeing an optimum.
Five dashboard/vent parameters + two small orientation corrections per source.
Then freeze cameras/profile and fit at most two shared A-pillar parameters.
Only source annotations from r02 are read. Mirror, roof and door belt are held out.
"""
import json,math,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];S=R.parents[1];OLD=S/'research/r02-camera-calibration'
G=json.loads((OLD/'shared_geometry.json').read_text());ANN=json.loads((OLD/'source_annotations.json').read_text());A=ANN['views'];IDS=['S01','S02','S03']
def project(p,xyz):
 C=np.asarray(p[:3]);yaw,pitch,roll=p[3:6];f=np.array([np.cos(pitch)*np.cos(yaw),np.cos(pitch)*np.sin(yaw),np.sin(pitch)]);right=np.array([np.sin(yaw),-np.cos(yaw),0]);up=np.cross(right,f);rr=right*np.cos(roll)+up*np.sin(roll);uu=-right*np.sin(roll)+up*np.cos(roll);d=np.asarray(xyz)-C;z=d@f;fx=1920*p[6]/36
 return np.stack([960+(d@rr)*fx/np.maximum(z,.03),540-(d@uu)*fx/np.maximum(z,.03)],axis=-1)
def ellipse(pts):
 pts=np.asarray(pts);center=pts.mean(0);w,v=np.linalg.eigh(np.cov(pts.T));order=np.argsort(w)[::-1];ax=np.sqrt(2*w[order]);a=np.arctan2(v[1,order[0]],v[0,order[0]])
 def er(p):
  c,s=np.cos(p[4]),np.sin(p[4]);q=(pts-p[:2])@np.array([[c,-s],[s,c]]);return ((q[:,0]/p[2])**2+(q[:,1]/p[3])**2-1)*min(p[2:4])/2
 return least_squares(er,[*center,*ax,a],bounds=([-2000,-2000,1,1,-10],[4000,4000,1000,1000,10])).x
ELL={id:ellipse(A[id]['vent_rim']) for id in IDS}
def radial(pts,e):
 c,s=np.cos(e[4]),np.sin(e[4]);q=(pts-e[:2])@np.array([[c,-s],[s,c]]);rho=np.sqrt((q[:,0]/e[2])**2+(q[:,1]/e[3])**2);return (rho-1)*np.linalg.norm(q,axis=1)/np.maximum(rho,.001)
CAM={id:np.array(G['cameras'][id]['position']+G['cameras'][id]['yaw_pitch_roll']+[G['cameras'][id]['lens']]) for id in IDS}
# Shared profile parameters: front-edge delta Y, tilt X, top thickness, vent radius multiplier, vent local height delta.
P0=np.array([0,0,.095,1,0.]);LO=np.array([-.04,np.radians(-35),.035,.65,-.03]);HI=np.array([.20,np.radians(10),.095,1.05,.12])
def profile_points(p):
 dy,tilt,thick,scale,h=p;f=.637+dy;top=1.0325;fas_top=top-thick+.0025;co,si=np.cos(tilt),np.sin(tilt);rot=np.array([[1,0,0],[0,co,-si],[0,si,co]])
 def tr(xyz):return (np.asarray(xyz)-[0,.637,.94])@rot.T+[0,f,fas_top]
 center=np.array([.8,.6135,.77+h]);angles=np.linspace(0,2*np.pi,64,endpoint=False);circle=np.stack([.8+.117*scale*np.cos(angles),np.full(64,.6135),.77+h+.117*scale*np.sin(angles)],axis=1)
 br=min(.045,thick*.49)
 return {'vent_center':tr(center),'vent_rim':tr(circle),'dash_top_corner':np.array([1.03-.521787*br,f-.007+.521787*br,top-.263367*br]),'dash_bottom_corner':np.array([1.03-.521787*br,f-.007+.521787*br,top-thick+.263367*br])}
def a_points(p):
 dy,bulge=p;foot_y=.93+(.23-.93)*(1.0325-.97)/(1.66-.97)+dy;t=np.linspace(0,1,65);y=(1-t)*foot_y+t*.23+4*bulge*t*(1-t);z=1.0325+t*(1.66-1.0325)
 return {'a_foot':np.array([.87,foot_y,1.0325]),'a_inner_edge':np.stack([np.full(len(t),.87),y,z],axis=1)}
def polyline_resid(pr,obs):
 obs=np.asarray(obs);a=pr[:-1];d=pr[1:]-a;dd=np.sum(d*d,axis=1);t=np.clip(np.sum((obs[:,None,:]-a[None,:,:])*d[None,:,:],axis=2)/dd,0,1);near=a[None,:,:]+t[:,:,None]*d[None,:,:];res=near-obs[:,None,:];which=np.argmin(np.sum(res*res,axis=2),axis=1);return res[np.arange(len(obs)),which].ravel()
def feat(camera,id,points,name):
 pr=project(camera,points[name]);obs=A[id][name]
 if name=='vent_rim':return radial(pr[::4],ELL[id])
 if name.endswith('line') or name=='a_inner_edge':return polyline_resid(pr,obs)
 return (pr-obs).ravel()
TRAIN_D=['vent_center','vent_rim','dash_top_corner','dash_bottom_corner'];TRAIN_A=['a_foot','a_inner_edge'];HOLD=['mirror_center','roof_lower_line','door_belt_line']
def normalized(v,sigma):v=np.asarray(v);return v/sigma*np.sqrt(2/max(len(v),2))
def get_cameras(x):
 out={}
 for i,id in enumerate(IDS):
  p=CAM[id].copy();p[3]+=x[5+i*2];p[4]+=x[6+i*2];out[id]=p
 return out
def dash_resid(x,selected=IDS,freeze=None):
 pts=profile_points(x[:5]);cams=get_cameras(x) if freeze is None else freeze;out=[]
 for id in selected:
  for name in TRAIN_D:out.extend(normalized(feat(cams[id],id,pts,name),7 if name.startswith('vent') else 10))
 if freeze is None:
  # Weak orientation prior, not a license to change principal point or perspective scale.
  for j in range(6):out.append(x[5+j]/(.04 if j%2==0 else .03)*.35)
 return out
def all_features(camera,id,p,a):
 pts=profile_points(p);pts.update(a_points(a));base=G['states'][str(G['cameras'][id]['state'])]
 for n in HOLD:pts[n]=base[n]
 rows={}
 for name in TRAIN_D+TRAIN_A+HOLD:
  if A[id].get(name) is None:continue
  res=np.asarray(feat(camera,id,pts,name));rows[name]={'residual_components':res.tolist(),'rms_px':float(np.sqrt(np.mean(res**2))),'euclidean_px':float(np.linalg.norm(res)) if len(res)==2 else None,'role':'fit_dashboard' if name in TRAIN_D else 'fit_A' if name in TRAIN_A else 'held_out'}
 return rows
if __name__=='__main__':
 rng=np.random.default_rng(109);lo=np.r_[LO,[-.10,-.06]*3];hi=np.r_[HI,[.10,.06]*3];fits=[]
 for i in range(8):
  seed=np.r_[P0,[0.]*6] if i==0 else np.r_[np.array([.10,np.radians(-18),.06,.80,.04])+rng.normal(0,[.03,.1,.008,.06,.02]),rng.normal(0,.02,6)]
  seed=np.clip(seed,lo+1e-8,hi-1e-8);fits.append(least_squares(dash_resid,seed,bounds=(lo,hi),max_nfev=500,ftol=1e-8,xtol=1e-8,gtol=1e-8))
 best=min(fits,key=lambda x:x.cost);x=best.x;cams=get_cameras(x);p=x[:5]
 # Geometry-only leave-one-view-out sensitivity, with all cameras frozen after above fit.
 sens=[]
 for excluded in IDS:
  keep=[v for v in IDS if v!=excluded];res=least_squares(lambda q:dash_resid(q,keep,cams),p,bounds=(LO,HI),max_nfev=500)
  sens.append({'excluded':excluded,'geometry_parameters':res.x.tolist(),'bounds_active':np.flatnonzero(np.isclose(res.x,LO,atol=.001)|np.isclose(res.x,HI,atol=.001)).tolist(),'held_view_features':all_features(cams[excluded],excluded,res.x,[0,0])})
 def ar(q):
  pts=a_points(q);out=[]
  for id in IDS:
   for n in TRAIN_A:out.extend(normalized(feat(cams[id],id,pts,n),15 if n=='a_foot' else 12))
  return out
 alo=[-.18,-.10];ahi=[.06,.10];afits=[least_squares(ar,start,bounds=(alo,ahi),max_nfev=400) for start in [[0,0],[-.08,.04],[.04,-.04]]];abest=min(afits,key=lambda y:y.cost);ap=abest.x
 rows={}
 for id in IDS:rows[id]={'camera':cams[id].tolist(),'original_camera':CAM[id].tolist(),'state':G['cameras'][id]['state'],'baseline_original_cameras':all_features(CAM[id],id,P0,[0,0]),'baseline_frozen_r03_cameras':all_features(cams[id],id,P0,[0,0]),'D1_dashboard_profile':all_features(cams[id],id,p,[0,0]),'D2_profile_and_A':all_features(cams[id],id,p,ap)}
 result={'scope':'Shared bounded parametric proxy fit, followed by actual Blender rebuild and pixel/visibility checks; not acceptance','dashboard_parameter_names':['front_edge_delta_y','fascia_tilt_X_radians','top_thickness','vent_radius_factor','vent_height_delta_local'],'dashboard_baseline':P0.tolist(),'dashboard_parameters':p.tolist(),'dashboard_bounds':[LO.tolist(),HI.tolist()],'dashboard_bounds_active':np.flatnonzero(np.isclose(p,LO,atol=.001)|np.isclose(p,HI,atol=.001)).tolist(),'camera_orientation_deltas':x[5:].tolist(),'camera_delta_bounds_active':np.flatnonzero(np.isclose(x[5:],lo[5:],atol=.001)|np.isclose(x[5:],hi[5:],atol=.001)).tolist(),'A_parameter_names':['lower_joint_delta_y','single_y_bulge'],'A_parameters':ap.tolist(),'A_bounds':[alo,ahi],'A_bounds_active':np.flatnonzero(np.isclose(ap,alo,atol=.001)|np.isclose(ap,ahi,atol=.001)).tolist(),'fit_features':TRAIN_D+TRAIN_A,'held_out_features':HOLD,'leave_one_view_out_geometry_sensitivity':sens,'results':rows,'stop_rule':'Any boundary hit or cross-view/heldout degradation is diagnostic; do not widen bounds. Preserve physical trials as not accepted.'}
 (R/'fit_result.json').write_text(json.dumps(result,indent=2)+'\n')
 print('DASH',p,'ACTIVE',result['dashboard_bounds_active'],'CAMERA_ACTIVE',result['camera_delta_bounds_active']);print('A',ap,'ACTIVE',result['A_bounds_active'])
 for id,row in rows.items():print(id,{n:round(v['rms_px'],1) for n,v in row['D2_profile_and_A'].items()})
