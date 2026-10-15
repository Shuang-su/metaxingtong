"""Conditional small-step shared geometry; no per-view geometry or image registration.
Only G/H named cushion upper and unambiguous side branches fit; N640 furniture held out.
N640 camera is a rotation/focal hypothesis derived from static window frames only.
"""
import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).parent
# import diagnostic functions without executing diagnostic producer
text=(R/'diagnose_contours.py').read_text();exec(text[:text.index('out=[]\nfor k,n')])
base=D['cameras']['MATCH_H'];M=np.array(base['matrix']);Q=M[:3,:3]/np.linalg.norm(M[:3,:3],axis=0)
# Black frame centerline samples, source grayscale-dark interval inspected at each row.
winobs=[(-1.603616178,[[106.5,350],[101,500],[95.5,650]]),(0,[[1009,350],[1010,500],[1012,650]]),(1.5,[[1567,350],[1573,500],[1579.5,650]])]
def cam_n640(q):
 c=dict(base);mat=M.copy();mat[:3,:3]=Rotation.from_rotvec(q[:3]).as_matrix()@Q;c['matrix']=mat.tolist();c['lens']=base['lens']*np.exp(q[3]);return c

def line_res(c,x,pts):
 p=project(np.array([[x,.0027,0],[x,.0027,2.7146654]]),c);return [p[0,0]+(uv[1]-p[0,1])*(p[1,0]-p[0,0])/(p[1,1]-p[0,1])-uv[0] for uv in pts]
solcam=least_squares(lambda q:np.r_[np.concatenate([line_res(cam_n640(q),x,pts) for x,pts in winobs])/2,q/np.array([.08,.08,.08,.06])],np.zeros(4),bounds=(-np.array([.12,.12,.12,.06]),np.array([.12,.12,.12,.06])),loss='linear',max_nfev=500)
N=cam_n640(solcam.x);cams={'G':D['cameras']['MATCH_G_Sofa_And_Bed'],'H':base,'N640':N}
# Preserve observed source branches; numerical fitting uses only straight-run side samples.
records=[]
for br in A['branches']:
 if br['object_id'] not in ['sofa_back_left','sofa_back_right']:continue
 if br['contour_branch'] not in ['upper','left','right']:continue
 br=dict(br);br['mesh_name']=MAP[br['object_id']];br['excluded_samples']=[]
 if br['contour_branch']!='upper':
  # Rounded shoulder has its own identity; no nearest-side or upper replacement.
  br['excluded_samples']=br['source_points'][:1];br['source_points']=br['source_points'][1:]
 records.append(br)
names=['Sofa • reclined back cushion 1','Sofa • reclined back cushion 2']
verts={n:np.array(D['meshes'][n]['vertices']) for n in names};EE={n:edges(D['meshes'][n]) for n in names}
def deformed(n,q):
 v=verts[n].copy();h=(v[:,2]-v[:,2].min())/(v[:,2].max()-v[:,2].min());v+=h[:,None]*q[3*names.index(n):3*names.index(n)+3];return v

def residual_record(br,q):
 n=br['mesh_name'];p=project(deformed(n,q),cams[br['frame']]);axis=0 if br['contour_branch']=='upper' else 1;side='max' if br['contour_branch']=='right' else 'min';return directed(p,EE[n],br['source_points'],axis,side)
fit=[b for b in records if b['frame'] in ['G','H']]
def fun(q):
 rr=[]
 for br in fit:
  for t in residual_record(br,q):
   rr.append(t['residual']/br['uncertainty_px'] if t['residual'] is not None else 100)
 return np.r_[rr,q/np.tile([.05,.05,.035],2)]
sol=least_squares(fun,np.zeros(6),bounds=(-np.tile([.08,.08,.05],2),np.tile([.08,.08,.05],2)),loss='soft_l1',max_nfev=1000,xtol=1e-10,ftol=1e-10,gtol=1e-10)
res={'status':'UNACCEPTED_CONDITIONAL_SHARED_CUSHION_CANDIDATE','base':'D','cameras':cams,'geometry_parameters':{n:sol.x[3*i:3*i+3].tolist() for i,n in enumerate(names)},'deformation':'world deltaXYZ times normalized height above cushion bottom; all views same mesh; bottom fixed','fit_views':['G','H'],'heldout_furniture_view':'N640','N640_camera':{'hypothesis':'D H camera position fixed; rotation and <=6% focal correction from three known window centerlines only; no sofa observations used; pure-rotation cross-time identity not independently verified','parameters':solcam.x.tolist(),'window_samples':winobs,'window_residuals_px':{str(x):line_res(N,x,pts) for x,pts in winobs}},'branches':[],'limitations':['Camera/geometry ambiguity remains. No patient-bed metric calibration. No acceptance. Mesh visibility to be checked with scene ray casts. Source shoulder points excluded instead of reassigning to another branch.']}
for br in records:
 b=residual_record(br,np.zeros(6));a=residual_record(br,sol.x);res['branches'].append({'branch_id':br['branch_id'],'mesh':br['mesh_name'],'frame':br['frame'],'role':'fit' if br['frame'] in ['G','H'] else 'conditional_holdout','branch':br['contour_branch'],'source_uncertainty_px':br['uncertainty_px'],'excluded_rounded_transition_samples':br['excluded_samples'],'before':b,'after':a})
(R/'local_fit_candidate.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print('CAM',res['N640_camera']);print('GEOM',res['geometry_parameters'])
for frame in ['G','H','N640']:
 for mode in ['before','after']:
  v=[t['residual'] for b in res['branches'] if b['frame']==frame for t in b[mode] if t['residual'] is not None];print(frame,mode,'n',len(v),'medianAbs',np.median(np.abs(v)),'MAE',np.mean(np.abs(v)),'MAX',np.max(np.abs(v)))
