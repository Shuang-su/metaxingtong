import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pathlib import Path
p=Path('classroom_motion_validation_20261010');old=json.load(open('classroom_hd_alignment_20261010/qa/scene_inspection.json'));cams={c['name']:c for c in old['cameras']}
w={'board_TL':[1.9,.084,2.060728],'board_TR':[-1.9,.084,2.060728],'board_BL':[1.9,.084,.593477],'board_BR':[-1.9,.084,.593477],'clock':[-1.82,.1065,2.340059],'door_TL':[-4.0175,.768928,1.698732],'door_TR':[-4.0175,1.640472,1.698732],'door_BL':[-4.0175,.768928,0],'door_BR':[-4.0175,1.640472,0],'teacher_L':[-.363664,2.074549,.846306],'teacher_R':[-1.279898,2.074549,.846306],'leg_L':[-.4173,2.056494,.092171],'leg_R':[-1.2263,2.056494,.092171],'leg_back_L':[-.4173,1.577866,.092171],'book_BL':[3.049261,.458706,.004225],'book_BR':[2.287747,.458706,.004225],'stage_FL':[1.838784,2.304318,.092171],'stage_FR':[-1.661069,2.304318,.092171],'stage_BL':[1.838784,.452229,.092171],'stage_BR':[-1.661069,.452229,.092171]}
obs={
'F_path_059':{'fit':{'board_TR':[446,79],'board_BR':[447,292],'clock':[431,39],'door_TL':[716,146],'door_TR':[798,137],'door_BL':[713,351],'door_BR':[793,365],'teacher_L':[390,274],'teacher_R':[533,266]},'hold':{'leg_L':[397,410],'leg_back_L':[351,397]}},
'F_path_073':{'fit':{'board_TL':[8,38],'board_TR':[500,12],'board_BL':[48,262],'board_BR':[505,191],'door_TL':[740,51],'door_TR':[812,58],'door_BL':[730,237],'door_BR':[798,257],'teacher_L':[460,230],'teacher_R':[575,213]},'hold':{'stage_FL':[121,440],'stage_FR':[643,311],'leg_L':[472,332],'leg_R':[570,309]}},
'F_path_076':{'fit':{'board_BL':[147,197],'board_BR':[628,145],'teacher_L':[526,195],'teacher_R':[665,181],'door_BL':[884,209],'door_BR':[948,234],'book_BR':[108,300],'door_TR':[983,17]},'hold':{'stage_FL':[150,398],'stage_FR':[729,297],'leg_L':[539,300],'leg_R':[654,282]}},
'F_path_080':{'fit':{'board_BL':[503,143],'board_BR':[973,182],'book_BL':[369,207],'book_BR':[460,218],'teacher_L':[734,210],'teacher_R':[897,222],'stage_BL':[490,200],'stage_BR':[941,241]},'hold':{'stage_FL':[384,302],'stage_FR':[943,365],'leg_L':[739,316],'leg_R':[873,331]}}
}
results=[]
for name,d in obs.items():
 labels=list(d['fit'])+list(d['hold']);X=np.array([w[k] for k in labels]);Y=np.array([d['fit'].get(k,d['hold'].get(k)) for k in labels]);N=len(d['fit'])
 def project(v):
  q=(X-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix();return np.stack([590+v[6]*q[:,0]/-q[:,2],332-v[6]*q[:,1]/-q[:,2]],1)
 best=None
 for camname in ['SOURCE_4310','SOURCE_4300','SOURCE_4298']:
  c=cams[camname];v=np.r_[c['location'],c['rotation'],c['lens']/36*1180];fit=least_squares(lambda v:(project(v)[:N]-Y[:N]).ravel(),v,max_nfev=1500)
  if fit.x[6]>100 and fit.x[1]>2 and (best is None or fit.cost<best.cost):best=fit
 v=best.x;uv=project(v);err=np.linalg.norm(uv-Y,axis=1);r={'name':name,'location':v[:3].tolist(),'rotation_xyz':v[3:6].tolist(),'lens_mm':float(v[6]*36/1180),'sensor_width_mm':36,'fit_rms_px':float(np.sqrt(np.mean(err[:N]**2))),'holdout_rms_px':float(np.sqrt(np.mean(err[N:]**2))),'points':[{'label':k,'world':w[k],'source_px':Y[i].tolist(),'projected_px':uv[i].tolist(),'error_px':float(err[i]),'role':'fit' if i<N else 'holdout'} for i,k in enumerate(labels)],'caveats':'Manual boundary picks ~3-6px uncertainty, moving video screenshot time bracket ~0.3s. Camera-only fit; no geometry/material change. Partial source blur. Existing4310 family, not new independent baseline count.'};results.append(r);print(name,r['fit_rms_px'],r['holdout_rms_px'],r['location'],r['lens_mm'])
(p/'qa/camera_only_fits.json').write_text(json.dumps(results,indent=2));(p/'qa/manual_source_anchors.json').write_text(json.dumps({'world':w,'observations':obs},indent=2))
