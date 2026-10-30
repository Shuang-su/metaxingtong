"""Joint fit of frontal static anchors, shared board texture correspondences and wall corners.
No image or model per-camera modifications. Fitted parameters are an underdetermined hypothesis.
"""
import json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1]
# Read existing fit without rerunning it.
exec((ROOT/'scripts/fit_cameras.py').read_text().split('# Front anchors:')[0].replace('ROOT=Path(__file__).resolve().parents[1]',''))
cfg=json.loads((ROOT/'docs/camera-fit-front-r03.json').read_text())
feat=json.loads((ROOT/'docs/board-feature-matches.json').read_text())
names=cfg['geometry_parameter_names'];g0=np.array([cfg['geometry'][n] for n in names]);f0=np.array(cfg['front'])
front_uv=np.array([a['source_px'] for a in cfg['front_anchors']])
uv0=np.array([p['texture_xy'] for p in feat['inlier_matches']]);uv1=np.array([p['oblique_xy'] for p in feat['inlier_matches']])
def geom(g):
 h,b,w,d,y,z,wy,wh,ry,tx=g
 return np.array([[-1.03,0,b+h],[1.03,0,b+h],[-1.03,0,b],[1.03,0,b],
 [tx-w/2,y+d/2,z],[tx+w/2,y+d/2,z],[tx-w/2,y-d/2,z],[tx+w/2,y-d/2,z],[-wh,wy,.14],[wh,wy,.14],[-wh,ry,.14]])
def plane(g):
 return np.c_[uv0[:,0]/771*2-1,np.zeros(len(uv0)),g[1]+.030+(1-uv0[:,1]/408)*(g[0]-.060)]
def fitob(c):return (projection(plane(g0),c)-uv1).ravel()
best=None
for start in [[1.8,-1.3,1.45,-.7,-.1,0,1200],[1.5,-3,1.45,-.5,-.1,0,2400],[-1,-2,1.4,.3,-.1,0,2000]]:
 o=least_squares(fitob,start,bounds=([-2.2,-6,.4,-1.3,-.5,-.1,300],[2.2,-.1,2.5,1.3,.5,.1,6000]),max_nfev=5000)
 if best is None or o.cost<best.cost:best=o
ob0=best.x
def residual(v):
 cf,co,gg=v[:7],v[7:14],v[14:]
 # Static board is one plane. 177 features do not count as 177 independent baselines.
 priors=(gg-g0)/[.05,.25,.3,.3,.5,.25,.5,.3,.5,.2]
 wall=geom(gg)[[8,10]]
 return np.r_[(projection(geom(gg),cf)-front_uv).ravel(),
              ((projection(plane(gg),co)-uv1)*.22).ravel(),
              ((projection(wall,co)-[[437,908],[270,960]])*2).ravel(),priors*.5]
lo=[-.4,-6.6,.4,-.15,-.35,-.03,600, -2.2,-6,.4,-1.3,-.5,-.1,300, .9,.5,1.4,.3,-1.5,.4,.08,1.8,-.5,-.2]
hi=[.4,-3,2.5,.15,.2,.03,6000, 2.2,-.1,2.5,1.3,.5,.1,6000, 1.4,1.5,2.6,.85,-.15,1.,1.5,2.8,.6,.2]
sol=least_squares(residual,np.r_[f0,ob0,g0],bounds=(lo,hi),max_nfev=10000)
cf,co,gg=sol.x[:7],sol.x[7:14],sol.x[14:]
cfg['front']=cf.tolist();cfg['oblique']=co.tolist();cfg['geometry']=dict(zip(names,gg.tolist()))
for a,p,pred in zip(cfg['front_anchors'],geom(gg),projection(geom(gg),cf)):
 a['world']=p.tolist();a['predicted_px']=pred.tolist();a['error_px']=float(np.linalg.norm(pred-a['source_px']))
cfg.pop('oblique_anchors',None)
errs=np.linalg.norm(projection(plane(gg),co)-uv1,axis=1)
cfg['oblique_features']={'count':len(errs),'median_error_px':float(np.median(errs)),'max_error_px':float(errs.max()),'p95_error_px':float(np.quantile(errs,.95)),'source':'board-feature-matches.json'}
cfg['oblique_wall_corners']={'source_px':[[437,908],[270,960]],'predicted_px':projection(geom(gg)[[8,10]],co).tolist()}
cfg['limitations']+=['R02 joint fit uses177 matches on ONE static plane; ambiguous geometry remains','second view not complete object coverage; inferred room closure unchanged between cameras']
(ROOT/'docs/camera-fit-r03.json').write_text(json.dumps(cfg,indent=2))
print(json.dumps({k:cfg[k] for k in ['front','oblique','geometry','oblique_features','oblique_wall_corners']},indent=2))
