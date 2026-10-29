from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[2];P=R/'c27';j=json.loads((P/'projection_source.json').read_text());name='Window • calibrated vertical mullion.001';ob=j['objects'][name]
# Fixed native image search ROIs chosen from physical edge identity before fit.
spec={'H':('hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',[965,1015,350,750]),'G':('hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png',[335,410,500,800]),'665':('BV1GqXMByE1s_665.501733_downward_native.png',[987,1030,300,420])}
obs={};meta={}
for k,(f,roi) in spec.items():
 im=np.array(Image.open(R/'inputs'/f).convert('RGB'),dtype=float);g=im.mean(2);x0,x1,y0,y1=roi;ys=np.arange(y0,y1);grad=g[ys,x0+1:x1+1]-g[ys,x0-1:x1-1];left=x0+grad.argmin(1);right=x0+grad.argmax(1);fits=[];masks=[]
 for xx in [left,right]:
  coef=np.polyfit(ys,xx,1)
  for _ in range(5):
   keep=np.abs(xx-np.polyval(coef,ys))<2
   coef=np.polyfit(ys[keep],xx[keep],1)
  fits.append(coef.tolist());masks.append(keep)
 y=np.linspace(y0+5,y1-5,24);obs[k]=(y,np.array([np.polyval(fits[0],y),np.polyval(fits[1],y)]).T)
 meta[k]={'source':f,'sha256':hashlib.sha256((R/'inputs'/f).read_bytes()).hexdigest(),'roi':roi,'fits_x_ay_b':fits,'accepted_gradient_rows':[int(x.sum()) for x in masks],'samples_y':y.tolist(),'observed_edges':obs[k][1].tolist(),'usage':'HELDOUT, never used for fitting or parameter selection' if k=='665' else 'FIT'}
v=np.array(ob['world_vertices']);cx=ob['location'][0]
def predict(k,param):
 dx,scale=param;w=v.copy();w[:,0]=cx+(w[:,0]-cx)*scale+dx;z=np.c_[w,np.ones(len(w))]@np.array(j['cameras'][k]['projection']).T;uv=z[:,:2]/z[:,3:4];uv=np.c_[(uv[:,0]+1)*960,(1-uv[:,1])*540]
 hull=uv[ConvexHull(uv).vertices];pts=[]
 for y in obs[k][0]:
  xx=[]
  for a,b in zip(hull,np.roll(hull,-1,axis=0)):
   if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(b[1]-a[1])>1e-9:xx.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
  pts.append([min(xx),max(xx)])
 return np.array(pts)
def residual(p):return np.concatenate([(predict(k,p)-obs[k][1]).ravel() for k in ['H','G']])
fit=least_squares(residual,[0,1],bounds=([-0.12,.5],[.12,2]),xtol=1e-12,ftol=1e-12,gtol=1e-12)
out={'target':name,'parameters':['world_x_translation_scene_units','width_x_scale'],'bounds':[[-.12,.5],[.12,2]],'before':[0,1],'fitted':fit.x.tolist(),'camera_policy':'all original cameras frozen','fit_views':['H','G'],'heldout_view':'665','observations':meta,'results':{},'metric':'absolute native pixel x distance at fixed y to observed silhouette edges; correlated line samples, NOT independent 3D landmarks'}
for k in obs:
 er0=predict(k,[0,1])-obs[k][1];er1=predict(k,fit.x)-obs[k][1]
 out['results'][k]={'before_mean_abs_px':float(np.abs(er0).mean()),'after_mean_abs_px':float(np.abs(er1).mean()),'before_max_abs_px':float(np.abs(er0).max()),'after_max_abs_px':float(np.abs(er1).max()),'before_edges':predict(k,[0,1]).tolist(),'after_edges':predict(k,fit.x).tolist()}
out['decision']='candidate' if all(out['results'][k]['after_mean_abs_px']<out['results'][k]['before_mean_abs_px'] for k in obs) else 'REJECT: one or more views regress'
(P/'mullion_fit.json').write_text(json.dumps(out,indent=2)+'\n')
print('fit',fit.x,'decision',out['decision'])
for k,r in out['results'].items():print(k,{a:b for a,b in r.items() if 'px' in a})
