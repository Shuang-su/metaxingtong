import json,numpy as np
from scipy.optimize import least_squares,minimize_scalar
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=json.loads((P/'qa/camera_fit.json').read_text());K=F['k']
# same projection and ray basis as shared Blender geometry
exec((P/'scripts/fit_cameras.py').read_text().split('order=')[0])
def ray(key,uv):
 c=F['cameras'][key]['params'];x,y,z,tx,tz,f,roll=c;pos=np.array([x,y,z]);fw=np.array([tx,3,tz])-pos;fw/=np.linalg.norm(fw);rt=np.cross(fw,[0,0,1]);rt/=np.linalg.norm(rt);up=np.cross(rt,fw);u=(uv[0]-590)/f;v=(331.5-uv[1])/f;co,si=np.cos(roll),np.sin(roll);u,v=co*u+si*v,-si*u+co*v;return pos,fw+u*rt+v*up
obs={'顶部簇':{'C':[555,56],'A':[795,68],'B':[199,42]},'上左':{'C':[482,118],'A':[724,132],'B':[132,109]},'上右':{'C':[641,118],'A':[875,141],'B':[303,113]},'左白':{'C':[321,225],'A':[547,263]},'右上簇':{'C':[721,156],'A':[956,166],'B':[391,143]},'左外':{'C':[246,218],'A':[471,264]},'中低簇':{'C':[559,362],'A':[822,389],'B':[177,363]}}
res={}
for n,ob in obs.items():
 pos,rr=ray('C',ob['C'])
 def point(t):return pos+t*rr
 def residual(t):
  p=point(t[0]);out=[]
  for key,uv in ob.items():
   if key=='C':continue
   out.extend(proj(p[None,:],F['cameras'][key]['params'])[0]-uv)
  return out
 fit=least_squares(residual,[8],bounds=([5],[13]),loss='soft_l1',f_scale=10)
 pp=point(fit.x[0]);res[n]={'point':pp.tolist(),'observations':ob,'residuals_px':residual(fit.x)}
# Fit the single shared floor ball from three independent views. Sources may be occluded; retain residuals.
ballobs={'A':[1117,603],'B':[846,493],'C':[1030,548]}
def br(p):
 xyz=np.array([[p[0],p[1],.16+p[2]]]);out=[]
 for key,uv in ballobs.items():out.extend(proj(xyz,F['cameras'][key]['params'])[0]-uv)
 return out
b=least_squares(br,[2.5,-3.5,.3],bounds=([0,-6,.15],[5,1,.65]),loss='soft_l1',f_scale=15)
result={'lamps':res,'ball':{'xyz':[b.x[0],b.x[1],.16+b.x[2]],'radius':b.x[2],'residuals_px':br(b.x),'observations':ballobs}}
(P/'qa/shared_prop_fit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
