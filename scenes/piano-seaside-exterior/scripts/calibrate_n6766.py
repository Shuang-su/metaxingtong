"""Bounded N6766 camera experiment. Fixed R07 piano, no geometry parameter."""
from pathlib import Path
import numpy as np,json,math
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/r08'
def bez(t):
 a=np.array([.184,1.225]);b=np.array([.184,.970]);c=np.array([.025,.852]);d=np.array([-.270,.852]);return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
# All manual contour correspondences are hypotheses with explicit px uncertainty.
rows=[('near cheek top',[.780,.184,1.225],[1340,125],18),('near curve t=.2',[.780,*bez(.2)],[1370,420],30),('near curve t=.4',[.780,*bez(.4)],[1335,590],30),('near curve t=.6',[.780,*bez(.6)],[1255,710],30),('near curve t=.8',[.780,*bez(.8)],[1155,765],30),('near curve low',[.780,-.270,.852],[1060,788],22),('near cheek nose',[.780,-.480,.773],[820,880],25),('far cheek nose',[-.780,-.480,.773],[384,935],35),('trim near front corner',[.760,-.0145,1.1815],[1135,335],40),('trim far front corner',[-.760,-.0145,1.1815],[568,632],40)]
pts=np.array([r[1] for r in rows]);pix=np.array([r[2] for r in rows]);sigma=np.array([r[3] for r in rows])
def unpack(p):
 pos=p[:3];yaw,pitch,roll=p[3:6];f=np.array([math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)]);r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f);return pos,f,r*math.cos(roll)+u*math.sin(roll),u*math.cos(roll)-r*math.sin(roll),math.exp(p[6])
def proj(p,points=pts):
 pos,f,r,u,lens=unpack(p);d=points-pos;dep=d@f
 return np.stack([960+(lens*1920/36)*(d@r)/dep,540-(lens*1920/36)*(d@u)/dep],1),dep
candidates=[]
for weight in [.25,.5,1,2]:
 best=None
 for pos in [[1.05,-.7,.75],[1.3,-.5,.8],[1.5,-.9,.75],[.95,-.9,.65]]:
  f=np.array([.50,-.10,1.02])-pos;f/=np.linalg.norm(f);p0=[*pos,math.atan2(f[1],f[0]),math.asin(f[2]),0,math.log(35)]
  def residual(p):
   xy,dep=proj(p);res=(xy-pix)/sigma[:,None];res[7:]*=weight
   return np.r_[res.ravel(),p[5]/.015,np.minimum(dep-.04,0)*100]
  fit=least_squares(residual,p0,bounds=([.805,-2,.3,1.7,-.2,-.04,math.log(12)],[3,-.05,1.4,3.13,1.0,.04,math.log(100)]),loss='soft_l1',max_nfev=1500)
  if best is None or fit.cost<best.cost:best=fit
 p=best.x;xy,dep=proj(p);pos,f,r,u,lens=unpack(p)
 candidates.append({'id':f'contour_weight_{weight:g}','location':pos.tolist(),'target':(pos+f).tolist(),'lens_mm':lens,'roll_rad':float(p[5]),'near_curve_rms_pixels':float(np.sqrt(np.mean((xy[:7]-pix[:7])**2))),'all_anchor_rms_pixels':float(np.sqrt(np.mean((xy-pix)**2))),'anchors':[{'name':r[0],'model_xyz':r[1],'source_xy':r[2],'uncertainty_px':r[3],'projection_xy':xy[i].tolist()} for i,r in enumerate(rows)]})
 print(candidates[-1]['id'],np.round(pos,3),'lens',round(lens,2),'near rms',round(candidates[-1]['near_curve_rms_pixels'],1),'all rms',round(candidates[-1]['all_anchor_rms_pixels'],1))
# Deliberate close-view candidates avoid treating doubtful point fits as calibration truth.
for i,(pos,target,lens) in enumerate([((1.12,-.75,.78),(.45,-.08,1.01),35),((1.05,-.75,.78),(.45,-.08,1.01),28),((1.30,-.65,.80),(.45,-.10,1.02),35),((1.20,-.65,.80),(.45,-.10,1.02),28)]):
 candidates.append({'id':f'manual_close_{i}','location':pos,'target':target,'lens_mm':lens,'roll_rad':0,'status':'manual framing diagnostic, fixed R07 geometry'})
(OUT/'camera-initial-fit-rerun.json').write_text(json.dumps({'status':'low-sample framing experiments; no independent calibration ground truth','candidates':candidates},indent=2)+'\n')
