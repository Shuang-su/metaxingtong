"""Camera-only robust fit. Fixed shared geometry and fixed explicit door states.
Manual point/line/ellipse annotations are candidate correspondences, not calibration truth.
No image warps, principal-point shift, distortion, person dimensions or per-view geometry.
"""
import numpy as np,json,math,sys
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from pathlib import Path
R=Path(__file__).resolve().parent
G=json.loads((R/'shared_geometry.json').read_text())
A={
 'S01':{'vent_center':[212,753],'vent_rim':[[184,687],[220,700],[254,731],[276,770],[270,802],[241,818],[204,800],[170,765],[150,730],[154,702]],'dash_top_corner':[265,606],'dash_bottom_corner':[273,632],'a_foot':[181,575],'a_inner_edge':[[300,494],[500,386],[780,275]],'door_belt_line':[[460,562],[800,556],[1500,542],[1660,538]],'roof_lower_line':[[1420,199],[1750,211]],'mirror_center':[601,470]},
 'S02':{'vent_center':[248,802],'vent_rim':[[215,728],[251,741],[283,778],[307,819],[307,854],[279,872],[242,853],[208,819],[188,780],[188,747]],'dash_top_corner':[299,649],'dash_bottom_corner':[302,680],'a_foot':[196,620],'a_inner_edge':[[330,540],[530,426],[780,315]],'door_belt_line':[[620,568],[930,507]],'roof_lower_line':None,'mirror_center':None},
 'S03':{'vent_center':[365,685],'vent_rim':[[333,629],[364,638],[396,668],[415,699],[414,726],[389,742],[357,728],[327,700],[313,668],[316,642]],'dash_top_corner':[406,558],'dash_bottom_corner':[418,585],'a_foot':[337,532],'a_inner_edge':[[470,446],[680,333],[905,253]],'door_belt_line':[[550,529],[800,526],[1460,518],[1685,514]],'roof_lower_line':[[1400,192],[1750,203]],'mirror_center':[699,447]}}
SIGMA={'vent_center':7,'vent_rim':7,'dash_top_corner':10,'dash_bottom_corner':10,'a_foot':15,'a_inner_edge':12,'door_belt_line':9}
TRAIN=list(SIGMA)
(R/'source_annotations.json').write_text(json.dumps({'method':'Manual native-coordinate picks from actual four PNGs; inspection grids/crops are labeled derivatives. Ellipse samples are outer rim estimates in compressed/chromatic source. Lines are observed segments with unknown pointwise parameterization. Person excluded.','uncertainty_pixels':SIGMA,'training_features':TRAIN,'held_out_features':['roof_lower_line','mirror_center'],'views':A},indent=2)+'\n')
def project(p,xyz):
 C=np.asarray(p[:3]);yaw,pitch,roll=p[3:6];f=np.array([math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)])
 right=np.array([math.sin(yaw),-math.cos(yaw),0]);up=np.cross(right,f)
 r=right*math.cos(roll)+up*math.sin(roll);u=-right*math.sin(roll)+up*math.cos(roll)
 d=np.asarray(xyz)-C;z=d@f;fx=1920*p[6]/36
 return np.stack([960+(d@r)*fx/np.maximum(z,.03),540-(d@u)*fx/np.maximum(z,.03)],axis=-1)
def ellipse_fit(pts):
 pts=np.asarray(pts);center=pts.mean(0);cov=np.cov(pts.T);w,v=np.linalg.eigh(cov);order=np.argsort(w)[::-1];axes=(2*w[order])**.5;angle=math.atan2(v[1,order[0]],v[0,order[0]])
 def er(p):
  c,s=np.cos(p[4]),np.sin(p[4]);q=(pts-p[:2])@np.array([[c,-s],[s,c]]);return ((q[:,0]/p[2])**2+(q[:,1]/p[3])**2-1)*min(p[2:4])/2
 result=least_squares(er,[*center,*axes,angle],bounds=([-2000,-2000,1,1,-10],[4000,4000,1000,1000,10]))
 return result.x
ELL={id:ellipse_fit(a['vent_rim']) for id,a in A.items()}
def signed_ellipse_distance(points,e):
 c,s=np.cos(e[4]),np.sin(e[4]);q=(points-e[:2])@np.array([[c,-s],[s,c]])
 rho=np.sqrt((q[:,0]/e[2])**2+(q[:,1]/e[3])**2)
 radial_length=np.linalg.norm(q,axis=1)
 return (rho-1)*radial_length/np.maximum(rho,.001)
def feature_residual(p,id,name):
 geo=G['states'][str(G['cameras'][id]['state'])];obs=A[id][name];pr=project(p,geo[name])
 if name=='vent_rim':return signed_ellipse_distance(pr[::10],ELL[id])
 if name.endswith('_line') or name=='a_inner_edge':
  # Finite projected support matters: an infinite fitted line can match while
  # the physical door ends halfway across the source image.
  a,b=pr;d=b-a;obs=np.asarray(obs);t=np.clip(((obs-a)@d)/(d@d),0,1)
  return np.ravel(a+t[:,None]*d-obs)
 return pr-np.asarray(obs)
def residual(p,id,active=TRAIN):
 out=[]
 for name in active:
  v=np.ravel(feature_residual(p,id,name));v=v/SIGMA[name]
  # One rim/line is one evidence group, not 16 new independent anchors.
  if len(v)>2:v=v*np.sqrt(2/len(v))
  out.extend(v)
 return np.asarray(out)
def summary(p,id):
 rows={}
 for name,obs in A[id].items():
  if obs is None:continue
  rr=np.ravel(feature_residual(p,id,name));rows[name]={'rms_pixels':float(np.sqrt(np.mean(rr*rr))),'max_abs_pixels':float(abs(rr).max()),'residual_components_pixels':rr.tolist(),'role':'fit' if name in TRAIN else 'held-out'}
 return rows
if __name__=='__main__':
 lo=[-3.5,-1.7,.60,-1.1,-.55,-.20,14];hi=[.50,1.40,1.95,1.1,.55,.20,70]
 rng=np.random.default_rng(73);results={}
 for id,c in G['cameras'].items():
  p0=np.array(c['position']+c['yaw_pitch_roll']+[c['lens']]);trials=[]
  for k in range(18):
   seed=p0 if k==0 else np.clip(p0+rng.normal(0,[.3,.25,.14,.15,.10,.03,5]),np.array(lo)+1e-6,np.array(hi)-1e-6)
   fit=least_squares(residual,seed,args=(id,),bounds=(lo,hi),loss='linear' if '--balanced' in sys.argv else 'soft_l1',f_scale=1.5,max_nfev=1800,xtol=1e-10,ftol=1e-10,gtol=1e-10)
   trials.append(fit)
  best=min(trials,key=lambda x:x.cost);p=best.x
  # Holdout tests above are never used by the optimizer.
  results[id]={'initial_camera':p0.tolist(),'fitted_camera':p.tolist(),'parameter_order':['x','y','z','yaw_radians','pitch_radians','roll_radians','lens_mm'],'door_state':c['state'],'geometry_changed':False,'initial_features':summary(p0,id),'fitted_features':summary(p,id),'normalized_rms_before':float(np.sqrt(np.mean(residual(p0,id)**2))),'normalized_rms_after':float(np.sqrt(np.mean(residual(p,id)**2))),'cost':float(best.cost),'multistart_count':len(trials),'bounds_active':np.where(np.isclose(p,lo,atol=.002)|np.isclose(p,hi,atol=.002))[0].tolist(),'ellipse_manual_fit':ELL[id].tolist()}
 (R/'camera_only_fit.json').write_text(json.dumps({'geometry_sha256':G['geometry_vertex_topology_sha256'],'loss':'linear group-balanced least squares' if '--balanced' in sys.argv else 'soft_l1','scope':'Camera position, focal length and orientation only. Fixed principal point/sensor, no warp or distortion. Hard anchors are candidate mesh correspondences, not proof of identity.','results':results},indent=2)+'\n')
 for id,v in results.items():print(id,'camera',np.round(v['fitted_camera'],3),'normalized',round(v['normalized_rms_before'],2),'->',round(v['normalized_rms_after'],2),'features',{n:round(r['rms_pixels'],1) for n,r in v['fitted_features'].items()})
