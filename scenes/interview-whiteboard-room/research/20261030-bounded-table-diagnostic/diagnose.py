"""Bounded, local pinhole projection diagnostic; never changes R05 or renders a scene.

Step 1: fixed R05 geometry, static frame/stand/wall camera fit. Table is held out.
Step 2: fixed fitted cameras, only shared table depth/x/y. Failed trials are retained.
Axes, principal point and all other geometry remain the R05 assumptions.
"""
import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares, minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CFG = json.loads((ROOT/'docs/camera-fit-r03.json').read_text())
G = CFG['geometry']
FEATURES = json.loads((ROOT/'docs/board-feature-matches.json').read_text())['inlier_matches']
FROZEN_HEAD = '0c6280de6c33099d7b3cff8e2fe0103bc9ed0381'

def save(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def basis(c):
    x, y, z, yaw, pitch, roll, f = c
    fw = np.array([np.sin(yaw)*np.cos(pitch), np.cos(yaw)*np.cos(pitch), np.sin(pitch)])
    rt = np.array([np.cos(yaw), -np.sin(yaw), 0.])
    up = np.cross(rt, fw)
    return rt*np.cos(roll)+up*np.sin(roll), -rt*np.sin(roll)+up*np.cos(roll), fw

def project(points, c):
    r, u, fw = basis(c)
    p = np.asarray(points)-c[:3]
    d = p@fw
    return np.c_[960+c[6]*(p@r)/d, 540-c[6]*(p@u)/d]

def point(label, xyz, uv, sigma, group):
    return dict(id=label, world=xyz, source_px=uv, uncertainty_px=sigma, group=group)

# Annotation was fixed by direct native-source inspection, before fitting this stage.
# Frame corners are intersections of straight segment CENTRE lines, not rounded caps.
# Pixel uncertainty is a diagnostic tolerance, not a statistical confidence interval.
bb, bh = G['board_bottom'], G['board_height']
bc = bb+bh/2
wh, wy, ry = G['wall_half'], G['wall_y'], G['return_y']
FRONT = [point('frame virtual '+n, [x,-.015,z], uv, 3., 'frame') for n,x,z,uv in [
    ('TL',-1.0155,bb+bh-.0145,[572,167]), ('TR',1.0155,bb+bh-.0145,[1367,167]),
    ('BL',-1.0155,bb+.0145,[572,595]), ('BR',1.0155,bb+.0145,[1367,595])]]
FRONT += [point('left pivot',[-1.065,.012,bc+.015],[559,393],7.,'stand'),
          point('right pivot',[1.065,.012,bc+.015],[1379,393],7.,'stand'),
          point('left clamp',[-1.065,-.005,bb-.145],[560,654],5.,'stand'),
          point('right clamp',[1.065,-.005,bb-.145],[1379,654],5.,'stand'),
          point('left rear skirting',[-wh,wy,.14],[160,852],4.,'wall'),
          point('right rear skirting',[wh,wy,.14],[1757,852],4.,'wall'),
          point('left return skirting',[-wh,ry,.14],[113,875],4.,'wall')]
OBLIQUE = [point('left pivot',[-1.065,.012,bc+.015],[804,239],7.,'stand'),
           point('left clamp',[-1.065,-.005,bb-.145],[812,681],5.,'stand'),
           point('left rear skirting',[-wh,wy,.14],[437,908],4.,'wall'),
           point('left return skirting',[-wh,ry,.14],[270,960],4.,'wall')]

# Visible frame centreline samples. Each uses distance to a projected 3D line,
# not a fabricated point-to-point correspondence along an edge.
OB_LINES = [dict(id='left frame centre', world=[[-1.0155,-.015,bb+.055],[-1.0155,-.015,bb+bh-.055]],
                 source_px=[[823,50],[820,400],[818,540]],uncertainty_px=4.,group='frame'),
            dict(id='bottom frame centre',world=[[-.975,-.015,bb+.0145],[.975,-.015,bb+.0145]],
                 source_px=[[862,582],[1820,601]],uncertainty_px=4.,group='frame')]

def line_errors(c, lines):
    out=[]
    for a in lines:
        p,q=project(a['world'],c)
        d=q-p
        v=np.asarray(a['source_px'])-p
        e=(v[:,0]*d[1]-v[:,1]*d[0])/np.linalg.norm(d)
        out.extend(e/a['uncertainty_px'])
    return np.array(out)

# Spread actual matched text features over the visible plane; cap their weight.
# They check the plane, not independent 3D baselines. Unselected matches validate it.
tex=np.array([m['texture_xy'] for m in FEATURES])
obs=np.array([m['oblique_xy'] for m in FEATURES])
selected=[int(np.argmin(tex[:,0]))]
for _ in range(15):
    d=((tex[:,None,:]-tex[selected][None,:,:])**2).sum(axis=2).min(axis=1)
    selected.append(int(np.argmax(d)))
plane=np.c_[tex[:,0]/771*2-1,np.full(len(tex),-.0005),bb+.030+(1-tex[:,1]/408)*(bh-.060)]

def anchor_residual(c, view):
    anchors=FRONT if view=='front' else OBLIQUE
    e=(project([a['world'] for a in anchors],c)-[a['source_px'] for a in anchors])
    r=(e/np.array([a['uncertainty_px'] for a in anchors])[:,None]).ravel()
    if view=='oblique':
        r=np.r_[r,line_errors(c,OB_LINES),((project(plane[selected],c)-obs[selected])/3.).ravel()*.4]
    return r

def anchor_stats(c, view):
    anchors=FRONT if view=='front' else OBLIQUE
    pred=project([a['world'] for a in anchors],c)
    rows=[]
    for a,p in zip(anchors,pred):
        e=float(np.linalg.norm(p-a['source_px']))
        rows.append(dict(**a,predicted_px=p.tolist(),error_px=e,normalized_error=e/a['uncertainty_px']))
    lines=[]
    if view=='oblique':
        for a in OB_LINES:
            e=line_errors(c,[a])*a['uncertainty_px']
            lines.append(dict(**a,error_px=e.tolist()))
    feature_errors=np.linalg.norm(project(plane,c)-obs,axis=1) if view=='oblique' else None
    gate=all(a['normalized_error']<=2 for a in rows) and all(max(abs(np.array(a['error_px'])))<=2*a['uncertainty_px'] for a in lines)
    return dict(points=rows,lines=lines,manual_anchor_gate_2x_tolerance=bool(gate),
                normalized_rms=float(np.sqrt(np.mean(anchor_residual(c,view)**2))),
                features=None if feature_errors is None else dict(count=len(feature_errors),median_px=float(np.median(feature_errors)),p95_px=float(np.quantile(feature_errors,.95))))

TABLE_UV=np.array([[546,712],[1353,712],[488,750],[1407,750]],float)
T0=np.array([G['table_depth'],G['table_x'],G['table_y']])

def table_corners(t):
    d,x,y=t; w,z=G['table_width'],G['table_z']
    return np.array([[x-w/2,y+d/2,z],[x+w/2,y+d/2,z],[x-w/2,y-d/2,z],[x+w/2,y-d/2,z]])

def table_feet(t):
    d,x,y=t;w=G['table_width']
    return np.array([[x-w/2+.065,y-d/2+.052,0],[x+w/2-.065,y-d/2+.052,0]])

def table_boxes(t):
    d,x,y=t;w,z=G['table_width'],G['table_z']
    boxes=[([x-w/2,y-d/2,z-.028],[x+w/2,y+d/2,z])]
    for xx in [x-w/2+.065,x+w/2-.065]:
        for yy in [y-d/2+.052,y+d/2-.052]:
            boxes.append(([xx-.0225,yy-.0225,0],[xx+.0225,yy+.0225,z-.028]))
    for yy in [y-d/2+.052,y+d/2-.052]:
        boxes.append(([x-(w-.09)/2,yy-.0175,z-.064],[x+(w-.09)/2,yy+.0175,z-.028]))
    for xx in [x-w/2+.065,x+w/2-.065]:
        boxes.append(([xx-.0175,y-(d-.08)/2,z-.064],[xx+.0175,y+(d-.08)/2,z-.028]))
    return np.array(boxes)

# Entire rectangle is visibly table-free in the oblique native source.
# Avoid character and board upright at x~808. Samples at 5 px, inclusive bounds.
EMPTY_RECT=[140,795,780,1070]
ex,ey=np.meshgrid(np.arange(140,781,5),np.arange(795,1071,5))
EMPTY_UV=np.c_[ex.ravel(),ey.ravel()]

def empty_hits(t,c):
    r,u,fw=basis(c)
    rays=fw+(EMPTY_UV[:,0,None]-960)/c[6]*r-(EMPTY_UV[:,1,None]-540)/c[6]*u
    hits=np.zeros(len(rays),bool)
    for lo,hi in table_boxes(t):
        q1=(lo-c[:3])/rays;q2=(hi-c[:3])/rays
        near=np.minimum(q1,q2).max(axis=1);far=np.maximum(q1,q2).min(axis=1)
        hits|=far>=np.maximum(near,0)
    return hits

def table_stats(t,cf,co):
    uv=project(table_corners(t),cf)
    errs=np.linalg.norm(uv-TABLE_UV,axis=1)
    feet=project(table_feet(t),cf)
    hits=empty_hits(t,co)
    return dict(table_parameters=dict(zip(['depth','x','y'],map(float,t))),
                front_corners_px=uv.tolist(),front_corner_errors_px=errs.tolist(),
                front_corner_rms_px=float(np.sqrt(np.mean(errs**2))),
                front_feet_px=feet.tolist(),front_feet_bottom_deficit_px=np.maximum(1080-feet[:,1],0).tolist(),
                oblique_table_free_rect_px=EMPTY_RECT,oblique_free_samples=len(hits),
                oblique_wrong_table_samples=int(hits.sum()),oblique_wrong_table_fraction=float(hits.mean()))

BOUNDS={
 'front': ([-.7,-6.8,.6,-.2,-.25,-.04,800],[.7,-2.5,2.,.2,.2,.04,5000]),
 'oblique': ([-1.8,-6.8,.6,-1.2,-.3,-.05,500],[1.8,-.3,2.,1.2,.3,.05,6000])}

def camera_phase():
    results={}
    for view in ['front','oblique']:
        c0=np.array(CFG[view]);lo,hi=map(np.array,BOUNDS[view]);trials=[]
        starts=[c0,c0*np.array([1,.9,1,1,1,1,.9]),c0*np.array([1,1.07,1,1,1,1,1.07])]
        for i,start in enumerate(starts):
            fit=least_squares(anchor_residual,np.clip(start,lo+1e-6,hi-1e-6),args=(view,),bounds=(lo,hi),max_nfev=1000,x_scale='jac',ftol=1e-11,xtol=1e-11,gtol=1e-11)
            trials.append(dict(id=f'{view}-camera-only-seed-{i}',parameters=fit.x.tolist(),cost=float(fit.cost),nfev=fit.nfev,success=bool(fit.success),message=fit.message,anchors=anchor_stats(fit.x,view)))
        best=min(trials,key=lambda a:a['cost'])
        cb=np.array(best['parameters'])
        # Bounded focal profile: all six extrinsics re-fit, fixed geometry.
        profile=[]
        for multiplier in [.90,.95,1.,1.05,1.10]:
            f=cb[6]*multiplier
            fit=least_squares(lambda x:anchor_residual(np.r_[x,f],view),cb[:6],bounds=(lo[:6],hi[:6]),max_nfev=500,x_scale='jac')
            cp=np.r_[fit.x,f]
            profile.append(dict(focal_multiplier=multiplier,parameters=cp.tolist(),cost=float(fit.cost),nfev=fit.nfev,success=bool(fit.success),anchors=anchor_stats(cp,view)))
        results[view]=dict(baseline_parameters=c0.tolist(),baseline_anchors=anchor_stats(c0,view),trials=trials,best=best,focal_profile=profile)
    cf=np.array(results['front']['best']['parameters']);co=np.array(results['oblique']['best']['parameters'])
    results['held_out_table']=dict(r05=table_stats(T0,np.array(CFG['front']),np.array(CFG['oblique'])),camera_only=table_stats(T0,cf,co))
    results['focal_profile_held_out']={view:[dict(focal_multiplier=p['focal_multiplier'],anchors_pass=p['anchors']['manual_anchor_gate_2x_tolerance'],table=table_stats(T0,np.array(p['parameters']) if view=='front' else cf,np.array(p['parameters']) if view=='oblique' else co)) for p in results[view]['focal_profile']] for view in ['front','oblique']}
    results['recorded_at_utc']=datetime.now(timezone.utc).isoformat()
    results['frozen_head']=FROZEN_HEAD
    results['geometry_changed']=False
    save('camera-only-results.json',results)
    save('annotations-and-method.json',dict(frozen_head=FROZEN_HEAD,units='arbitrary model units',front=FRONT,oblique=OBLIQUE,oblique_lines=OB_LINES,plane_feature_indices=selected,
        table_corners_held_out_px=TABLE_UV.tolist(),front_foot_constraint='foot endpoints not observed; y >= 1080 is only a lower bound, no true leg length measured',
        oblique_clear_rect=EMPTY_RECT,empty_sample_step_px=5,table_boxes='conservative unbeveled AABBs; rays before the known background; exact small bevel not modeled in diagnostic',
        bounds=BOUNDS,limitations=['fixed R05 metric-free geometry is only one hypothesis','front virtual frame corners extrapolate line centres, not rounded cap tips','stand sections/depths partly inferred; tolerance is not confidence','principal point fixed 960,540; zero lens distortion assumed','177 text matches share one plane; only 16 spatially spread features contribute weakly to fit','no table source observations enter camera optimization','no character dimensions or landmarks enter fitting','no image warping, per-camera geometry, hidden objects, or new temporal state']))
    print(json.dumps(results['held_out_table'],indent=2))
    print('STATIC ANCHOR GATES',[(v,results[v]['best']['anchors']['manual_anchor_gate_2x_tolerance']) for v in ['front','oblique']])

def clip_polygon(poly, value):
    """Keep vertices where value >= 0, interpolating actual polygon intersections."""
    result=[]
    if len(poly)==0:return np.empty((0,3))
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        va,vb=value(a),value(b)
        if va>=0:result.append(a)
        if (va>=0)!=(vb>=0):result.append(a+(b-a)*va/(va-vb))
    return np.array(result)

def top_intrusion_fraction(t,c):
    """Projected top surface only: continuous lower bound on wrong table silhouette."""
    poly=table_corners(t)[[0,1,3,2]]
    fw=basis(c)[2]
    poly=clip_polygon(poly,lambda p:(p-c[:3])@fw-.01)
    if len(poly)<3:return 0.
    poly=project(poly,c)
    x0,y0,x1,y1=EMPTY_RECT
    for axis,bound,sign in [(0,x0,1),(0,x1,-1),(1,y0,1),(1,y1,-1)]:
        poly=clip_polygon(poly,lambda p:sign*(p[axis]-bound))
        if len(poly)<3:return 0.
    area=abs(np.sum(poly[:,0]*np.roll(poly[:,1],-1)-poly[:,1]*np.roll(poly[:,0],-1)))/2
    return float(area/((x1-x0)*(y1-y0)))

def table_phase():
    cameras=json.loads((HERE/'camera-only-results.json').read_text())
    bounds=[(.30,1.60),(-.25,.25),(-2.20,-.35)]
    rear_limit=T0[2]+T0[0]/2
    # Conservative envelope: table rear edge never advances toward the fixed chair
    # back / whiteboard; legs stay outside fixed chair width. This is not mesh QA.
    rear=lambda t:rear_limit-(t[2]+t[0]/2)
    starts=[T0,np.array([.4,-.05,-.9]),np.array([1.2,-.05,-1.4])]
    results={}
    for family in ['r05','failed_camera_only']:
        if family=='r05':cf,co=map(lambda v:np.array(CFG[v]),['front','oblique'])
        else:cf,co=map(lambda v:np.array(cameras[v]['best']['parameters']),['front','oblique'])
        def front_rms(t):return float(np.sqrt(np.mean(np.sum((project(table_corners(t),cf)-TABLE_UV)**2,axis=1))))
        def foot_deficit(t):return float(np.maximum(1080-project(table_feet(t),cf)[:,1],0).max())
        def objective(t,kind):
            if kind=='front_only':return front_rms(t)**2
            if kind=='min_top_intrusion_front6':return top_intrusion_fraction(t,co)
            if kind=='min_foot_deficit_front6':return foot_deficit(t)
            if kind=='joint_tradeoff':return (front_rms(t)/6)**2+(foot_deficit(t)/15)**2+(top_intrusion_fraction(t,co)/.1)**2
            raise ValueError(kind)
        trials=[]
        for kind in ['front_only','min_top_intrusion_front6','min_foot_deficit_front6','joint_tradeoff']:
            constraints=[dict(type='ineq',fun=rear)]
            if kind in ['min_top_intrusion_front6','min_foot_deficit_front6']:
                constraints.append(dict(type='ineq',fun=lambda t:6-front_rms(t)))
            for i,start in enumerate(starts):
                fit=minimize(lambda t:objective(t,kind),start,method='SLSQP',bounds=bounds,constraints=constraints,options=dict(maxiter=150,ftol=1e-9))
                t=fit.x
                stats=table_stats(t,cf,co)
                trials.append(dict(id=f'{family}-{kind}-{i}',objective=kind,parameters=t.tolist(),success=bool(fit.success),message=fit.message,nit=fit.nit,
                    cost=float(fit.fun),rear_envelope_clearance=float(rear(t)),front6_feasible=bool(front_rms(t)<=6.001),
                    oblique_top_intrusion_area_fraction=top_intrusion_fraction(t,co),table=stats))
        # An explicit coarse grid checks the bounded search shape, not exhaustiveness.
        # Values include the R05 depth and x/y. All rejected envelope trials retained.
        grid=[]
        for d,x,y in itertools.product([.3,.45,.6,float(T0[0]),.9,1.05,1.2,1.4,1.6],[-.25,float(T0[1]),.25],[-2.2,-1.8,-1.4,-1.1,-.9,float(T0[2]),-.65,-.5,-.35]):
            t=np.array([d,x,y])
            grid.append(dict(parameters=t.tolist(),rear_envelope_pass=bool(rear(t)>=-1e-8),front_corner_rms_px=front_rms(t),
                front_foot_deficit_max_px=foot_deficit(t),oblique_top_intrusion_area_fraction=top_intrusion_fraction(t,co)))
        results[family]=dict(front_camera=cf.tolist(),oblique_camera=co.tolist(),baseline=table_stats(T0,cf,co),
                            baseline_top_intrusion_fraction=top_intrusion_fraction(T0,co),optimization_trials=trials,coarse_grid=grid)
    results['method']=dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),frozen_head=FROZEN_HEAD,
        shared_parameters=['depth','x','y'],bounds=bounds,constant_dimensions={'width':G['table_width'],'top_z':G['table_z'],'top_thickness':.028},
        rear_edge_max_y=float(rear_limit),floor_contact='leg length / pads unchanged; bottom z=0 in analytic model',
        optimizer_budget='2 camera families x 4 objectives x 3 starts, max150 SLSQP iterations; 243 coarse grid trials per family',
        gate='static frame/stand/wall anchors must pass before model candidate; front corner RMS <=6px is a diagnostic constraint, not acceptance',
        caveats=['R05 cameras were previously fitted with front tabletop anchors: baseline front corners are not independent evidence',
                 'all three table parameters shared across views; no width/height change, no per-camera object state',
                 'top area fraction is lower bound on wrong table silhouette, not full image score; box-ray check includes table frame',
                 'table-free rectangle is observed wall/skirting/floor, not character region',
                 'frozen wall/board/stand geometry is itself conditional and static-anchor gates failed; no resulting table may be promoted',
                 'bounds and pinhole assumptions limit conclusion; no proof that every possible shared scene is impossible',
                 'analytic no-new-rear-overlap envelope is conservative; no revised mesh was built or collision-certified'])
    save('shared-table-results.json',results)
    for family in ['r05','failed_camera_only']:
        print(family)
        for kind in ['front_only','min_top_intrusion_front6','min_foot_deficit_front6','joint_tradeoff']:
            trials=[a for a in results[family]['optimization_trials'] if a['objective']==kind]
            a=min(trials,key=lambda a:a['cost']);s=a['table']
            print(kind,'success',a['success'],'params',a['parameters'],'front RMS',round(s['front_corner_rms_px'],3),'foot deficits',s['front_feet_bottom_deficit_px'],'top wrong',round(a['oblique_top_intrusion_area_fraction'],3),'full box wrong',round(s['oblique_wrong_table_fraction'],3))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['camera','table'])
    args=parser.parse_args()
    if args.phase=='camera':camera_phase()
    else:table_phase()
