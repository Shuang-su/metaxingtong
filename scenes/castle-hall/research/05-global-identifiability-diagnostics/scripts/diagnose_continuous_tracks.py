from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];D=R/'inputs/motion_right_to_front_verified';T=json.loads((R/'qa/continuous_architecture_tracks.json').read_text());C=np.array([590.,332.])
def mp(a,p):
 f1,f2=np.exp(p[:2]);q=np.c_[(a-C)/f1,np.ones(len(a))]@Rotation.from_rotvec(p[2:]).as_matrix().T;return C+f2*q[:,:2]/q[:,2:]
def stats(a):return dict(n=len(a),median_px=float(np.median(a)),p90_px=float(np.percentile(a,90)),max_px=float(max(a)))
# Manually reviewed architecture groups. Exclude rear_column_foot (tablecloth corner), low window (balloon-adjacent), and obscured near-foot right side.
allowed=['rear_lamp_high','side_window_high','arch_wall_ornament_high','arch_wall_ornament_low','arch_spring_junction','arch_jamb_foot'];excluded=[7,8,17,18,19,20,21,22,23,24];outs=[]
for ai,bi in [(31,48),(35,48),(42,49),(29,49)]:
 pts=[p for p in T['tracks'] if p['id'] not in excluded and p['xy'][ai] is not None and p['xy'][bi] is not None];a=np.array([p['xy'][ai] for p in pts]);b=np.array([p['xy'][bi] for p in pts]);gr=np.array([p['group'] for p in pts]);w=np.array([1/np.sqrt(sum(gr==g)) for g in gr]);w*=np.sqrt(len(w)/len(set(gr)));runs=[]
 for f in [500,800,1200,1800,2350]:
  sol=least_squares(lambda p:((mp(a,p)-b)*w[:,None]).ravel(),[np.log(f),np.log(f),0,0,0],bounds=([np.log(400),np.log(400),-.65,-.65,-.25],[np.log(2400),np.log(2400),.65,.65,.25]),loss='soft_l1',f_scale=1,max_nfev=800);e=np.linalg.norm(mp(a,sol.x)-b,axis=1);runs.append((float(np.sum(e**2)),sol))
 _,s=min(runs,key=lambda z:z[0]);pred=mp(a,s.x);e=np.linalg.norm(pred-b,axis=1);profile=[]
 for f in [600,800,1000,1400,1900,2350]:
  fit=least_squares(lambda q:((mp(a,np.r_[np.log(f),q])-b)*w[:,None]).ravel(),s.x[1:],bounds=([np.log(400),-.65,-.65,-.25],[np.log(2400),.65,.65,.25]),loss='soft_l1',max_nfev=800);ee=np.linalg.norm(mp(a,np.r_[np.log(f),fit.x])-b,axis=1);profile.append({'f1_pixels':f,'f2_pixels':float(np.exp(fit.x[0])),'residual':stats(ee)})
 out={'frames':[ai,bi],'time_brackets':[T['timestamps'][ai],T['timestamps'][bi]],'point_ids':[p['id'] for p in pts],'n':len(pts),'f1':float(np.exp(s.x[0])),'f2':float(np.exp(s.x[1])),'rotation_vector':s.x[2:].tolist(),'residual':stats(e),'by_group':{g:stats(e[gr==g]) for g in sorted(set(gr))},'focal_profile':profile,'points':[dict(id=p['id'],group=p['group'],source_xy=x.tolist(),target_xy=y.tolist(),predicted_xy=z.tolist(),error_px=float(er)) for p,x,y,z,er in zip(pts,a,b,pred,e)]};outs.append(out);print(ai,bi,out['residual'],'f',out['f1'],out['f2']);print(out['by_group'])
 im=Image.open(D/f'{bi:03}.jpg').crop((0,27,1180,691)).convert('RGB');d=ImageDraw.Draw(im)
 for p,x,y,z,er in zip(pts,a,b,pred,e):
  u,v=y;pu,pv=z;d.ellipse((u-3,v-3,u+3,v+3),outline='lime',width=2);d.line((u,v,pu,pv),fill='red',width=2);d.rectangle((pu-2,pv-2,pu+2,pv+2),outline='red');d.text((u+4,v),str(p['id']),fill='white')
 d.rectangle((0,0,1180,18),fill='black');d.text((5,3),f'{ai:03}->{bi:03} FIXED PP rotation+zoom residuals; green observed / red predicted; NOT accepted camera',fill='white');im.save(R/'qa'/f'continuous_residual_{ai:03}_{bi:03}.jpg',quality=95,subsampling=0)
(R/'qa/continuous_motion_diagnostic.json').write_text(json.dumps({'status':'DIAGNOSTIC_ONLY_NO_GEOMETRY_FIT','fixed_principal_point':[590,332],'model':'K2 R K1^-1, focal bounds400..2400px, squarepixels, no distortion, no translation; equal group contribution, soft_l1','excluded_ids':excluded,'exclusion_reason':'Rear column-foot candidates landed on tablecloth, side-window-low candidates too balloon-adjacent, nearcolumnfoot right side performer/balloon boundary. No props/floor included.','pairs':outs},indent=2))
