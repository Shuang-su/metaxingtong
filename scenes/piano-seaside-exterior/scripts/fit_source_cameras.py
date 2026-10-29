"""Conditional perspective-only fit to manually identified piano anchors.
No image modification, no per-camera geometry. Pixel picks and 3D correspondence
are hypotheses, not measured calibration. Source occlusions remain untouched.
"""
import json, math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1]
# (label, inferred model coordinate, source pixel, uncertainty px)
anchors={
'N2518':[
 ('far trim end',[-.76,-.014,1.167],[280,88],20),
 ('far cheek low arc',[-.75,-.27,.852],[260,315],35),
 ('far keyboard rear',[-.69,-.069,.812],[462,350],25),
 ('near keyboard rear',[.69,-.069,.812],[1700,632],18),
 ('near keyboard front',[.69,-.423,.812],[1393,825],30),
 ('near cheek low arc',[.780,-.27,.852],[1600,698],25)],
'N6766':[
 ('far cheek nose',[-.780,-.48,.773],[384,935],20),
 ('far cheek upper join',[-.780,.300,1.225],[637,534],25),
 ('far trim outer end',[-.76,-.014,1.167],[565,632],20),
 ('near trim outer end',[.76,-.014,1.167],[1130,337],20),
 ('near cheek nose',[.780,-.48,.773],[820,880],25),
 ('near cheek low arc',[.780,-.27,.852],[1090,780],30),
 ('near cheek upper join',[.780,.300,1.225],[1340,125],20)],
'N2453':[
 ('near rim front',[.78,.22,1.19],[510,435],35),
 ('near rim curve start',[.78,.54,1.19],[550,540],25),
 ('far rim front',[-.78,.22,1.19],[1290,430],50),
 ('tail rim',[-.26,2.40,1.19],[1795,817],40),
 ('front near caster',[.61,.18,.075],[580,1025],25),
 ('music rear top near',[.33,.273,1.57],[755,375],35),
 ('music rear top far',[-.33,.273,1.57],[1200,370],35)],
'N6318':[
 ('hinge front',[-.78,.38,1.21],[870,663],25),
 ('near cheek upper join',[-.780,.184,1.225],[1104,670],20),
 ('near cheek low arc',[-.780,-.27,.852],[1198,849],20),
 ('near cheek nose',[-.780,-.48,.773],[1232,937],30),
 ('near front leg shoulder',[-.61,.18,.68],[1010,963],40),
 ('tail shoulder',[-.31,2.08,.68],[480,910],45),
 ('music upper near',[-.33,.273,1.57],[1053,584],35)],
'N4037':[
 ('hinge front',[-.78,.38,1.21],[875,640],25),
 ('near cheek upper join',[-.780,.184,1.225],[1090,638],25),
 ('near cheek low arc',[-.780,-.27,.852],[1165,784],25),
 ('near cheek nose',[-.780,-.48,.773],[1194,850],20),
 ('near front leg shoulder',[-.61,.18,.68],[938,920],35),
 ('far front caster',[.61,.18,.075],[696,1044],45)]}
initial={'N2518':([1.12,-1.12,1.21],[-.04,-.05,.87],44),'N6766':([1.2,-1.1,.65],[.1,-.05,1.0],35),'N2453':([3.8,4.0,3.3],[-.4,.95,1.0],58),'N6318':([-5.9,-2.1,1.2],[.05,.75,1.55],48),'N4037':([-4.5,1.6,2.1],[-.1,0,1.22],50)}
def unpack(p):
 pos=np.array(p[:3]);yaw,pitch,roll=p[3:6];forward=np.array([math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)])
 right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 rr=right*math.cos(roll)+up*math.sin(roll);uu=up*math.cos(roll)-right*math.sin(roll)
 return pos,forward,rr,uu,math.exp(p[6])
def project(p,pts):
 pos,f,r,u,lens=unpack(p);d=pts-pos;depth=d@f;focal=lens*1920/36
 return np.stack([960+focal*(d@r)/depth,540-focal*(d@u)/depth],axis=1),depth
# One lid angle is jointly estimated with all five rigid perspective cameras.
# Native pixel uncertainty is explicit; geometry other than the common hinge angle
# is frozen. Characters, UI and background are never fit anchors.
lid_pixels={'N6318':[1176,370],'N4037':[644,110],'N2453':[670,0]}
names=list(anchors);initial_params=[]
for name in names:
 pos,target,lens=initial[name];f=np.array(target)-pos;f/=np.linalg.norm(f)
 initial_params.extend([*pos,math.atan2(f[1],f[0]),math.asin(f[2]),0,math.log(lens)])
p0=np.r_[initial_params,math.radians(40)]
lo=[];hi=[]
for i,name in enumerate(names):
 yaw=p0[7*i+3];lo.extend([-20,-20,.1,yaw-1.0,-1.3,-.035,math.log(20)]);hi.extend([20,20,15,yaw+1.0,1.3,.035,math.log(100)])
lo.append(math.radians(25));hi.append(math.radians(65))
def data_for(name,tilt):
 rows=anchors[name];pts=[r[1] for r in rows];pix=[r[2] for r in rows];sigma=[r[3] for r in rows]
 if name in lid_pixels:
  pts=pts+[[-.78+1.56*math.cos(tilt),.38,1.21+1.56*math.sin(tilt)]];pix=pix+[lid_pixels[name]];sigma=sigma+[25]
 return np.array(pts),np.array(pix),np.array(sigma)
def all_residual(params):
 residuals=[]
 for i,name in enumerate(names):
  p=params[7*i:7*i+7];pts,pix,sigma=data_for(name,params[-1]);pred,depth=project(p,pts)
  residuals.extend(((pred-pix)/sigma[:,None]).ravel())
  residuals.extend([p[5]/.012,(30 if name=='N6766' else 3)*(p[6]-p0[7*i+6])])
  residuals.extend(np.minimum(depth-.05,0)*100)
 return residuals
fit=least_squares(all_residual,p0,bounds=(lo,hi),max_nfev=4000,loss='soft_l1')
result={'common_lid_angle_degrees':math.degrees(fit.x[-1]),'method':'joint rigid perspective cameras and one shared hinge angle; fixed body/keyboard/cheek; no image transform','cameras':{}}
for i,name in enumerate(names):
 p=fit.x[7*i:7*i+7];pts,pix,sigma=data_for(name,fit.x[-1]);pred,depth=project(p,pts);pos,f,r,u,lens=unpack(p)
 rows=anchors[name]+([('free lid front',pts[-1].tolist(),pix[-1].tolist(),25)] if name in lid_pixels else [])
 result['cameras'][name]={'location':pos.tolist(),'target':(pos+f).tolist(),'lens_mm':lens,'roll_rad':float(p[5]),'rms_pixels':float(np.sqrt(np.mean((pred-pix)**2))),'anchors':[{'name':row[0],'model_xyz':row[1],'source_xy':row[2],'uncertainty_px':row[3],'projected_xy':pred[j].tolist(),'residual_px':float(np.linalg.norm(pred[j]-pix[j]))} for j,row in enumerate(rows)],'status':'conditional manual correspondence fit; not calibrated; shared fixed geometry'}
 print(name,'rms',round(result['cameras'][name]['rms_pixels'],1),'pos',np.round(pos,3),'lens',round(lens,1),'roll',round(p[5],3))
print('shared lid angle',result['common_lid_angle_degrees'])
(ROOT/'qa/r07/camera-anchor-fit.json').write_text(json.dumps(result,indent=2)+'\n')
