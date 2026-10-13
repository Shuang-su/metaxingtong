"""Frozen D camera hypotheses only. Source/render pixels never transformed.
Manual pixels are observations with stated uncertainty, not exact geometry truth.
"""
from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
R=Path(__file__).parent;J=json.load(open(R/'frozen_d_world_geometry.json'));O=J['objects']
c=J['cameras']['MATCH_F_Turning_Right'];m=np.array(c['matrix_world']);rot=m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0);base=np.r_[Rotation.from_matrix(rot).as_rotvec(),m[:3,3],np.log(c['lens_mm'])]
TV='TV • rectangular black frame';M3='Window • calibrated vertical mullion.003';M4='Window • calibrated vertical mullion.004';RAIL='Curtain rail • forward overhead beam';BED='Bed • observed endboard, consistent width';REC='Bed end • moulded central recess'
P={
 'tv_tl':[5.461250305,-1.233129382,2.134857416],
 'tv_tr':[5.461250305,-3.223905087,2.134857416],
 'tv_br':[5.461250305,-3.223905087,.990924895],
 'tv_bl':[5.461250305,-1.233129382,.990924895],
 'm3_top':[3.576422215,.0027,2.71466565],
 'm4_top':[4.994256496,.0027,2.71466565],
 'shell_corner':[5.537500381,0,2.714665413],
 'rail_left':[1.46442926,-.34530795,2.70874977],
}
# Fixed identification uncertainty includes geometry proxy (not image picking alone).
A={'tv_tl':[1026,604],'tv_tr':[1557,578],'tv_br':[1584,892],'m3_top':[536,296],'m4_top':[690,433],'shell_corner':[744,475],'rail_left':[219,88],'m3_axis':[[529,458],[500,1050]],'m4_axis':[[685,569],[676,1050]],'rail_upper':[[219,88],[900,10]],'bed_train':[[765,938],[1000,895],[1200,882],[1400,885]],'bed_hold':[[739,1006],[815,921],[1540,900],[1760,1020]],'recess_hold':[[1055,969],[1250,966],[1393,970],[1420,993],[1400,1028],[1100,1032],[1029,1015],[1024,995]]}
B={'tv_tl':[1009,584],'tv_tr':[1552,559],'tv_br':[1577,877],'tv_bl':[1018,885],'m3_top':[507,271],'m4_top':[666,409],'shell_corner':[722,452],'rail_left':[170,49],'m3_axis':[[502,433],[466,1050]],'m4_axis':[[661,539],[647,1050]],'rail_upper':[[170,49],[600,2]],'bed_train':[[743,976],[1000,927],[1200,912],[1400,914]],'bed_hold':[[708,1070],[787,955],[1510,923],[1810,1020]],'recess_hold':[[1055,1008],[1260,1003],[1400,1005],[1430,1030],[1400,1063],[1100,1072],[1035,1052],[1028,1027]]}
views={'A':A,'B':B}

def project(x,p):
 q=(np.asarray(p)-x[3:6])@Rotation.from_rotvec(x[:3]).as_matrix();f=np.exp(x[6])/36*1920
 return np.c_[960-f*q[:,0]/q[:,2],540+f*q[:,1]/q[:,2]]
def curve_distance(x,name,uv):
 q=project(x,O[name]['vertices']);h=ConvexHull(q);poly=q[h.vertices];a=poly;b=np.roll(poly,-1,axis=0);v=b-a;p=np.array(uv);t=np.clip(((p[:,None]-a)*v).sum(2)/(v*v).sum(1),0,1);dd=((p[:,None]-(a+t[:,:,None]*v))**2).sum(2);return np.sqrt(dd.min(1))
def line_res(x,xyz,uv):
 q=project(x,xyz);v=q[1]-q[0];n=np.array([-v[1],v[0]])/np.linalg.norm(v);return (np.array(uv)-q[0])@n

def terms(x,k):
 a=views[k];e={}
 for n in ['tv_tl','tv_tr','tv_br','m3_top','rail_left']:
  e[n]=(project(x,[P[n]])[0]-a[n])
 e['m3_axis']=line_res(x,[[3.576422215,.0027,.4],[3.576422215,.0027,2.5]],a['m3_axis'])
 e['bed_upper']=curve_distance(x,BED,a['bed_train'])
 return e
sigma={'tv_tl':4,'tv_tr':4,'tv_br':4,'m3_top':12,'rail_left':10,'m3_axis':10,'bed_upper':12}
# Equal object weighting; the 3 TV points share a group budget. No sofa observations exist in A/B.
weights={'tv_tl':1/np.sqrt(3),'tv_tr':1/np.sqrt(3),'tv_br':1/np.sqrt(3),'m3_top':1/np.sqrt(2),'m3_axis':1/np.sqrt(2),'rail_left':1,'bed_upper':1}

def residual(x,k,bed_weight=1,priors=True):
 ee=[]
 for n,e in terms(x,k).items():ee.extend(e/sigma[n]*weights[n]/np.sqrt(len(e))*(bed_weight if n=='bed_upper' else 1))
 if priors:ee.extend((x[:6]-base[:6])/np.array([1,1,1,8,8,4])*.1)
 return np.array(ee)

def metrics(x,k):
 a=views[k];out={}
 for n,e in terms(x,k).items():out[n]={'split':'train','rms_px':float(np.sqrt(np.mean(e**2))),'residual_px':e.tolist(),'sigma_px':sigma[n]}
 for n in ['m4_top','shell_corner']+(['tv_bl'] if k=='B' else []):
  e=project(x,[P[n]])[0]-a[n];out[n]={'split':'holdout','euclidean_px':float(np.linalg.norm(e)),'residual_xy_px':e.tolist()}
 for n,name,uv in [('bed_upper_hold',BED,a['bed_hold']),('recess_envelope_hold',REC,a['recess_hold'])]:
  e=curve_distance(x,name,uv);out[n]={'split':'holdout','rms_px':float(np.sqrt(np.mean(e**2))),'residual_px':e.tolist()}
 e=line_res(x,[[4.994256496,.0027,.4],[4.994256496,.0027,2.5]],a['m4_axis']);out['m4_axis']={'split':'holdout','rms_px':float(np.sqrt(np.mean(e**2))),'residual_px':e.tolist()}
 e=line_res(x,[P['rail_left'],[1.46442926,-3.38280821,2.70874977]],a['rail_upper']);out['rail_upper_direction']={'split':'holdout','rms_px':float(np.sqrt(np.mean(e**2))),'residual_px':e.tolist()}
 return out

# Shared-focal camera pair; both poses free; geometry/materials immutable.
q0=np.r_[base[:6],base[:6],base[6]];lo=q0-np.r_[np.tile([.3,.3,.3,2.5,2.5,1.1],2),.3];hi=q0+np.r_[np.tile([.3,.3,.3,2.5,2.5,1.1],2),.3];lo[12]=np.log(25);hi[12]=np.log(50);lo[5]=lo[11]=.1
unpack=lambda q:{k:np.r_[q[i*6:i*6+6],q[12]] for i,k in enumerate(views)}
runs=[]
for bw in [.5,1,2]:
 for focal in [30,35.229946,42]:
  st=q0.copy();st[12]=np.log(focal)
  def fun(q):
   xs=unpack(q);return np.r_[residual(xs['A'],'A',bw),residual(xs['B'],'B',bw)]
  sol=least_squares(fun,st,bounds=(lo,hi),loss='soft_l1',max_nfev=500,ftol=1e-10,xtol=1e-10,gtol=1e-10)
  xs=unpack(sol.x);runs.append({'bed_weight':bw,'initial_focal_mm':focal,'cost':sol.cost,'focal_mm':float(np.exp(sol.x[12])),'parameters':sol.x.tolist(),'views':{k:{'camera_parameters':x.tolist(),'metrics':metrics(x,k)} for k,x in xs.items()},'bound_parameters':[i for i in range(len(sol.x)) if min(abs(sol.x[i]-lo[i]),abs(sol.x[i]-hi[i]))<1e-3]})
  print(bw,focal,sol.cost,np.exp(sol.x[12]),flush=True)
bal=min((r for r in runs if r['bed_weight']==1),key=lambda r:r['cost']);xs=unpack(np.array(bal['parameters']));cameras={}
for k,x in xs.items():
 m=np.eye(4);m[:3,:3]=Rotation.from_rotvec(x[:3]).as_matrix();m[:3,3]=x[3:6];cameras[k]={'matrix_world':m.tolist(),'lens_mm':float(np.exp(x[6])),'sensor_width_mm':36,'sensor_fit':'HORIZONTAL','shift_x':0,'shift_y':0,'location':x[3:6].tolist(),'rotation_euler_xyz_rad':Rotation.from_matrix(m[:3,:3]).as_euler('xyz').tolist()}
out={'status':'unaccepted camera hypotheses; source camera uncalibrated','frozen_blend_sha256':J['source_sha256'],'method':'camera-only joint shared focal; equal object budgets TV/window/rail/bed; multi-start and bed-weight sensitivity; no image resampling, registration or warping','pixels_manually_estimated':True,'observations':views,'point_geometry':P,'selected':bal,'cameras':cameras,'runs':runs,'excluded':['dynamic TV content','HUD','light/shadow boundaries','sofa and chair absent from these frames'],'limits':['Camera and focal are hypotheses conditional on unaccepted D geometry.','Manual curve contour proximity is not exact vertex correspondence.','Recess is fully held out.','No spatial scale recovery or full room acceptance is claimed.']}
(R/'camera_candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('SELECTED',json.dumps(cameras));print('METRICS',json.dumps(bal['views']))
