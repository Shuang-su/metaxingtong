"""Frozen J1, H camera audit only. Fixes upper-edge-versus-full-hull ambiguity."""
from screen_joint_candidate import *
Q=json.load(open(R/'joint_candidate_screening.json'))['selected'];g=Q['geometry'];q=np.array(Q['parameters']);old=json.load(open(R/'heldout_camera_validation.json'))['views']['H'];b=normcam(J['cameras']['MATCH_H'])
obs={'m0':[[82,150],[32,1050]],'m1':[[990,20],[992,790]],'sofaL':[[882,804],[963,798],[1080,795],[1196,793]],'sofaR':[[1228,798],[1332,791],[1440,787],[1481,788]]}
def cam(v):return np.r_[v[:3],[bm[0]+g['bed_dx']+(bx[0]-bm[0])*v[3],bc[1]+g['bed_dy']+(v[4]-.5)*(bx[1]-bm[1])*g['bed_width_scale'],bx[2]+v[5]],v[6]]
def upper(c,n,uv):
 p=project(c,V[n]);poly=p[ConvexHull(p).vertices];res=[]
 for x,y in uv:
  vals=[]
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>1e-8: vals.append(a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
  if vals:res.append(min(vals)-y)
  else:
   # Penalize missing horizontal support as well as y rather than silently selecting another silhouette.
   nearest=p[np.argmin(abs(p[:,0]-x))];res.append(np.sign(nearest[1]-y or 1)*(abs(nearest[1]-y)+abs(nearest[0]-x)))
 return np.array(res)
def fun(v):
 c=cam(v);return np.r_[line(c,xline(-1.603616,g['window_y']+.0027),obs['m0'])/8,line(c,xline(0,g['window_y']+.0027),obs['m1'])/8,upper(c,SOFAL,obs['sofaL'])/12,upper(c,SOFAR,obs['sofaR'])/12]
lo=np.r_[b[:3]-.45,.03,.08,.15,np.log(25)];hi=np.r_[b[:3]+.45,.4,.92,.65,np.log(48)];runs=[]
for f in [30,40]:
 st=np.array(old['parameters']);st[-1]=np.log(f);sol=least_squares(fun,np.clip(st,lo+1e-7,hi-1e-7),bounds=(lo,hi),max_nfev=400,loss='soft_l1',ftol=1e-9,xtol=1e-9,gtol=1e-9);c=cam(sol.x)
 runs.append({'cost':float(sol.cost),'camera':c.tolist(),'parameters':sol.x.tolist(),'upper_left_y_residual_px':upper(c,SOFAL,obs['sofaL']).tolist(),'upper_right_y_residual_px':upper(c,SOFAR,obs['sofaR']).tolist(),'calibration_residual_sigma':fun(sol.x).tolist(),'m2_target_residual_px':line(c,xline(1.5,g['window_y']+.0027),[[1542,500],[1551,700]]).tolist(),'grey_right_target_residual_px':line(c,xline(1.521875+g['pillar_width']+.59,g['window_y']-g['pillar_projection']-.02),[[1801,300],[1814,500],[1827,700],[1840,900]]).tolist(),'bounds':[i for i,x in enumerate(sol.x) if min(abs(x-lo[i]),abs(x-hi[i]))<1e-3]})
c=np.array(old['camera']);out={'status':'AUDIT_ONLY_NO_NEW_GEOMETRY_OR_RERENDERS','geometry_frozen':True,'original_H_calibration_status':'INVALID_UPPER_EDGE_ASSOCIATION','original_H_holdout_metrics_status':'WITHDRAWN_AS_RELIABLE_GEOMETRY_TEST','reason':'Source sofa upper-edge observations were matched to the whole convex hull, allowing matches to lower edges. Actual render exposes ~200px wrong top position.','old_true_upper_left_residual_px':upper(c,SOFAL,obs['sofaL']).tolist(),'old_true_upper_right_residual_px':upper(c,SOFAR,obs['sofaR']).tolist(),'corrected_upper_envelope_only_runs':runs,'selected':min(runs,key=lambda x:x['cost']),'limitations':['No externally calibrated H camera exists.','New nuisance-camera parameters are mathematical audit results, not rendered/accepted views.','Existing H PNGs retain old invalid calibration and must be shown only as a failure diagnostic.','J1 separately fails actual blind/grey-fold physical occlusion.']}
(R/'H_camera_upper_edge_correction_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
