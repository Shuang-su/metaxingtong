from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];D=json.loads((R/'qa/continuous_motion_refined_diagnostic.json').read_text())
def fit(a,b):
 def norm(x):
  c=x.mean(0);s=2**.5/np.mean(np.linalg.norm(x-c,axis=1));T=np.array([[s,0,-s*c[0]],[0,s,-s*c[1]],[0,0,1]]);return (np.c_[x,np.ones(len(x))]@T.T)[:,:2],T
 x,T=norm(a);y,U=norm(b);A=[]
 for (xx,yy),(u,v) in zip(x,y):A.extend([[-xx,-yy,-1,0,0,0,u*xx,u*yy,u],[0,0,0,-xx,-yy,-1,v*xx,v*yy,v]])
 _,_,vt=np.linalg.svd(A);H=np.linalg.inv(U)@vt[-1].reshape(3,3)@T;H/=H[2,2];return H

def mp(a,H):
 q=np.c_[a,np.ones(len(a))]@H.T;return q[:,:2]/q[:,2:]
def st(e):return {'n':len(e),'median_px':float(np.median(e)),'p90_px':float(np.percentile(e,90)),'max_px':float(max(e))}
outs=[]
for pair in D['pairs']:
 pts=pair['points'];a=np.array([q['source_xy'] for q in pts]);b=np.array([q['target_xy'] for q in pts]);gr=np.array([q['group'] for q in pts]);s=np.array([q['group'] in ['arch_wall_ornament_high','arch_wall_ornament_low','arch_spring_junction','arch_jamb_foot'] for q in pts]);H=fit(a[s],b[s]);e=np.linalg.norm(mp(a,H)-b,axis=1);allH=fit(a,b);allerr=np.linalg.norm(mp(a,allH)-b,axis=1);out={'frames':pair['frames'],'training_groups':['arch_wall_ornament_high','arch_wall_ornament_low','arch_spring_junction','arch_jamb_foot'],'train_residual':st(e[s]),'by_group':{g:st(e[gr==g]) for g in sorted(set(gr))},'arch_plane_H':H.tolist(),'all_point_H_residual':st(allerr),'all_point_H_by_group':{g:st(allerr[gr==g])for g in sorted(set(gr))},'predictions':[dict(q,arch_plane_prediction=z.tolist(),arch_plane_error=float(er))for q,z,er in zip(pts,mp(a,H),e)]}
 nearest=np.flatnonzero(gr=='nearest_column_square_plinth')
 if len(nearest):
  rng=np.random.default_rng(712);pred=[]
  for _ in range(400):
   hh=fit(a[s]+rng.normal(0,1,a[s].shape),b[s]+rng.normal(0,1,b[s].shape));pred.append(mp(a[nearest],hh)[0])
  pred=np.array(pred);out['nearest_prediction_under_1px_input_jitter']={'n':400,'mean_xy':pred.mean(0).tolist(),'std_xy':pred.std(0).tolist(),'radial_p95_from_mean_px':float(np.percentile(np.linalg.norm(pred-pred.mean(0),axis=1),95)),'meaning':'numerical sensitivity under assumed1px independent Gaussian coordinate perturbation; NOT statistical real-world confidence interval'}
 outs.append(out);print(pair['frames'],out['train_residual'],out['by_group'].get('nearest_column_square_plinth'),'allH',out['all_point_H_residual'])
(R/'qa/plane_transfer_diagnostic.json').write_text(json.dumps({'status':'POINT_MAPPING_ONLY_NO_IMAGE_WARP','interpretation':'Planar H fitted to broad arch facade. Other depth groups held out. Relief and endpoint uncertainty remain. Global H residual also reported; pure rotation with any focal/principal points must be a common H in ideal pinhole model.','pairs':outs},indent=2))
