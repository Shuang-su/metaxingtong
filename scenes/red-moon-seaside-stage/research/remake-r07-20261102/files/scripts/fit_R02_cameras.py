import numpy as np,json,math
from scipy.optimize import least_squares
from pathlib import Path
D=Path(__file__).resolve().parents[1]
# Manual source corner soft annotations, from actual native image visual review.
# World geometry is an explicit conditional working hypothesis, not measured dimensions.
W={'LO':[-5.8,3.57,3.5],'LI':[-4.3,3.57,3.5],'LB':[-5.8,3.57,.04],'LIB':[-4.3,3.57,.04], 'LFo':[-4.7,3.205,3.12],'LFi':[-3.5,3.205,3.12], 'RO':[5.8,3.57,3.5],'RI':[4.3,3.57,3.5],'RB':[5.8,3.57,.04],'RIB':[4.3,3.57,.04], 'RFo':[4.7,3.205,3.12],'RFi':[3.5,3.205,3.12]}
A={
'SOURCE_P1_45':{'wh':[1920,1080],'uncertainty_px':8,'points':{'LO':[130,185],'LI':[338,196],'LB':[149,650],'LFo':[296,247],'LFi':[447,242],'RO':[1659,202],'RI':[1474,207],'RB':[1633,642],'RFo':[1512,255],'RFi':[1372,248]}},
'SOURCE_P2_32':{'wh':[3840,2160],'uncertainty_px':15,'display_scale':1.875,'points':{'LO':[414,285],'LI':[597,294],'LB':[416,729],'LFo':[551,339],'LFi':[678,330],'RI':[1810,235],'RFo':[1867,313],'RFi':[1685,305]}},
'SOURCE_P1_15':{'wh':[1920,1080],'uncertainty_px':8,'points':{'LI':[219,195],'LFo':[156,240],'LFi':[340,239],'RO':[1515,266],'RI':[1352,270],'RB':[1499,659],'RFo':[1395,309],'RFi':[1282,296]}}}
def basis(p):
 yaw,pitch,roll=p[3:6];f=np.array([np.sin(yaw)*np.cos(pitch),np.cos(yaw)*np.cos(pitch),np.sin(pitch)]);r=np.array([np.cos(yaw),-np.sin(yaw),0]);u=np.cross(r,f);return np.cos(roll)*r+np.sin(roll)*u,-np.sin(roll)*r+np.cos(roll)*u,f
def proj(p,world,wh):
 r,u,f=basis(p);q=world-p[:3];z=q@f;return np.column_stack((wh[0]/2+p[6]*wh[0]*(q@r)/z,wh[1]/2-p[6]*wh[0]*(q@u)/z))
R={}
for name,rec in A.items():
 xy=np.array(list(rec['points'].values()))*rec.get('display_scale',1);world=np.array([W[k] for k in rec['points']]);wh=rec['wh']
 rec['points']={k:x.tolist() for k,x in zip(rec['points'],xy)};rec.pop('display_scale',None)
 init=np.array([0,-8.5,3.7,0,-.16,0,.67]);res=least_squares(lambda p:(proj(p,world,wh)-xy).ravel(),init,bounds=([-5,-20,.5,-.65,-.6,-.12,.35],[5,-3,7,.65,.15,.12,1.7]),loss='soft_l1',f_scale=rec['uncertainty_px'],max_nfev=2000)
 errors=np.linalg.norm(proj(res.x,world,wh)-xy,axis=1);r,u,f=basis(res.x)
 R[name]={'parameters':res.x.tolist(),'location':res.x[:3].tolist(),'right':r.tolist(),'up':u.tolist(),'forward':f.tolist(),'lens_mm':res.x[6]*36,'rms_native_px':float(np.sqrt(np.mean(errors**2))),'max_native_px':float(errors.max()),'point_errors_px':dict(zip(rec['points'],errors.tolist())),'status':'conditional camera fit to assumed shared screen geometry; not unique or source accepted'}
(D/'models/R02-camera-soft-anchors.json').write_text(json.dumps({'world_assumption':W,'sources':A,'exclude':'cropped corners, balloon occluded arc endpoints, dynamic frames, actor; screen bottom soft because snow occlusion'},indent=2))
(D/'models/R02-camera-fit.json').write_text(json.dumps(R,indent=2));print(json.dumps(R,indent=2))
