from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1];C=np.array([590.,332.])
def mapR(a,p):
 f1,f2=np.exp(p[:2]);q=np.c_[(a-C)/f1,np.ones(len(a))]@Rotation.from_rotvec(p[2:5]).as_matrix().T;return C+f2*q[:,:2]/q[:,2:]
def homography(a,b):
 def norm(x):
  c=x.mean(0);s=np.sqrt(2)/np.mean(np.linalg.norm(x-c,axis=1));T=np.array([[s,0,-s*c[0]],[0,s,-s*c[1]],[0,0,1]]);return (np.c_[x,np.ones(len(x))]@T.T)[:,:2],T
 x,T=norm(a);y,U=norm(b);A=[]
 for (xx,yy),(u,v) in zip(x,y):A += [[-xx,-yy,-1,0,0,0,u*xx,u*yy,u],[0,0,0,-xx,-yy,-1,v*xx,v*yy,v]]
 _,_,vt=np.linalg.svd(A);H=np.linalg.inv(U)@vt[-1].reshape(3,3)@T;return H/H[2,2]
def hmap(a,H):
 q=np.c_[a,np.ones(len(a))]@H.T;return q[:,:2]/q[:,2:]
def robustH(a,b):
 rng=np.random.default_rng(72);best=[]
 for k in range(700):
  try:
   j=rng.choice(len(a),4,replace=False);H=homography(a[j],b[j]);e=np.linalg.norm(hmap(a,H)-b,axis=1);ins=np.flatnonzero(e<2.5)
   if len(ins)>len(best):best=ins
  except (np.linalg.LinAlgError,ValueError):pass
 if len(best)<4:return None,None
 H=homography(a[best],b[best]);return H,np.linalg.norm(hmap(a,H)-b,axis=1)
def stats(x):return {'n':len(x),'median_px':float(np.median(x)),'p90_px':float(np.percentile(x,90)),'max_px':float(np.max(x))}
for name in ['pair_4528_4529_tentative','pair_2713_4509_tentative']:
 d=json.loads((R/'qa'/(name+'.json')).read_text());ms=[];rejected=[]
 for m in d['matches']:
  x,y=m['source_xy'];u,v=m['target_xy'];bad=(u>=1068 and v>=535) or v>=626
  if '4528' in name:bad |= (435<x<675 and 195<y<620) or (467<u<671 and 195<v<630)
  else:bad |= (500<u<693 and 193<v<664) or m['group']=='table_cake'
  if bad:rejected.append(m)
  else:ms.append(m)
 a=np.array([m['source_xy'] for m in ms],float);b=np.array([m['target_xy'] for m in ms],float);groups=np.array([m['group'] for m in ms]);archgroups=['near_wall','side_window','back_lamp'] if '4528' in name else ['back_lamp','back_lamp_right'];sel=np.isin(groups,archgroups);aa=a[sel];bb=b[sel];gs=groups[sel];w=np.array([1/np.sqrt(sum(gs==g)) for g in gs]);w*=np.sqrt(len(w)/len(set(gs)))
 runs=[]
 for f0 in [500,800,1200,1800,2350]:
  scale=.65 if '2713' in name else 1.;init=[np.log(f0),np.log(np.clip(f0*scale,400,2400)),.04 if '2713' in name else 0,.0 if '2713' in name else .16,0]
  sol=least_squares(lambda p:((mapR(aa,p)-bb)*w[:,None]).ravel(),init,bounds=([np.log(400),np.log(400),-.65,-.65,-.25],[np.log(2400),np.log(2400),.65,.65,.25]),loss='soft_l1',f_scale=1,max_nfev=600)
  e=np.linalg.norm(mapR(aa,sol.x)-bb,axis=1);runs.append((float(np.sum(np.minimum(e,10)**2)),sol))
 _,sol=min(runs,key=lambda x:x[0]);p=sol.x;err=np.linalg.norm(mapR(a,p)-b,axis=1);sv=np.linalg.svd(sol.jac,compute_uv=False);Ha,ea=robustH(aa,bb);hf,ef=robustH(a[np.char.startswith(groups.astype(str),'floor')],b[np.char.startswith(groups.astype(str),'floor')]);h_all,e_all=robustH(a,b)
 profile=[]
 for f1 in [450,600,800,1000,1400,1900,2350]:
  ini=np.r_[p[1],p[2:]];ss=least_squares(lambda q:((mapR(aa,np.r_[np.log(f1),q])-bb)*w[:,None]).ravel(),ini,bounds=([np.log(400),-.65,-.65,-.25],[np.log(2400),.65,.65,.25]),loss='soft_l1',f_scale=1,max_nfev=350);ee=np.linalg.norm(mapR(aa,np.r_[np.log(f1),ss.x])-bb,axis=1);profile.append({'f1_pixels':f1,'f2_pixels':float(np.exp(ss.x[0])),'training_median_px':float(np.median(ee)),'training_p90_px':float(np.percentile(ee,90))})
 out={'source':d['source'],'target':d['target'],'status':'IDENTIFIABILITY_DIAGNOSTIC_NOT_CAMERA_OR_GEOMETRY_ACCEPTANCE','assumptions':'Perspective cameras with fixed principal point (590,332), square pixels, no distortion. Per-view focal lengths bounded 400..2400 pixels. Rotation+zoom mapping only; no translation and no image warp. Only named static architecture groups fit; floor/props are diagnostic validation, with tentative correspondence uncertainty.','training_groups':archgroups,'retained_matches':len(ms),'rejected_dynamic_ui_or_ambiguous':len(rejected),'rotation_zoom':{'f1_pixels':float(np.exp(p[0])),'f2_pixels':float(np.exp(p[1])),'rotation_vector_radians':p[2:].tolist(),'training_residual':stats(err[sel]),'by_group':{g:stats(err[groups==g]) for g in sorted(set(groups))},'jacobian_singular_values':sv.tolist(),'condition_number':float(sv[0]/sv[-1]),'focal_profile':profile},'architecture_general_homography':{'matrix':Ha.tolist(),'residual':stats(ea),'inliers_2_5px':int(sum(ea<2.5))} if Ha is not None else None,'floor_plane_homography':{'matrix':hf.tolist(),'residual':stats(ef),'inliers_2_5px':int(sum(ef<2.5))} if hf is not None else None,'all_point_general_homography':{'matrix':h_all.tolist(),'residual':stats(e_all),'inliers_2_5px':int(sum(e_all<2.5))} if h_all is not None else None,'points':[dict(m,rotation_zoom_prediction=q.tolist(),rotation_zoom_error_px=float(e)) for m,q,e in zip(ms,mapR(a,p),err)],'no_reference_warp':True,'heldout_4426_used':False}
 (R/'qa'/(name.replace('_tentative','')+'_motion_diagnostic.json')).write_text(json.dumps(out,indent=2));print(name,'rotation zoom',out['rotation_zoom']['training_residual'],'f',np.exp(p[:2]),'condition',sv[0]/sv[-1]);print('groups',out['rotation_zoom']['by_group']);print('globalH',out['all_point_general_homography']['inliers_2_5px'],'/',len(ms))
