from pathlib import Path
import numpy as np,json,math
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];V=R.parent/'castlehall_hd_verification_20261010'
# Manual image observations with explicit uncertainty. Centers refer to shaft/base contact, not all-image scoring.
obs={
 'fit_4528':dict(source='hall_right_arch_4528_paused_core.png',columns={2:[477,331,432,525],3:[270,297,240,300],4:[140,292,106,179]},lamp=[46,99],near_left=1098),
 'fit_4529':dict(source='hall_right_arch_4529_natural_ui_clear_core.png',columns={2:[609,346,561,659],3:[382,313,351,417],4:[284,309,255,315]},lamp=[245,118],near_left=None),
}
def matrix(p):
 cx,cy,cz,yaw,pitch,roll,f=p
 forward=np.array([math.sin(yaw)*math.cos(pitch), math.cos(yaw)*math.cos(pitch),math.sin(pitch)])
 right=np.array([math.cos(yaw),-math.sin(yaw),0.]);up=np.cross(right,forward)
 rr=right*math.cos(roll)+up*math.sin(roll);uu=-right*math.sin(roll)+up*math.cos(roll)
 return np.array([rr,uu,forward]),np.array([cx,cy,cz]),f

def project(x,p):
 M,C,f=matrix(p);v=(np.array(x)-C)@M.T;return np.stack((590+f*v[...,0]/v[...,2],332-f*v[...,1]/v[...,2]),axis=-1)
def col(j,p):
 a=np.arange(192)/192*2*math.pi;pts=np.stack((4.25+.54*np.cos(a),(j-1)*6+.54*np.sin(a),np.ones_like(a)*.51),axis=-1)
 uv=project(pts,p);cent=project([[4.25,(j-1)*6,.51]],p)[0]
 return [cent[0],cent[1],uv[:,0].min(),uv[:,0].max()]

def residual(p,ob):
 r=[]
 for j,uv in ob['columns'].items():
  pr=col(j,p)
  # Current column widths/count are approximate; give transverse geometry weak weight.
  r.extend([(pr[0]-uv[0])/7,(pr[1]-uv[1])/10,(pr[2]-uv[2])/18,(pr[3]-uv[3])/18])
 lamp=project([[4.8,21.5,4.6]],p)[0];r.extend((lamp-np.array(ob['lamp']))/12)
 if ob['near_left'] is not None:r.append((col(1,p)[2]-ob['near_left'])/18)
 r.extend([(p[2]-1.3)/.6,p[4]/.15,p[5]/.03,(p[-1]-1000)/800])
 return r
out={}
for key,ob in obs.items():
 results=[]
 for x in [-2,0,2]:
  for y in [-9,-5,-2]:
   p=[x,y,1.3,.5,-.03,0,1000]
   sol=least_squares(residual,p,args=(ob,),bounds=([-5,-14,.5,0,-.25,-.05,450],[5,-.4,3.3,1.4,.25,.05,1800]),max_nfev=600)
   results.append(sol)
 sol=min(results,key=lambda x:sum(x.fun*x.fun));p=sol.x;M,C,f=matrix(p)
 out[key]={'source':ob['source'],'parameters':p.tolist(),'location':C.tolist(),'right':M[0].tolist(),'up':M[1].tolist(),'forward':M[2].tolist(),'focal_pixels':float(f),'lens_mm':float(f*36/1180),'cost':float(sum(sol.fun*sol.fun)),'manual_observations':ob,'projected_columns':{str(j):col(j,p) for j in ob['columns']},'projected_lamp':project([[4.8,21.5,4.6]],p)[0].tolist()}
 im=Image.open(V/'references'/ob['source']).convert('RGB');d=ImageDraw.Draw(im)
 for j,uv in ob['columns'].items():
  pr=col(j,p);d.ellipse((uv[0]-5,uv[1]-5,uv[0]+5,uv[1]+5),outline='cyan',width=2);d.ellipse((pr[0]-5,pr[1]-5,pr[0]+5,pr[1]+5),outline='red',width=2);d.line((pr[2],pr[1],pr[3],pr[1]),fill='red',width=2);d.text((pr[0],pr[1]+6),f'R{j}',fill='red')
 uv=out[key]['projected_lamp'];d.ellipse((uv[0]-5,uv[1]-5,uv[0]+5,uv[1]+5),outline='red',width=2)
 im.save(R/'qa'/f'{key}_manual_alignment.jpg',quality=94)
 print(key,json.dumps(out[key],indent=2))
(R/'qa/source_camera_fits.json').write_text(json.dumps(out,indent=2))
