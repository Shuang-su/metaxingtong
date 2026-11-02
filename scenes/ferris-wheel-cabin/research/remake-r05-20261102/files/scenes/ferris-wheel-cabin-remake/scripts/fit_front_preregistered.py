import json,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];Q=R/'qa/front-camera-diagnostic';protocol=json.loads((Q/'preregistered-protocol.json').read_text());g=json.loads((Q/'actual-mesh-edges.json').read_text());B=g['baseline_camera'];C=np.array(B['matrix_world']);rv=Rotation.from_matrix(np.diag([1,-1,-1])@C[:3,:3].T).as_rotvec();base=np.r_[B['location'],rv]
def project(points,p,f):
 q=(Rotation.from_rotvec(p[3:]).as_matrix()@(np.array(points)-p[:3]).T).T
 return np.stack([960+f/36*1920*q[:,0]/q[:,2],540+f/36*1920*q[:,1]/q[:,2]],1),q[:,2]
def delta(points,edge):
 a,b=edge;d=b-a;t=np.clip(((np.array(points)-a)@d)/(d@d),0,1);return a+t[:,None]*d-np.array(points)
def evaluate(p,f):
 rows=[];res=[];weighted=[];depth=[]
 for name,edge in g['training_edges_world'].items():
  xy,z=project(edge,p,f);dd=delta(protocol['training_source_subsegments'][name],xy);dist=np.linalg.norm(dd,axis=1);res.extend(dist);weighted.extend((dd/protocol['source_uncertainty_px'][name]).ravel());depth.extend(z);rows.append({'edge':name,'projected_model_finite_edge':xy.tolist(),'depths':z.tolist(),'source_subsegment':protocol['training_source_subsegments'][name],'residual_px':dist.tolist()})
 return {'mean_px':float(np.mean(res)),'max_px':float(np.max(res)),'rows':rows,'min_depth':float(min(depth))},np.r_[weighted,np.maximum(.02-np.array(depth),0)*100]
profiles=[]
for f in protocol['focal_profiles_mm']:
 p=base.copy();p[1]=1.79-(1.79-base[1])*f/27
 fit=least_squares(lambda p:evaluate(p,f)[1],p,loss='soft_l1',f_scale=1,max_nfev=300,xtol=1e-11,ftol=1e-11,gtol=1e-11)
 train,_=evaluate(fit.x,f);sv=np.linalg.svd(fit.jac,compute_uv=False);profiles.append({'lens_mm':f,'pose_camera_position_then_world_to_cv_rotvec':fit.x.tolist(),'training':train,'nfev':fit.nfev,'optimizer_success':bool(fit.success),'jacobian_singular_values':sv.tolist(),'jacobian_rank_relative1e-8':int(sum(sv>sv[0]*1e-8)),'jacobian_raw_condition':float(sv[0]/sv[-1]),'optimizer_message':fit.message})
best=min(x['training']['mean_px'] for x in profiles);eligible=[x for x in profiles if x['training']['mean_px']<=best+.25];selected=next(x for f in [27,20,35] for x in eligible if x['lens_mm']==f);p=np.array(selected['pose_camera_position_then_world_to_cv_rotvec']);f=selected['lens_mm'];baseline=evaluate(base,27)[0];hold=[]
for x in g['heldout_edges']:
 xy,z=project(x['edge_world'],p,f);d=np.linalg.norm(delta(x['source_subsegment'],xy),axis=1);hold.append({**x,'projected_edge':xy.tolist(),'depths':z.tolist(),'residual_px':d.tolist(),'mean_px':float(np.mean(d)),'all_front_facing':bool(np.all(z>0))})
lamp,z=project([g['heldout_lamp']['world']],p,f);lamp_error=float(np.linalg.norm(lamp[0]-g['heldout_lamp']['source']));improved=selected['training']['mean_px']<=baseline['mean_px']*.75 and selected['training']['min_depth']>0
report={'protocol_file':'preregistered-protocol.json','profiles':profiles,'baseline_training':baseline,'selection_rule':protocol['selection'],'selected_lens_mm':f,'selected_pose':p.tolist(),'selected_training':selected['training'],'training_improved_ge25percent':bool(improved),'heldout_not_blind':hold,'lamp':{'projection':lamp[0].tolist(),'source':g['heldout_lamp']['source'],'residual_px':lamp_error,'depth':float(z[0])},'status':'conditional camera candidate eligible' if improved else 'do not adopt camera; retain failed bounded diagnosis','limits':['Single rear plane does not establish focal-distance uniqueness','Outer tan panel-to-model whole leaf identification is a conditional hypothesis, not proved door construction','All source views previously inspected; reserved diagnostics are not blind tests','Heldout fixed-window widths and front configuration may expose incorrect shared geometry; do not use them to reverse-select focal','No geometry changes or image warp, no other camera updates']}
(Q/'fit-report.json').write_text(json.dumps(report,indent=2));im=Image.open(R/'sources/BV18C3d66E17_P1_3844.793761.png').convert('RGB');d=ImageDraw.Draw(im)
for row in selected['training']['rows']:
 d.line([tuple(p) for p in row['source_subsegment']],fill=(0,255,70),width=5);d.line([tuple(p) for p in row['projected_model_finite_edge']],fill=(255,20,20),width=3)
for row in hold:
 d.line([tuple(p) for p in row['source_subsegment']],fill=(0,140,255),width=4)
 if row['all_front_facing']:d.line([tuple(p) for p in row['projected_edge']],fill=(255,0,220),width=3)
d.text((15,15),'GREEN source training / RED model / BLUE reserved source / MAGENTA reserved prediction / NOT scene calibrated',fill='white');im.save(Q/'training-and-reserved-diagnostic.jpg',quality=93)
print(json.dumps({'profiles':[(x['lens_mm'],x['training']['mean_px'],x['jacobian_raw_condition']) for x in profiles],'baseline':baseline['mean_px'],'selected':f,'eligible':bool(improved),'heldout_means':[x['mean_px'] for x in hold],'lamp':lamp_error},indent=2))
