import numpy as np,math,json
from scipy.optimize import least_squares
from pathlib import Path
R=Path(__file__).resolve().parents[1]
# Pixel annotations refer to the unwarped source video area, x 0..1188, y 26..694.
# Object widths/depth fixed. Poster/bed height revised globally, never per-camera.
pts=[[-1.117,-.278,.87],[1.117,-.278,.87],[-1.145,-2.69,.08],[1.145,-2.69,.08],[0,0,.02],[-.511,-.08,2.28],[.639,-.08,1.274],[1.135,-.86,.6975],[1.805,-.86,.6975]]
pix=[[378,363],[819,363],[335,613],[858,613],[594,516],[494,73],[728,274],[808,405],[953,405]]
def project(p,vs=pts):
 x,y,z,pitch,lens,shift=p;f=lens/36*1188;c=np.array([x,y,z]);fw=np.array([0,math.cos(pitch),-math.sin(pitch)]);rt=np.array([1.,0,0]);up=np.cross(rt,fw);out=[]
 for v in vs:
  q=np.array(v)-c;out.append([594+f*np.dot(q,rt)/np.dot(q,fw),334-f*np.dot(q,up)/np.dot(q,fw)+shift])
 return np.array(out)
# Shift is restrained to 0: ordinary camera, matching by focal length and rigid pose.
def res(v):
 p=[v[0],v[1],v[2],v[3],v[4],0];a=project(p)-pix;return np.r_[a[:7].flatten(),a[7:].flatten()*.25]
r=least_squares(res,[0,-18,2.8,.095,105],bounds=([-.15,-30,1.2,0,60],[.15,-10,4,.3,180]))
p=[*r.x,0];pred=project(p);print(p);print(pred);print(np.sqrt(((pred[:7]-np.array(pix[:7]))**2).sum(axis=1)).tolist());json.dump({'parameters':p,'source_anchors':pix,'projected_anchors':pred.tolist(),'fixed_world_points':pts,'warning':'Sparse manually annotated approximate frontal fit; no side validation; furniture right-cabinet anchors downweighted pending global layout refinement.'},open(R/'analysis/front_camera_fit.json','w'),indent=2)
