"""Numeric proxy only: 3 shared vent parameters, never per-view geometry.
Does not edit BLEND, source pixels or current candidate. A physical rebuild would need
the matching fascia aperture, cavity and louvers reconstructed as one module.
"""
import json,math,numpy as np
from scipy.optimize import least_squares
from pathlib import Path
import fit_cameras as f
R=Path(__file__).resolve().parent
base=json.loads((R/'camera_only_fit.json').read_text());ids=['S01','S02','S03'];original={k:json.loads(json.dumps(v)) for k,v in f.G['states'].items()}
def apply_proxy(g):
 tilt,scale,dz=g;co,si=math.cos(tilt),math.sin(tilt);rot=np.array([[1,0,0],[0,co,-si],[0,si,co]])
 for frame,source in original.items():
  center=np.array(source['vent_center']);circle=np.array(source['vent_rim']);new=center+np.array([0,0,dz]);f.G['states'][frame]['vent_center']=new.tolist();f.G['states'][frame]['vent_rim']=((circle-center)@rot.T*scale+new).tolist()
def residual(p):
 apply_proxy(p[-3:]);out=[]
 for i,id in enumerate(ids):out.extend(f.residual(p[i*7:i*7+7],id))
 return np.array(out)
lo=[-3.5,-1.7,1.04,-1.1,-.55,-.20,14]*3+[math.radians(-45),.5,-.18]
hi=[.50,1.40,1.58,1.1,.55,.20,70]*3+[math.radians(45),1.5,.18]
p=np.array(sum([base['results'][id]['fitted_camera'] for id in ids],[])+[math.radians(-20),.85,.04])
fits=[]
for start in [(0,1,0),(-20,.85,.04),(-35,.7,.08),(20,.9,-.04)]:
 seed=p.copy();seed[-3:]=[math.radians(start[0]),start[1],start[2]]
 fit=least_squares(residual,seed,bounds=(lo,hi),loss='linear',max_nfev=700,xtol=1e-9,ftol=1e-9,gtol=1e-9);fits.append(fit)
best=min(fits,key=lambda x:x.cost);p=best.x;apply_proxy(p[-3:]);rows={}
for i,id in enumerate(ids):rows[id]={'camera':p[i*7:i*7+7].tolist(),'features':f.summary(p[i*7:i*7+7],id)}
report={'scope':'Three shared vent proxy parameters + independent cameras; numeric hypothesis only, geometry files unchanged. Matching aperture/cavity/louvers would have to change together in a future physical rebuild. No per-view vertex motion.','parameters':{'vent_module_tilt_X_degrees':math.degrees(p[-3]),'uniform_radius_scale':p[-2],'center_delta_z_model_units':p[-1]},'bounds_active':np.where(np.isclose(p,lo,atol=.002)|np.isclose(p,hi,atol=.002))[0].tolist(),'results':rows,'not_accepted':True,'reason':'Single-feature module correction cannot establish cabin-wide geometry, visibility or source acceptance; inspect held-out and A-pillar residuals'}
(R/'shared_vent_hypothesis_numeric_only.json').write_text(json.dumps(report,indent=2)+'\n');print(report['parameters']);print('active',report['bounds_active'])
for id,row in rows.items():print(id,{name:round(v['rms_pixels'],1) for name,v in row['features'].items()})
