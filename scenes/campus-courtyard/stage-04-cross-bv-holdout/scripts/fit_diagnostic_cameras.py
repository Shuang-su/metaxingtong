"""Camera-only hypothesis test. Geometry is frozen; picked identities are conditional.
No actor anchors, image warps, source textures, or model mutation.
Pixel uncertainties are manual reading tolerance, not statistical calibration.
"""
import json,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
D=Path(__file__).resolve().parents[1]
def project(p,xyz):
    x,y,z,a,e,l=p
    forward=np.array([math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)])
    right=np.array([math.cos(a),-math.sin(a),0]);up=np.cross(right,forward)
    v=np.array(xyz)-[x,y,z];depth=v@forward;f=l*1920/36
    return np.c_[960+f*(v@right)/depth,540-f*(v@up)/depth],depth
# After independent review the occluded far-right corner is removed, not imputed.
# Earlier five-point fit is retained under trials/ as a rejected measurement attempt.
# Three better defined points alone locate a conditional camera. The uncertain far-left
# corner and all separate object groups are withheld. Fixed focal lengths test sensitivity.
image_points=[('blue_near_right',[1322,655],8,'hard blue/red corner'),
              ('net_left_foot',[311,586],10,'slender upright foot, assembly identity hypothesis'),
              ('net_right_foot',[1215,586],10,'padded upright foot, assembly identity hypothesis')]
world={
 'FORWARD_COURT_ORDER':[[19.5,9.5,.11],[5.8,18,.1],[18.2,18,.1]],
 'REVERSE_TRACK_SIDE':[[1.5,22.5,.11],[18.2,18,.1],[5.8,18,.1]],
}
result={};trial_log=[]
for name,xyz in world.items():
 for fixed_lens in [20,35,50]:
    rev=name.startswith('REVERSE');a0=math.pi if rev else 0
    xy=np.array([r[1] for r in image_points]);sigma=np.array([r[2] for r in image_points])
    lo=[-60,-90,.15,a0-1.1,-.8];hi=[80,100,30,a0+1.1,.6]
    def residual(v):
        p=np.r_[v,fixed_lens]
        uv,z=project(p,xyz)
        return np.r_[((uv-xy)/sigma[:,None]).ravel(),np.minimum(z-.1,0)*100]
    sols=[]
    for delta in [-.3,0,.3]:
        initial=[10.5,40 if rev else -7,3,a0+delta,-.05]
        f=least_squares(residual,initial,bounds=(lo,hi),max_nfev=2000,ftol=1e-12,xtol=1e-12,gtol=1e-12)
        sols.append(f);trial_log.append({'hypothesis':name,'fixed_lens':fixed_lens,'initial_azimuth_delta':delta,'x':f.x.tolist(),'cost':float(f.cost),'success':bool(f.success),'message':f.message})
    fit=min(sols,key=lambda f:f.cost);p=np.r_[fit.x,fixed_lens]
    fwd=np.array([math.sin(p[3])*math.cos(p[4]),math.cos(p[3])*math.cos(p[4]),math.sin(p[4])]);uv,depth=project(p,xyz)
    points=[]
    for row,w,u,z in zip(image_points,xyz,uv,depth):
        points.append({'name':row[0],'world':w,'source_xy':row[1],'manual_tolerance_px':row[2],'pick_note':row[3],'projection_xy':u.tolist(),'depth':float(z),'error_px':float(np.linalg.norm(u-row[1]))})
    far_world=[19.5,9.5,.11] if rev else [1.5,22.5,.11];far_uv,far_z=project(p,[far_world])
    result[name+'_F'+str(fixed_lens)]={'location':p[:3].tolist(),'target':(p[:3]+fwd*30).tolist(),'lens_mm':float(p[5]),'sensor_width_mm':36,'shift_x':0,'shift_y':0,'roll':0,'parameters':p.tolist(),'fitting_points':points,'mean_error_px':float(np.mean([r['error_px'] for r in points])),'weighted_cost':float(fit.cost),'bounds':{'lower':lo,'upper':hi},'bound_hits':np.where((abs(p[:5]-np.array(lo))<1e-4)|(abs(p[:5]-np.array(hi))<1e-4))[0].tolist(),'heldout_far_left':{'world':far_world,'source_xy':[426,552],'tolerance_px':12,'projection_xy':far_uv[0].tolist(),'depth':float(far_z[0]),'error_px':float(np.linalg.norm(far_uv[0]-[426,552]))},'accepted':False}
(D/'qa/camera_fit.json').write_text(json.dumps({'status':'conditional pose hypotheses, not calibration or asset acceptance','shared_geometry_commit':'87b37f98911f533605d5aebdd60756edb96fe951','hypotheses':result,'all_numeric_trials':trial_log},indent=2))
print(json.dumps({k:{kk:v[kk] for kk in ['location','lens_mm','mean_error_px','heldout_far_left','bound_hits']} for k,v in result.items()},indent=2))
