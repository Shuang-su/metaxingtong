"""Read-only numerical diagnostics. Does not import Blender or mutate any scene."""
import json, numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
P=Path(__file__).parent
CAMS=json.load(open(P.parent/'qa/camera_only_fits.json'))
CAMS={c['name']:c for c in CAMS if c['name']!='F_path_059'}
NAMES=list(CAMS)
OBS={
 'A_cup_rim_center':[[756,523],[626,615],[279,541]],
 'B_cup_rim_center':[[982,417],[996,510],[696,631]],
 'A_cup_base_contact':[[756,550],[627,645],[284,568]],
 'B_pencilcase_base_midpoint':[[915,459],[885,555],[557,618]],
}
OBS={k:np.array(v,dtype=float) for k,v in OBS.items()}
V0=np.array([np.r_[c['location'],c['rotation_xyz'],c['lens_mm']/36*1180] for c in CAMS.values()])
def proj(X,v):
 q=(np.asarray(X)-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix()
 return np.stack([590+v[6]*q[...,0]/-q[...,2],332-v[6]*q[...,1]/-q[...,2]],axis=-1)
def ray(p,v):
 d=Rotation.from_euler('xyz',v[3:6]).as_matrix()@np.array([(p[0]-590)/v[6],-(p[1]-332)/v[6],-1.]);return v[:3],d/np.linalg.norm(d)
def triang(obs,vs=V0):
 rs=[ray(p,v) for p,v in zip(obs,vs)]
 A=np.array([np.eye(3)-np.outer(d,d) for c,d in rs]);b=np.array([a@c for a,(c,d) in zip(A,rs)])
 x=np.linalg.solve(A.sum(axis=0),b.sum(axis=0))
 fit=least_squares(lambda x:np.ravel([proj(x,v)-p for v,p in zip(vs,obs)]),x,max_nfev=5000)
 err=np.array([proj(fit.x,v)-p for v,p in zip(vs,obs)]);dists=[np.linalg.norm(np.cross(fit.x-c,d)) for c,d in rs]
 return {'ray_linear_intersection':x.tolist(),'pixel_optimal_point':fit.x.tolist(),'reprojection_rms_px':float(np.sqrt(np.mean(np.sum(err**2,axis=1)))),'per_frame_residuals_px':err.tolist(),'distance_to_rays_model_units':dists},fit.x
TRI={};XS=[]
for k,o in OBS.items():
 TRI[k],x=triang(o);XS.append(x)
XS=np.array(XS)
# Two actual tabletop-contact features, with independent XY and one shared free Z.
tablekeys=['A_cup_base_contact','B_pencilcase_base_midpoint']
def unpack_table(x): return np.array([[x[0],x[1],x[4]],[x[2],x[3],x[4]]])
x0=np.r_[XS[2,:2],XS[3,:2],np.mean(XS[2:,2])]
f=least_squares(lambda x:np.ravel([proj(X,v)-OBS[k][i] for X,k in zip(unpack_table(x),tablekeys) for i,v in enumerate(V0)]),x0,max_nfev=5000)
tres=np.array([proj(X,v)-OBS[k][i] for X,k in zip(unpack_table(f.x),tablekeys) for i,v in enumerate(V0)])
SHARED={'points':dict(zip(tablekeys,unpack_table(f.x).tolist())),'shared_z_model_units':float(f.x[4]),'rms_px':float(np.sqrt(np.mean(np.sum(tres**2,axis=1)))),'per_observation_residuals_px':tres.tolist()}
# Plane sensitivity with no camera adjustment.
planes={}
for z in [.45,.55,.6954849958,.8,.95]:
 entry={}
 for k,o in OBS.items():
  if 'base' not in k:continue
  vals=[]
  for p,v in zip(o,V0):
   c,d=ray(p,v);vals.append(c+(z-c[2])/d[2]*d)
  entry[k]={'points':np.array(vals).tolist(),'max_pairwise_disagreement':float(max(np.linalg.norm(a-b) for a in vals for b in vals))}
 planes[str(z)]=entry
# Joint bundle: original FIT anchors remain fixed, original HOLDOUT anchors remain excluded.
# Four static 3D features; two contacts share table Z. Cup rim heights unconstrained independently.
ANCH=[];HOLD=[]
for c in CAMS.values():
 ANCH.append([(np.array(p['world']),np.array(p['source_px'])) for p in c['points'] if p['role']=='fit'])
 HOLD.append([(np.array(p['world']),np.array(p['source_px'])) for p in c['points'] if p['role']=='holdout'])
def unpack(v):
 cs=v[:21].reshape(3,7);d=v[21:];z=d[4]
 pts=np.array([[d[0],d[1],z],[d[2],d[3],z],d[5:8],d[8:11]])
 return cs,pts
keys=tablekeys+['A_cup_rim_center','B_cup_rim_center']
startpts=[]
for k in keys:
 o=OBS[k];rr=[]
 for p,v in zip(o,V0):
  c,d=ray(p,v);z=.695485 if 'base' in k else .80;rr.append(c+(z-c[2])/d[2]*d)
 startpts.append(np.mean(rr,axis=0))
startpts=np.array(startpts)
vv=np.r_[V0.ravel(),startpts[0,:2],startpts[1,:2],.695485,startpts[2],startpts[3]]
lo=np.r_[(V0-np.array([1,1,1,.175,.175,.175,0])).ravel(),[-5,-1,-5,-1,.20,-5,-1,.20,-5,-1,.20]]
hi=np.r_[(V0+np.array([1,1,1,.175,.175,.175,0])).ravel(),[5,12,5,12,1.40,5,12,1.70,5,12,1.70]]
lo[:21].reshape(3,7)[:,6]=V0[:,6]*.70;hi[:21].reshape(3,7)[:,6]=V0[:,6]*1.30

def residual(v,prior):
 cs,pts=unpack(v);r=[]
 for c,anc in zip(cs,ANCH):r.extend((proj(X,c)-p)/5 for X,p in anc)
 for X,k in zip(pts,keys):r.extend((proj(X,c)-p)/4 for c,p in zip(cs,OBS[k]))
 r=np.array(r).ravel()
 if prior:
  # Soft priors express 'microadjustment', not independent observed facts.
  s=np.array([.25,.25,.25,.035,.035,.035,1.])
  ss=np.tile(s,(3,1));ss[:,6]=V0[:,6]*.08
  r=np.r_[r,((cs-V0)/ss).ravel()]
 return r

def metrics(v):
 cs,pts=unpack(v);cresult=[]
 for i,(c,anc,hold) in enumerate(zip(cs,ANCH,HOLD)):
  ae=np.array([proj(X,c)-p for X,p in anc]);he=np.array([proj(X,c)-p for X,p in hold]);se=np.array([proj(X,c)-OBS[k][i] for X,k in zip(pts,keys)])
  cresult.append({'name':NAMES[i],'location':c[:3].tolist(),'rotation_xyz':c[3:6].tolist(),'lens_mm':float(c[6]*36/1180),'delta_location_norm':float(np.linalg.norm(c[:3]-V0[i,:3])),'delta_rotation_degrees':np.degrees(c[3:6]-V0[i,3:6]).tolist(),'lens_change_percent':float((c[6]/V0[i,6]-1)*100),'original_fit_rms_px':CAMS[NAMES[i]]['fit_rms_px'],'new_fit_anchor_rms_px':float(np.sqrt(np.mean(np.sum(ae**2,axis=1)))),'original_holdout_rms_px':CAMS[NAMES[i]]['holdout_rms_px'],'new_holdout_rms_px':float(np.sqrt(np.mean(np.sum(he**2,axis=1)))),'static_feature_rms_px':float(np.sqrt(np.mean(np.sum(se**2,axis=1)))),'static_feature_residuals_px':dict(zip(keys,se.tolist()))})
 return {'table_z_model_units':float(pts[0,2]),'static_points':dict(zip(keys,pts.tolist())),'cameras':cresult}
BUNDLE={}
for prior in [True,False]:
 fit=least_squares(lambda x:residual(x,prior),vv,bounds=(lo,hi),max_nfev=10000,ftol=1e-11,xtol=1e-11,gtol=1e-11)
 result=metrics(fit.x);result.update({'success':bool(fit.success),'nfev':int(fit.nfev),'weighted_sum_sq':float(np.sum(fit.fun**2)),'active_bounds':np.flatnonzero(fit.active_mask).tolist(),'description':'Soft small-adjustment priors' if prior else 'Broad-bound diagnostic without pose/focal priors'})
 BUNDLE['regularized' if prior else 'unregularized']=result
# Contact-height profile with small-adjustment priors, to expose ambiguity rather than select an exact height.
PROFILE=[]
for z in [.45,.55,.65,.75,.85,.95]:
 def ex(w):return np.r_[w[:25],z,w[25:]]
 varidx=[i for i in range(len(vv)) if i!=25]
 init=vv[varidx]
 fit=least_squares(lambda w:residual(ex(w),True),init,bounds=(lo[varidx],hi[varidx]),max_nfev=4000)
 mm=metrics(ex(fit.x));PROFILE.append({'fixed_table_z':z,'weighted_sum_sq':float(np.sum(fit.fun**2)),'anchor_rms_by_frame':[q['new_fit_anchor_rms_px'] for q in mm['cameras']],'static_rms_by_frame':[q['static_feature_rms_px'] for q in mm['cameras']]})
RESULT={'schema_version':1,'coordinate_system':'1180x664 video crop. Original screenshot pixels = (u,v+47). All 3D coordinates in existing model units; no metric scale claim.','manual_points':{k:dict(zip(NAMES,v.tolist())) for k,v in OBS.items()},'measurement_warning':'Cup centers +/-3 px, contact midpoints +/-4-6 px. B cup base is censored at bottom in F_path_080 and excluded. Pencil-case contact midpoint is approximate, not an exact point measurement.','locked_camera_free_triangulation':TRI,'locked_camera_two_contact_shared_height':SHARED,'locked_camera_plane_sensitivity':planes,'joint_bundle':BUNDLE,'regularized_height_profile':PROFILE,'limits':'Exploratory only. Existing fixed model architecture/furniture may be geometrically wrong; small joint residual does not prove it correct. No model update or camera commitment. Holdouts independent from objective.'}
(P/'camera_static_point_diagnostics.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2))
for k,r in TRI.items():print('TRI',k,np.round(r['pixel_optimal_point'],3),r['reprojection_rms_px'])
print('SHARED',SHARED)
for name,res in BUNDLE.items():
 print('BUNDLE',name,'height',res['table_z_model_units'],'bounds',res['active_bounds'])
 for c in res['cameras']:print(c['name'], 'anchor',round(c['new_fit_anchor_rms_px'],2),'hold',round(c['new_holdout_rms_px'],2),'static',round(c['static_feature_rms_px'],2),'loc',round(c['delta_location_norm'],3),'focal%',round(c['lens_change_percent'],1))
print('PROFILE',PROFILE)
# Shared focal length for the whole continuous high-angle segment.
def expand_common(w):
 cs=np.c_[w[:18].reshape(3,6),np.full(3,w[18])]
 return np.r_[cs.ravel(),w[19:]]
common0=np.r_[V0[:,:6].ravel(),np.mean(V0[:,6]),vv[21:]]
commonlo=np.r_[lo[:21].reshape(3,7)[:,:6].ravel(),min(V0[:,6])*.70,lo[21:]]
commonhi=np.r_[hi[:21].reshape(3,7)[:,:6].ravel(),max(V0[:,6])*1.30,hi[21:]]
COMMON={}
for prior in [True,False]:
 fit=least_squares(lambda w:residual(expand_common(w),prior),common0,bounds=(commonlo,commonhi),max_nfev=10000,ftol=1e-11,xtol=1e-11,gtol=1e-11)
 mm=metrics(expand_common(fit.x));mm.update({'success':bool(fit.success),'nfev':int(fit.nfev),'weighted_sum_sq':float(np.sum(fit.fun**2)),'active_bounds':np.flatnonzero(fit.active_mask).tolist(),'shared_focal_mm':float(fit.x[18]*36/1180)})
 COMMON['regularized' if prior else 'unregularized']=mm
 print('COMMON',prior,'height',mm['table_z_model_units'],'f',mm['shared_focal_mm'],'bounds',mm['active_bounds'])
 for c in mm['cameras']:print(c['name'],'anchor',round(c['new_fit_anchor_rms_px'],2),'hold',round(c['new_holdout_rms_px'],2),'static',round(c['static_feature_rms_px'],2),'loc',round(c['delta_location_norm'],3),'focal%',round(c['lens_change_percent'],1))
RESULT['shared_focal_joint_bundle']=COMMON
RESULT['comparison']={'statement':'A shared focal model and per-frame focal model are alternative diagnostics, not proof of animated zoom. Compare image residuals and independent holdouts rather than optimizer success.','anchor_points_per_frame':[len(a) for a in ANCH],'holdout_points_per_frame':[len(a) for a in HOLD],'number_static_feature_observations':12,'free_focal_parameter_count':32,'shared_focal_parameter_count':30,'observed_scalar_count':76}
(P/'camera_static_point_diagnostics.json').write_text(json.dumps(RESULT,ensure_ascii=False,indent=2))
