import json,numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
D=Path(__file__).resolve().parents[1];Q=D/'qa/camera-new-source';obs=json.load(open(Q/'observations.json'));meshes=json.load(open(D/'qa/camera_diagnostic_meshes.json'));cams=json.load(open(D/'qa/camera_diagnostic_initial_cameras.json'))
def edge(obj,side):
 v=np.array(meshes[obj]['vertices_world']);y=v[:,1].min();front=v[abs(v[:,1]-y)<1e-5]
 if side in ['left','right']:
  x=front[:,0].min()if side=='left'else front[:,0].max();a=front[abs(front[:,0]-x)<1e-5];a=a[np.argsort(a[:,2])]
 else:
  z=front[:,2].max()if side=='top'else front[:,2].min();a=front[abs(front[:,2]-z)<1e-5];a=a[np.argsort(a[:,0])]
 if len(a)<2:raise ValueError((obj,side,len(a)))
 return np.array([a[0],a[-1]])
def project(p,v):
 R=Rotation.from_rotvec(p[:3]).as_matrix();q=(R@(v-p[3:6]).T).T;f=p[6]*1920/36;uv=q[:,:2]/q[:,2,None]*f+np.array([960,540]);return uv,q[:,2]
def residual(p,lines,scaled=True):
 out=[]
 for line in lines:
  uv,z=project(p,edge(line['object'],line['side']));a,b=uv;v=b-a;P=np.array(line['pixels']);t=((P-a)@v)/(v@v);near=a+np.clip(t,0,1)[:,None]*v;r=(P-near).reshape(-1)
  out.extend(r/(line['sigma']if scaled else 1));out.extend(np.minimum(z-.05,0)*100)
 return np.array(out)
results=[]
for view in obs['views']:
 M=np.array(cams[view['initial_camera']]['matrix']);R=np.diag([1,-1,-1])@M[:3,:3].T;base=np.r_[Rotation.from_matrix(R).as_rotvec(),M[:3,3],cams[view['initial_camera']]['lens']];tr=view['training'];ho=view['held_out'];starts=[]
 for lens in [36,55,80]:
  p=base.copy();p[6]=lens;p[4]=np.clip(base[4]*lens/base[6],-24.5,-2.1);p[3]=np.clip(p[3],-5.9,5.9);p[5]=np.clip(p[5],.31,7.9)
  sol=least_squares(lambda x:residual(x,tr),p,bounds=([-np.inf]*3+[-6,-25,.3,16],[np.inf]*3+[6,-2,8,100]),loss='soft_l1',max_nfev=900,ftol=1e-10,xtol=1e-10,gtol=1e-10)
  starts.append({'p':sol.x,'score':float(np.mean(residual(sol.x,tr)**2)),'success':bool(sol.success),'nfev':sol.nfev,'jac_singular_values':np.linalg.svd(sol.jac,compute_uv=False).tolist()})
 best=min(starts,key=lambda x:x['score']);p=best['p'];per=[]
 for use,lines in [('train',tr),('held_out',ho)]:
  for line in lines:
   uv,z=project(p,edge(line['object'],line['side']));a,b=uv;v=b-a;P=np.array(line['pixels']);t=((P-a)@v)/(v@v);err=np.linalg.norm(P-(a+np.clip(t,0,1)[:,None]*v),axis=1);per.append({'id':line['id'],'use':use,'errors_px':err.tolist(),'projected_edge':uv.tolist(),'observed_points':P.tolist(),'sigma':line['sigma'],'endpoint_t':t.tolist()})
 hits={k:float(v)for k,v,lo,hi in zip(['cx','cy','cz','f'],p[3:],[-6,-25,.3,16],[6,-2,8,100])if min(abs(v-lo),abs(v-hi))<.01}
 results.append({'source':view['source'],'base_parameters':base.tolist(),'best_parameters':p.tolist(),'train_initial_rms_scaled':float(np.sqrt(np.mean(residual(base,tr)**2))),'train_final_rms_scaled':best['score']**.5,'held_initial_rms_scaled':float(np.sqrt(np.mean(residual(base,ho)**2))),'held_final_rms_scaled':float(np.sqrt(np.mean(residual(p,ho)**2))),'starts':[{**x,'p':x['p'].tolist()}for x in starts],'per_line':per,'bound_hits':hits,'camera_center_outside_known_cabinet_boxes':bool(p[4]<-2),'camera_before_known_back_wall':bool(p[4]<1.28),'camera_inside_known_right_wall':bool(p[3]<6.08),'not_checked':'Full ray occlusion/cabinet surface correspondence; unknown ceiling/front not feasibility truths'})
(Q/'fit_results.json').write_text(json.dumps({'scope':'One conditional frozen-geometry point-to-finite-evaluated-edge pose/focal diagnostic; no model changed/rendered','parameter_order':['rotvec_x','rotvec_y','rotvec_z','Cx','Cy','Cz','focal_mm'],'principal_point_assumption':[960,540],'bounds':'Working computation bounds only; unknown front shell not imposed; no VP focal prior','no_holdout_model_selection':True,'reverse_2570_source_not_used':True,'results':results},indent=2));print([(r['source'],r['train_final_rms_scaled'],r['held_final_rms_scaled'],r['bound_hits'])for r in results])
