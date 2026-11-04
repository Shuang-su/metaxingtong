"""Conditional camera-only training diagnostic. Manual identity hypotheses, not measured calibration."""
import numpy as np,json,pathlib,hashlib
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=pathlib.Path(__file__).resolve().parents[1]
# Eleven provisional correspondences, retain all residuals including unfavorable ones.
pts=[(-2.8,1,5.35),(-2.45,1.8,5.3),(-1.4,2.6,5.5),(1.1,2.7,5.4),(2.7,1.1,5.45),(2.95,.1,5.15),(1.1,-2.65,5.05),(-.95,-2.7,5),(-2.6,-1.2,5.2),(-.25,2.85,5.4),(2.65,-1.15,5.45)]
obs=[(1770,755),(1825,735),(2190,750),(2410,850),(2420,910),(2415,1120),(1820,1220),(1640,1110),(1640,900),(2080,715),(2425,1030)]
X=np.array(pts);uv=np.array(obs);loc=np.array([11.,-15,26]);target=np.array([0,0,4.5]);z=loc-target;z/=np.linalg.norm(z);x=np.cross([0,0,1],z);x/=np.linalg.norm(x);y=np.cross(z,x);R0=np.column_stack([x,y,z]);fx=50/36*3840

def project(p):
 R=R0@Rotation.from_rotvec(p[3:]).as_matrix();q=(X-p[:3])@R;d=-q[:,2];safe=np.where(d>0,d,.001);return np.column_stack([1920+fx*q[:,0]/safe,1080-fx*q[:,1]/safe]),d,R

def fun(p):
 pred,d,R=project(p);return np.r_[(pred-uv).ravel()/40,np.minimum(d-.1,0)*100]
initial=np.r_[loc,[0,0,0]];trials=[]
for yaw in [0,-.3,.3]:
 init=initial.copy();init[5]=yaw;fit=least_squares(fun,init,bounds=([-40,-45,6,-1.3,-1.3,-1.3],[40,35,55,1.3,1.3,1.3]),loss='soft_l1',f_scale=1,max_nfev=2000,x_scale=[10,10,10,.3,.3,.3]);pred,d,R=project(fit.x);trials.append(dict(parameters=fit.x.tolist(),cost=float(fit.cost),mean_error_px=float(np.linalg.norm(pred-uv,axis=1).mean()),max_error_px=float(np.linalg.norm(pred-uv,axis=1).max()),residuals_px=(pred-uv).tolist(),projected=pred.tolist(),depths=d.tolist(),camera_to_world=R.tolist(),active_mask=fit.active_mask.tolist(),jacobian_singular_values=np.linalg.svd(fit.jac,compute_uv=False).tolist()))
baseline=project(initial);out=dict(source='sources/forest-official4k-native-503.06141.png',source_sha256=hashlib.sha256((ROOT/'sources/forest-official4k-native-503.06141.png').read_bytes()).hexdigest(),source_pixels=obs,world_hypotheses=pts,ids=['FLOWER_%02d'%i for i in range(11)],uncertainty='subjective ±40px annotation/centre definition, not statistical confidence; identity mapping provisional; cup centre not perfect projected 3D centre',focal_mm=50,sensor_width_mm=36,baseline_parameters=initial.tolist(),baseline_projected=baseline[0].tolist(),baseline_mean_px=float(np.linalg.norm(baseline[0]-uv,axis=1).mean()),trials=trials,chosen_trial=int(np.argmin([t['cost'] for t in trials])),geometry_changed=False,source_accepted=False,limits=['All points seen and used for training; no holdout','Planar-ish flower layout and approximate identities prevent unique intrinsic/extrinsic calibration','Keeps all eleven unfavorable points; newly observed white and pink flowers are included; other ambiguous small flowers remain unconfirmed','No background or world-motion calibration','New 4K cut and different timestamp, not exact original F frame','Approximate manual centres and color identity hypotheses; possible unmatched foreground cup retained in annotated uncertainty note'])
(ROOT/'qa/R09-4k-camera-training.json').write_text(json.dumps(out,indent=2)+'\n');print('baseline',out['baseline_mean_px']);print('trials',[(t['mean_error_px'],t['max_error_px']) for t in trials])
