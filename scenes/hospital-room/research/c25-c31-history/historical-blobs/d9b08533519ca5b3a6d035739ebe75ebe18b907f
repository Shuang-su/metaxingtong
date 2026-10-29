from pathlib import Path
import numpy as np,json
from scipy.optimize import minimize_scalar
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parents[2];P=R/'c28';j=json.load(open(R/'c27/blinds_projection_source.json'));f=json.load(open(R/'c27/bank1_fit.json'));obs=json.load(open(P/'upper_line_observations.json'));names=f['target_group'];trim=f['selected_H_G_only']['right_trim_scene_units'];anchor=np.array(j['objects'][names[1]]['world_vertices']).mean(0)[2]
def uv(k,idx,scale):
 v=np.array(j['objects'][names[idx]]['world_vertices']);lo=v[:,0].min();hi=v[:,0].max();v[:,0]=lo+(v[:,0]-lo)*(hi+trim-lo)/(hi-lo);v[:,2]+=(v[:,2].mean()-anchor)*(scale-1)
 q=np.c_[v,np.ones(len(v))]@np.array(j['cameras'][k]['projection']).T;a=q[:,:2]/q[:,3:4];return np.c_[(a[:,0]+1)*960,(1-a[:,1])*540]
def bottom(k,idx,scale,xs):
 a=uv(k,idx,scale);a=a[ConvexHull(a).vertices];out=[]
 for x in xs:
  y=[u[1]+(v[1]-u[1])*(x-u[0])/(v[0]-u[0]) for u,v in zip(a,np.roll(a,-1,axis=0)) if min(u[0],v[0])<=x<=max(u[0],v[0]) and abs(v[0]-u[0])>1e-9];out.append(max(y))
 return np.array(out)
def residual(s):
 a=[]
 for k in ['H','G']:
  rows=obs[k]['lines'];xs=np.linspace(rows[0]['search_domain'][0]+5,rows[0]['search_domain'][1]-5,24);b=bottom(k,1,s,xs);y=np.polyval(rows[0]['fit_y_ax_b'],xs)
  for n in range(1,5):a.extend((bottom(k,n+1,s,xs)-b)-(np.polyval(rows[n]['fit_y_ax_b'],xs)-y))
 return np.array(a)
fit=minimize_scalar(lambda s:np.mean(residual(s)**2),bounds=(.65,1.05),method='bounded',options={'xatol':1e-10});scale=float(fit.x);out={'fit_views':['H','G'],'check_view':'N642 previously viewed; not used in spacing fit','objective':'Within-view relative vertical gaps to lowest remaining slat, five source ridges, 24 correlated x samples per line; no endpoint fit','scale':scale,'anchor_world_z':float(anchor),'relative_gap_RMSE_before_px':float(np.sqrt(np.mean(residual(1)**2))),'relative_gap_RMSE_after_px':float(np.sqrt(fit.fun)),'views':{}}
for k,entry in obs.items():
 rows=[]
 for n,r in enumerate(entry['lines']):
  xs=np.linspace(r['search_domain'][0]+5,r['search_domain'][1]-5,24);y=np.polyval(r['fit_y_ax_b'],xs);a=bottom(k,n+1,1,xs);b=bottom(k,n+1,scale,xs)
  rows.append({'slat':n+2,'before_MAE_px':float(np.abs(a-y).mean()),'after_MAE_px':float(np.abs(b-y).mean()),'before_signed_px':float((a-y).mean()),'after_signed_px':float((b-y).mean()),'observed_slope':r['fit_y_ax_b'][0],'before_slope':float(np.polyfit(xs,a,1)[0]),'after_slope':float(np.polyfit(xs,b,1)[0])})
 out['views'][k]=rows
(P/'spacing_fit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
