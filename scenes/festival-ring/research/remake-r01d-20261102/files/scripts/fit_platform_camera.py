import numpy as np,json
from scipy.optimize import least_squares
from pathlib import Path
r=Path(__file__).resolve().parents[1];ang=np.linspace(0,2*np.pi,4096,endpoint=False)
# Silhouette extrema are compared with projected contours, NOT assigned fixed 3D points.
obs={'outer':[[590,1575],[3430,1580],[1990,1915]],'base':[[1298,1405],[2705,1415],[2000,1565]],'top':[[1415,1380],[2580,1380],[2000,1495],[2000,1260]]}
def project(radius,z,p,D):
 el,f,cx,cy,rt,zt,zb,roll=p;x=radius*np.cos(ang);y=radius*np.sin(ang);den=D+y*np.cos(el)-z*np.sin(el);u=f*x/den;v=-f*(y*np.sin(el)+z*np.cos(el))/den;cr=np.cos(roll);sr=np.sin(roll);return np.array([cx+u*cr-v*sr,cy+u*sr+v*cr]).T
def predicted(p,D):
 out=[]
 for tag,rad,z in [('outer',10,0),('base',4.95,p[6]),('top',p[4],p[5])]:
  q=project(rad,z,p,D);inds=[q[:,0].argmin(),q[:,0].argmax(),q[:,1].argmax()];
  if tag=='top':inds+=[q[:,1].argmin()]
  out.extend(q[inds])
 return np.array(out)
y=np.concatenate(list(obs.values()));results=[]
for D in [30,45,70]:
 def res(p):return ((predicted(p,D)-y)/20).ravel()
 opt=least_squares(res,[.22,140*D,2005,1550,4.2,.7,.2,0],bounds=([.08,2000,1800,1300,3.5,.3,.05,-.04],[.6,20000,2200,1800,4.8,1.3,.5,.04]),max_nfev=500)
 results.append({'fixed_camera_distance':D,'params':opt.x.tolist(),'native_pixel_rms':float(np.sqrt(np.mean((predicted(opt.x,D)-y)**2))),'predicted_extrema':predicted(opt.x,D).tolist(),'success':bool(opt.success)})
(r/'qa/platform-camera-conditional-fit.json').write_text(json.dumps({'observations':obs,'uncertainty_px':'15–25 hand selected','param_order':['elevation_rad','focal_px','principal_x','principal_y','top_radius','top_z','base_z','roll_rad'],'circle_azimuth':'unidentifiable from discs; must be conditioned on upper geometry, not unique calibration','base_radius':4.95,'outer_radius':10,'distance_branches':results,'selection':'D30 has lowest training-extrema RMS among three prespecified distance branches; no heldout, all remain ambiguous','scope':'Only platform silhouette hypothesis; no source acceptance/no metric units'},indent=2));print(json.dumps(results,indent=2))
