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
# Only the near-right corner and two net foot positions have relatively hard image picks.
# Distant blue endpoints are partially occluded estimates, explicitly lower weight.
image_points=[('blue_near_right',[1322,655],5,'hard blue/red corner'),
              ('blue_far_left',[430,552],20,'partly occluded far boundary estimate'),
              ('blue_far_right',[1150,552],20,'partly occluded far boundary estimate'),
              ('net_left_foot',[313,585],8,'slender upright foot, assembly identity hypothesis'),
              ('net_right_foot',[1215,585],8,'padded upright foot, assembly identity hypothesis')]
world={
 'FORWARD_COURT_ORDER':[[19.5,9.5,.11],[1.5,22.5,.11],[19.5,22.5,.11],[5.8,18,.1],[18.2,18,.1]],
 'REVERSE_TRACK_SIDE':[[1.5,22.5,.11],[19.5,9.5,.11],[1.5,9.5,.11],[18.2,18,.1],[5.8,18,.1]],
}
result={};trial_log=[]
for name,xyz in world.items():
    rev=name.startswith('REVERSE');a0=math.pi if rev else 0
    xy=np.array([r[1] for r in image_points]);sigma=np.array([r[2] for r in image_points])
    lo=[-40,-60,.4,a0-.85,-.6,10];hi=[60,85,20,a0+.85,.35,120]
    def residual(p):
        uv,z=project(p,xyz)
        return np.r_[((uv-xy)/sigma[:,None]).ravel(),np.minimum(z-.1,0)*100]
    sols=[]
    for lens in [15,25,45,80]:
        initial=[10.5,40 if rev else -7,3,a0,-.05,lens]
        f=least_squares(residual,initial,bounds=(lo,hi),max_nfev=2000,ftol=1e-12,xtol=1e-12,gtol=1e-12)
        sols.append(f);trial_log.append({'hypothesis':name,'initial_lens':lens,'x':f.x.tolist(),'cost':float(f.cost),'success':bool(f.success),'message':f.message})
    fit=min(sols,key=lambda f:f.cost);p=fit.x
    fwd=np.array([math.sin(p[3])*math.cos(p[4]),math.cos(p[3])*math.cos(p[4]),math.sin(p[4])]);uv,depth=project(p,xyz)
    points=[]
    for row,w,u,z in zip(image_points,xyz,uv,depth):
        points.append({'name':row[0],'world':w,'source_xy':row[1],'manual_tolerance_px':row[2],'pick_note':row[3],'projection_xy':u.tolist(),'depth':float(z),'error_px':float(np.linalg.norm(u-row[1]))})
    result[name]={'location':p[:3].tolist(),'target':(p[:3]+fwd*30).tolist(),'lens_mm':float(p[5]),'sensor_width_mm':36,'shift_x':0,'shift_y':0,'roll':0,'parameters':p.tolist(),'fitting_points':points,'mean_error_px':float(np.mean([r['error_px'] for r in points])),'weighted_cost':float(fit.cost),'bounds':{'lower':lo,'upper':hi},'bound_hits':np.where((abs(p-np.array(lo))<1e-4)|(abs(p-np.array(hi))<1e-4))[0].tolist(),'accepted':False}
(D/'qa/camera_fit.json').write_text(json.dumps({'status':'conditional pose hypotheses, not calibration or asset acceptance','shared_geometry_commit':'87b37f98911f533605d5aebdd60756edb96fe951','hypotheses':result,'all_numeric_trials':trial_log},indent=2))
print(json.dumps(result,indent=2))
