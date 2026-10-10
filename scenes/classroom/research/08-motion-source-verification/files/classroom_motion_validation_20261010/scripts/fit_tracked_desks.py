import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
p=Path('classroom_motion_validation_20261010');j=json.load(open(p/'desk_identity_highview/camera_static_point_diagnostics.json'))['shared_focal_joint_bundle']['regularized'];a=json.load(open(p/'desk_identity_highview/source_desk_identity_annotations.json'));cams={c['name']:c for c in j['cameras']};z=j['table_z_model_units'];out=[]
def project(X,c):
 q=(X-np.array(c['location']))@Rotation.from_euler('xyz',c['rotation_xyz']).as_matrix();f=c['lens_mm']/36*1180;return np.stack([590+f*q[:,0]/-q[:,2],332-f*q[:,1]/-q[:,2]],1)
def rectangle(v):
 cx,cy,w,d,t=v;xy=np.array([[w/2,-d/2],[-w/2,-d/2],[-w/2,d/2],[w/2,d/2]])@np.array([[np.cos(t),np.sin(t)],[-np.sin(t),np.cos(t)]]);return np.c_[xy+[cx,cy],np.full(4,z)]
for name in ['HV_A_book_stack','HV_B_paper_case']:
 observations=[]
 for frame,obs in a['tracks'][name]['frames'].items():
  for corner,q in obs['corners'].items():
   if q['pixel'] is not None and q['status'].startswith('visible'):observations.append((frame,int(corner[1]),np.array(q['pixel']),q['uncertainty_px']))
 def residual(v):
  X=rectangle(v);return np.concatenate([(project(X,cams[f])[i]-pt)/unc for f,i,pt,unc in observations])
 best=None
 for theta in np.arange(-np.pi,np.pi,.5):
  v0=[.6 if 'A_' in name else -.6,5.8,.8,.5,theta];fit=least_squares(residual,v0,bounds=([-4,1,.2,.15,-7],[4,9,1.5,1.2,7]),max_nfev=2000)
  if best is None or fit.cost<best.cost:best=fit
 v=best.x;X=rectangle(v);rows=[{'frame':f,'corner':'Q'+str(i),'source_px':pt.tolist(),'projected_px':project(X,cams[f])[i].tolist(),'error_px':float(np.linalg.norm(project(X,cams[f])[i]-pt)),'uncertainty_px':unc} for f,i,pt,unc in observations];out.append({'source_id':name,'rectangle_parameters_cx_cy_width_depth_angle':v.tolist(),'tabletop_z':z,'world_corners_Q0_to_Q3':X.tolist(),'visible_corner_rms_px':float(np.sqrt(np.mean([r['error_px']**2 for r in rows]))),'points':rows,'scope':'Fits visible rounded corners only. Camera is static-feature/building joint shared-focal diagnostic. No old model deskID imposed; no frame-specific desk movement. Height conditional.'});print(name,v,'rms',out[-1]['visible_corner_rms_px'])
(p/'tracked_desks_white/qa/two_rectangle_fits.json').write_text(json.dumps({'camera_solution':'shared_focal_joint_bundle.regularized','cameras':list(cams.values()),'desks':out,'limitations':'Two observed tables only, not full classroom count. Other visible unmeasured tables remain unmodelled constraints. Table thickness/legs/chairs not recovered by this fit.'},indent=2))
# Prefer a single shared furniture size/orientation if it explains visible corners comparably.
observations=[]
for di,name in enumerate(['HV_A_book_stack','HV_B_paper_case']):
 for frame,obs in a['tracks'][name]['frames'].items():
  for corner,q in obs['corners'].items():
   if q['pixel'] is not None and q['status'].startswith('visible'):observations.append((di,frame,int(corner[1]),np.array(q['pixel']),q['uncertainty_px']))
def params(v,di):return [v[di*2],v[di*2+1],v[4],v[5],v[6]]
def residual(v):return np.concatenate([(project(rectangle(params(v,di)),cams[f])[i]-pt)/unc for di,f,i,pt,unc in observations])
v0=np.r_[out[0]['rectangle_parameters_cx_cy_width_depth_angle'][:2],out[1]['rectangle_parameters_cx_cy_width_depth_angle'][:2],.61,.385,0];fit=least_squares(residual,v0,max_nfev=2000);v=fit.x;common=[]
for di,original in enumerate(out):
 pp=params(v,di);X=rectangle(pp);rows=[{'frame':f,'corner':'Q'+str(i),'source_px':pt.tolist(),'projected_px':project(X,cams[f])[i].tolist(),'error_px':float(np.linalg.norm(project(X,cams[f])[i]-pt)),'uncertainty_px':unc} for d,f,i,pt,unc in observations if d==di];r=dict(original);r['rectangle_parameters_cx_cy_width_depth_angle']=list(pp);r['world_corners_Q0_to_Q3']=X.tolist();r['points']=rows;r['visible_corner_rms_px']=float(np.sqrt(np.mean([x['error_px']**2 for x in rows])));common.append(r)
(p/'tracked_desks_white/qa/two_rectangle_fits.json').write_text(json.dumps({'camera_solution':'shared_focal_joint_bundle.regularized','cameras':list(cams.values()),'desks':common,'independent_sizes_diagnostic':out,'shared_template':{'width':v[4],'depth':v[5],'angle':v[6]},'limitations':'Two observed tables only, not room total. Other source tables remain unmodelled. Generic leg supports inferred. Shared size/orientation preferred over unexplained5% table size difference.'},indent=2));print('SHARED',v,'rms',[r['visible_corner_rms_px'] for r in common])
