from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def project(points,p):
 c=np.array(p[:3]);yaw,pitch,roll,f=p[3:];forward=np.array([np.sin(yaw)*np.cos(pitch),np.cos(yaw)*np.cos(pitch),np.sin(pitch)]);right=np.array([np.cos(yaw),-np.sin(yaw),0]);up=np.cross(right,forward);rr=right*np.cos(roll)+up*np.sin(roll);uu=up*np.cos(roll)-right*np.sin(roll);q=np.array(points)-c;return np.stack([590+f*(q@rr)/(q@forward),332-f*(q@uu)/(q@forward)],axis=-1)
# Coarse, manually read visible far endpoints of the six lowest tread nose lines. These were NOT geometry-fit targets.
# Soft source imagery, relief/shadow and endpoint ambiguity mean these are diagnostics, not survey points.
views=[('fit_4528','hall_right_arch_4528_paused_core.png','planar_camera_fit_4528.json',[(928,360),(942,342),(959,322),(978,304),(996,286),(1014,268)]),('holdout_4527','holdout_arch_4527_paused_core.png','holdout_camera_4527.json',[(1048,407),(1064,384),(1081,363),(1097,341),(1114,320),(1130,301)])]
pts=[(7.36+k*.33,3.06,(k+1)*.18) for k in range(6)];out={'status':'diagnostic residual, not passed','method':'Manual approximate far-end points of six visible tread noses, +/-5 px observation uncertainty. Shared geometry and camera already frozen; no feedback edits. Perspective projection only; source image unchanged.','geometry_sha256':json.loads((R/'models_frozen_sha256.json').read_text())['CastleHall_Shared_White_Candidate.blend']['sha256'],'world_points':pts,'views':[]}
for name,src,cf,obs in views:
 p=json.loads((R/'qa'/cf).read_text())['parameters'];pred=project(pts,p);err=np.linalg.norm(pred-np.array(obs),axis=1);r={'view':name,'camera':cf,'source':src,'manual_xy':obs,'projected_xy':pred.tolist(),'point_errors_px':err.tolist(),'median_px':float(np.median(err)),'max_px':float(err.max()),'interpretation':'Treads exist in the correct side opening, but their projected levels/endpoints remain displaced. This may include floor/camera/column-scale bias and must not be corrected by lifting the stairs off the common floor.'};out['views'].append(r)
 im=Image.open(R/'inputs'/src).convert('RGB');d=ImageDraw.Draw(im)
 for i,(a,b) in enumerate(zip(obs,pred)):
  a=tuple(a);b=tuple(b);d.line([a,b],fill=(255,220,0),width=2);d.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),outline=(0,255,255),width=2);d.line((b[0]-5,b[1],b[0]+5,b[1]),fill=(255,40,100),width=2);d.line((b[0],b[1]-5,b[0],b[1]+5),fill=(255,40,100),width=2);d.text((a[0]-18,a[1]-10),str(i+1),fill=(0,255,255))
 d.rectangle((4,4,880,40),fill=(20,20,20));d.text((12,11),'Cyan: coarse source observation | Pink: frozen candidate | No image warp',fill='white');im.save(R/'qa'/(name+'_tread_residuals.png'))
(R/'qa/frozen_tread_projection_residuals.json').write_text(json.dumps(out,indent=2));print([(x['view'],x['median_px'],x['max_px']) for x in out['views']])
# Verify pre-render input freeze remains identical.
f=json.loads((R/'inputs_frozen_sha256.json').read_text());bad=[]
for x in f['files']:
 p=Path(x['path']);p=p if p.is_absolute() else R/p
 if hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:bad.append(str(p))
(R/'qa/input_freeze_recheck.json').write_text(json.dumps({'pass':not bad,'changed':bad},indent=2));print('INPUT_RECHECK',bad)
