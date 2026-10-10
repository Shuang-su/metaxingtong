import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pathlib import Path
p=Path('classroom_motion_validation_20261010');cams={c['name']:c for c in json.load(open('classroom_hd_alignment_20261010/qa/scene_inspection.json'))['cameras']};delta=2.3264917179671376
b=next(y for y in json.load(open('classroom_hd_alignment_20261010/qa/new_source_anchor_errors.json')) if y['camera']['name']=='SOURCE_B');X=np.array([q['world'] for q in b['points']]);X[:,1]-=delta;Y=np.array([q['source_px'] for q in b['points']]);c=cams['SOURCE_B'];v0=np.r_[c['location'],c['rotation'],c['lens']/36*1180];v0[1]-=delta
# pinhole principal point fixed at native image centre. No image warp.
def proj(X,v):
 q=(X-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix();return np.stack([590+v[6]*q[:,0]/-q[:,2],332-v[6]*q[:,1]/-q[:,2]],1)
results=[]
for lens in [16,20,24,28,32,38.41616,45,55,65,85]:
 f=lens/36*1180;fit=least_squares(lambda z:(proj(X,np.r_[z,f])-Y).ravel(),v0[:6],max_nfev=2500);v=np.r_[fit.x,f];results.append({'lens_mm':lens,'location':v[:3].tolist(),'rotation':v[3:6].tolist(),'rms_px':float(np.sqrt(np.mean(np.sum((proj(X,v)-Y)**2,axis=1))))})
fit=least_squares(lambda v:(proj(X,v)-Y).ravel(),v0,max_nfev=4000);v=fit.x
out={'six_bay_B_window_only_free_lens':{'location':v[:3].tolist(),'rotation':v[3:6].tolist(),'lens_mm':float(v[6]*36/1180),'rms_px':float(np.sqrt(np.mean(np.sum((proj(X,v)-Y)**2,axis=1))))},'fixed_lens_profile':results,'warning':'Six coplanar old window anchor picks only; no independent table identity or 3D baseline. Lens-distance ambiguity and source/model frame geometry error must not become assumed furniture displacement.'}
# independent front16: first opening jamb and bookcase link two wall orientations
X=np.array([[3.049261,.458706,1.783019],[2.287747,.458706,1.783019],[3.049261,.458706,.004225],[2.287747,.458706,.004225],[4.050608,.791384,1.827585],[4.050608,.791384,.65312],[4.050608,1.373007,1.827585]])
Y=np.array([[797,242],[976,228],[794,655],[981,693],[560,239],[560,488],[466,213]],float);Y[:,1]-=47
best=None
for n in ['SOURCE_B','SOURCE_4298','SOURCE_4300']:
 c=cams[n];v0=np.r_[c['location'],c['rotation'],c['lens']/36*1180];fit=least_squares(lambda v:(proj(X,v)-Y).ravel(),v0,max_nfev=5000)
 if fit.x[6]>100 and (best is None or fit.cost<best.cost):best=fit
v=best.x;R=Rotation.from_euler('xyz',v[3:6]).as_matrix();desk=[]
for pix in [[95,650],[255,613],[462,667],[244,708]]:
 u,w=np.array(pix)-[0,47];ray=R@np.array([(u-590)/v[6],-(w-332)/v[6],-1]);pt=v[:3]+(.695485-v[2])/ray[2]*ray;desk.append({'image_px_raw':pix,'world_at_assumed_desk_height':pt.tolist()})
out['front16_two_wall_fit']={'location':v[:3].tolist(),'rotation':v[3:6].tolist(),'lens_mm':float(v[6]*36/1180),'rms_px':float(np.sqrt(np.mean(np.sum((proj(X,v)-Y)**2,axis=1)))),'source_points':Y.tolist(),'world_points':X.tolist(),'desk_plane_backprojections':desk,'warning':'Exploratory only: blurred bookcase edges and inferred metric window dimensions. Desktop height held to existing model, no desk geometry changed.'}
(p/'qa/B_camera_identity_exploration.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
