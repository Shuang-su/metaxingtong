import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from pathlib import Path
r=Path(__file__).resolve().parents[1];j=json.loads((r/'evidence/inner-arch-soft-fragments.json').read_text());pts=[np.array(sum(list(g.values()),[])) for g in j['source_groups'].values()];cam=json.loads((r/'qa/platform-camera-conditional-fit.json').read_text())['distance_branches'][0]['params'];theta=np.linspace(0,np.pi,2400)
def project(xyz,D,el,az,f,cx,cy,roll=0):
 right=np.array([np.cos(az),np.sin(az),0]);back=np.array([-np.sin(az)*np.cos(el),np.cos(az)*np.cos(el),-np.sin(el)]);up=np.array([-np.sin(az)*np.sin(el),np.cos(az)*np.sin(el),np.cos(el)]);den=D+xyz@back;u=f*(xyz@right)/den;v=-f*(xyz@up)/den;return np.array([cx+u*np.cos(roll)-v*np.sin(roll),cy+u*np.sin(roll)+v*np.cos(roll)]).T
# p: 4k azimuth, arch planeY, circle centerZ, outer radius, front D/el/f/cy.
def contours(p):
 az,y,z,R,D,e,f,cy=p; xyz=np.c_[R*np.cos(theta),np.full(theta.shape,y),z+R*np.sin(theta)]
 return [project(xyz,30,cam[0],az,cam[1],cam[2],cam[3],cam[7]),project(xyz,D,e,0,f,960,cy)]
def residual(p):
 qs=contours(p);rr=[]
 for q,obs,s in zip(qs,pts,[30,18]):rr.extend(cKDTree(q).query(obs)[0]/s)
 # Sole extra front platform observation is weak rear top lip, not whole ellipse.
 rt,zt=cam[4:6];q=project(np.array([[0,rt,zt]]),p[4],p[5],0,p[6],960,p[7]);rr.append((q[0,1]-910)/35)
 # Explicit broad regularization, not source fact.
 rr.extend([(p[1]-6)/10,(p[2]-3)/7,(p[3]-6)/8,(p[4]-10)/20,(p[6]-1500)/2500])
 return rr
p0=[-.7,6,3,6,10,.14,1500,1150];sol=least_squares(residual,p0,bounds=([-1.2,1,.1,2,3,-.2,400,700],[-.1,15,7,12,35,.5,6000,2000]),max_nfev=450,diff_step=1e-4)
out={'params_order':['azimuth4k','arch_plane_y','arch_center_z','arch_outer_radius','front_camera_D','front_camera_elevation','front_focal_px','front_principal_y'],'params':sol.x.tolist(),'initial':p0,'success':bool(sol.success),'nfev':sol.nfev,'cost':sol.cost,'observations':j,'camera4k_fixed_platform':cam,'working_shape':'shared circular upper arc; lower continuation inferred and not used in fitting','regularization':'weak y6/10,z3/7,R6/8,D10/20,f1500/2500; not source truth','diagnostics':[]}
for name,q,obs in zip(['4k','front'],contours(sol.x),pts):
 dist=cKDTree(q).query(obs)[0];out['diagnostics'].append({'view':name,'source_to_projected_sample_distance_px':dist.tolist(),'rms':float(np.sqrt(np.mean(dist**2))),'not_acceptance':'partial soft silhouette only, correspondence and thickness edge uncertain, no visibility-aware full contour audit'})
(r/'qa/shared-inner-arch-conditional-fit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['observations']},indent=2))
