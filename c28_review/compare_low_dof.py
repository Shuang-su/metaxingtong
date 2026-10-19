import json,pathlib,numpy as np
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
R=pathlib.Path(__file__).resolve().parents[1];P=R/'c27';O=R/'c28_review';j=json.loads((P/'blinds_projection_source.json').read_text());f=json.loads((P/'bank1_fit.json').read_text());lc=json.loads((P/'bank1_line_check.json').read_text());names=f['target_group'];base=np.array(j['objects'][names[1]]['world_vertices']);lo=base[:,0].min();hi=base[:,0].max();base[:,0]=lo+(base[:,0]-lo)*(hi+f['selected_H_G_only']['right_trim_scene_units']-lo)/(hi-lo)
center=base.mean(0);_,_,vh=np.linalg.svd(base[:,1:]-center[1:]);u=vh[0];u*=np.sign(u[0]);n=np.array([-u[1],u[0]]);proj={k:np.array(j['cameras'][k]['projection']) for k in lc};obs={k:np.array(f['observation_xy'][k]) for k in lc};keys=['H','G','N642']
def projection(k,v):
 q=np.c_[v,np.ones(len(v))]@proj[k].T;uv=q[:,:2]/q[:,3:4];return np.c_[(uv[:,0]+1)*960,(1-uv[:,1])*540]
def transform(params,names):
 p=dict(zip(names,params));v=base.copy();scale=p.get('depth_scale',1.);a=np.deg2rad(p.get('tilt_deg',0));c=np.cos(a);s=np.sin(a);rot=np.array([[c,-s],[s,c]]);yz=v[:,1:]-center[1:];yz=(np.outer(yz@u,u)*scale+np.outer(yz@n,n))@rot.T;v[:,1:]=center[1:]+yz
 v[:,0]=lo+(v[:,0]-lo)*(v[:,0].max()+p.get('trim_dx',0)-lo)/(v[:,0].max()-lo)
 a=np.deg2rad(p.get('bank_yaw_deg',0));c=np.cos(a);s=np.sin(a);v[:,:2]=(v[:,:2]-[lo,center[1]])@np.array([[c,-s],[s,c]]).T+[lo,center[1]]
 v[:,1]+=p.get('bank_dy',0);v[:,2]+=p.get('bank_dz',0);return v

def stats(params,names):
 v=transform(params,names);cap=v[base[:,0]>base[:,0].max()-1e-6];out={}
 for k in keys:
  xy=projection(k,v);cc=projection(k,cap);tip=cc[np.argmax(cc[:,1])];hull=xy[ConvexHull(xy).vertices];xx=np.array(lc[k]['sample_x']);yy=[]
  for x in xx:
   ys=[a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]) for a,b in zip(hull,np.roll(hull,-1,axis=0)) if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(a[0]-b[0])>1e-9]
   yy.append(max(ys) if ys else 999)
  yy=np.array(yy);res=yy-lc[k]['observed_y'];sl=np.polyfit(xx,yy,1)[0];out[k]={'endpoint_xy':tip.tolist(),'endpoint_residual_xy':(tip-obs[k]).tolist(),'endpoint_distance_px':float(np.linalg.norm(tip-obs[k])),'line_mean_abs_vertical_px':float(np.mean(abs(res))),'line_signed_mean_px':float(np.mean(res)),'line_slope':float(sl),'slope_delta':float(sl-lc[k]['fit_y_ax_b'][0]),'line_residual_at_left_mid_right_px':res[[0,12,-1]].tolist()}
 return out

def residual(params,names,line_weight=1.):
 d=stats(params,names);out=[]
 for k in ['H','G']:
  out.extend(d[k]['endpoint_residual_xy']);out.extend(np.array(d[k]['line_residual_at_left_mid_right_px'])*line_weight/np.sqrt(3))
 return out
bounds={'tilt_deg':(-35,35),'depth_scale':(.2,1.5),'trim_dx':(-.06,.06),'bank_yaw_deg':(-5,5),'bank_dy':(-.08,.08),'bank_dz':(-.02,.02)}
models=[['trim_dx'],['tilt_deg','trim_dx'],['depth_scale','trim_dx'],['tilt_deg','depth_scale','trim_dx'],['bank_yaw_deg','trim_dx'],['bank_dy','trim_dx'],['bank_dz','trim_dx'],['tilt_deg','trim_dx','bank_dz']]
out={'fit_views':['H','G'],'check_view':'N642 previously viewed, not used in parameter fit','native_slat_principal_depth_yz':u.tolist(),'native_slat_tilt_degrees':float(np.rad2deg(np.arctan2(u[1],u[0]))),'objective':'Per fit view: endpoint dx,dy plus bottom-line residuals at left/mid/right weighted 1/sqrt(3); equal aggregate endpoint-coordinate and line weights; line residual is silhouette minus fitted dark image ridge, not semantic contour truth.','baseline':stats([],[]),'models':{}}
for ns in models:
 best=None
 seeds=[-25,-12,0,12,25] if 'tilt_deg' in ns else [0]
 for tilt in seeds:
  x=[(tilt if n=='tilt_deg' else 1 if n=='depth_scale' else 0) for n in ns];res=least_squares(residual,x,args=(ns,),bounds=([bounds[n][0] for n in ns],[bounds[n][1] for n in ns]),diff_step=1e-5,max_nfev=1000)
  if best is None or np.sum(np.array(res.fun)**2)<np.sum(np.array(best.fun)**2):best=res
 out['models']['+'.join(ns)]={'parameters':dict(zip(ns,best.x.tolist())),'fit_objective_sse':float(np.sum(np.array(best.fun)**2)),'stats':stats(best.x,ns)}
(O/'low_dof_comparison.json').write_text(json.dumps(out,indent=2))
print('native tilt',out['native_slat_tilt_degrees']);print('baseline',json.dumps(out['baseline']))
for k,d in out['models'].items():print(k,d['parameters'],'SSE',round(d['fit_objective_sse'],3), 'stats',json.dumps({x:{q:round(z[q],4) for q in ['endpoint_distance_px','line_mean_abs_vertical_px','line_slope','slope_delta']} for x,z in d['stats'].items()}))
