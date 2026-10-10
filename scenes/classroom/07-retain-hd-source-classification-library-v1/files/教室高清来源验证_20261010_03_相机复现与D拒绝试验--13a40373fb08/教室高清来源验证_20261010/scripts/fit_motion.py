import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pathlib import Path
p=Path('classroom_hd_alignment_20261010')
r=json.load(open(p/'qa/scene_inspection.json'));cam=next(c for c in r['cameras'] if c['name']=='SOURCE_C')
# Native 1180x664 source coordinates, hand-picked visible physical boundaries; no image warp.
a=[('board_TL',[1.9,.084,2.060728],[274,123]),('board_TR',[-1.9,.084,2.060728],[961,127]),('board_BL',[1.9,.084,.593477],[274,397]),('board_BR',[-1.9,.084,.593477],[958,400]),('bookshelf_TR',[2.287747,.458706,1.783019],[152,165]),('bookshelf_BR',[2.287747,.458706,.004225],[156,520]),('teacher_front_left',[-.363664,2.074549,.846306],[716,414]),('teacher_front_right',[-1.279898,2.074549,.846306],[1007,414]),('clock_center',[-1.82,.1065,2.340059],[948,61])]
X=np.array([x[1] for x in a]);uv=np.array([x[2] for x in a]);train=np.array([0,1,2,3,4,6,7]);hold=np.array([5,8])
def project(v):
 R=Rotation.from_euler('xyz',v[3:6]).as_matrix();q=(X-v[:3])@R;return np.stack([590+v[6]*q[:,0]/-q[:,2],332-v[6]*q[:,1]/-q[:,2]],axis=1)
v=np.r_[cam['location'],cam['rotation'],1180*cam['lens']/36];v[1]=5;v[2]=1.35;v[6]=950
fit=least_squares(lambda v:(project(v)[train]-uv[train]).ravel(),v,max_nfev=1000)
e=np.linalg.norm(project(fit.x)-uv,axis=1)
out={'source':'xingtong_classroom_browser/hd_recapture/crops/classroom_motion_4282_video.png','camera_location':fit.x[:3].tolist(),'camera_rotation_xyz':fit.x[3:6].tolist(),'lens_mm':fit.x[6]*36/1180,'sensor_width_mm':36,'render_resolution':[1180,664],'fit_rms_px':float(np.sqrt(np.mean(e[train]**2))),'holdout_rms_px':float(np.sqrt(np.mean(e[hold]**2))),'points':[{'label':x[0],'world':x[1],'source_px':x[2],'projected_px':project(fit.x)[i].tolist(),'error_px':float(e[i]),'role':'fit' if i in train else 'holdout'} for i,x in enumerate(a)],'limitations':'Manual landmarks ~2-4px uncertainty. Camera-only fit to fixed approximate geometry. Focal-distance coupling; no calibrated ground truth.'}
(p/'qa/motion_camera_fit.json').write_text(json.dumps(out,indent=2));print(out)
