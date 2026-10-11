import numpy as np,json,hashlib
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/garden_hd_holdout_600_20261010');G=R.parent/'garden_hd_revision_20261010';d=json.load(open(G/'qa/joint_candidate_v3_conservative.json'))['fits'][1];p=np.array(d['parameters']);B=np.array(d['camera_basis_cv']);C=np.array(d['principal_point'])
def project(points):
 q=(np.array(points)-p[:3])@B.T;return q[:,:2]/q[:,2:]*p[6]+C
# Establish only facade image scale and translation. Camera pose and full v3 geometry fixed.
world=[[-3.4,.405,1.15],[3.4,.405,1.15]];original=project(world);target=np.array([[238,238],[937,238]])
a=original-original.mean(0);b=target-target.mean(0);scale=float(np.sum(a*b)/np.sum(a*a));translation=target.mean(0)-scale*original.mean(0);C2=scale*C+translation;f2=p[6]*scale
objects={
'left_window_outer_base':([-3.4-.68*.67,.405,1.15],[194,238]),'left_window_inner_base':([-3.4+.68*.67,.405,1.15],[282,238]),
'right_window_inner_base':([3.4-.68*.67,.405,1.15],[893,238]),'right_window_outer_base':([3.4+.68*.67,.405,1.15],[981,238]),
'door_left_base':([-.944,.425,.25],[495,347]),'door_right_base':([.944,.425,.25],[681,347]),
'arch_left_foot':([-2.145,-.625,.25],[322,440]),'arch_right_foot':([2.145,-.625,.25],[861,441]),
'far_left_pedestal_cap':([-5,-.025,1.73],[171,323]),'far_right_pedestal_cap':([5,-.025,1.73],[1037,331]),
}
rows=[]
for k,(w,obs)in objects.items():
 pred=scale*project([w])[0]+translation;rows.append(dict(name=k,world=w,observed=obs,predicted=pred.tolist(),residual_px=float(np.linalg.norm(pred-obs)),uncertainty_px=10 if 'arch' in k else 5,identity='nearest-to-facade urn pair predicted; source pair identity inferred from continuity and occlusion'if'pedestal'in k else'visible architectural edge or approximate foliage base'))
report=dict(source='garden_motion_sources_20261010/empty_garden_paused_core.png',source_sha256=hashlib.sha256((R.parent/'garden_motion_sources_20261010/empty_garden_paused_core.png').read_bytes()).hexdigest(),time=600.385210,paused_before_after_same=True,source_pixels=[1180,664],method='Single fit of uniform facade scale and translation from two window-base centers. Original v3 HD1326 camera pose fixed. Implemented as Blender lens and principal-point camera changes, no source-image warp. All remaining points held out.',scale=scale,translation=translation.tolist(),principal_point=C2.tolist(),lens_mm=float(f2*36/1180),shift_x=float((590-C2[0])/1180),shift_y=float((C2[1]-332)/1180),base_camera='HD1326',input_blend_sha256=hashlib.sha256((G/'models/Garden_HD_Conservative_v3_Frozen.blend').read_bytes()).hexdigest(),rows=rows,source_ratio={'window_width_to_window_centers_distance':88/699,'door_width_to_window_centers_distance':186/699,'visible_pedestal_centers_distance_to_window_centers_distance':866/699},model_ratio={'window_width_to_window_centers_distance':1.36*.67/6.8,'door_width_to_window_centers_distance':2.36*.8/6.8,'pedestal_world_x_spacing_to_window_centers_distance':10/6.8},limits=['Two window centers establish a comparison normalization, not a recovered camera. Unknown true principal point remains unresolved.','Urn pair matching is supported by visible occlusion/order; exact source asset coordinates remain unknown.','Molded facade base and cast shadows do not establish exact number of steps.'])
json.dump(report,open(R/'qa/holdout_fit.json','w'),indent=2);print(json.dumps(report,indent=2))
