from pathlib import Path
import numpy as np,json
from scipy.interpolate import CubicSpline
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parents[2];P=R/'c29';j=json.load(open(R/'c29_diagnosis/c28_curtain_mesh_readonly.json'));v=np.array(j['verts_local']);m=np.array(j['matrix_world']);cams=json.load(open(R/'c27/blinds_projection_source.json'))['cameras'];n=225;layers=65;profile=v[:n,0];old=profile[:29].copy();old[-1]=old[0];spline=CubicSpline(np.arange(29)/28,old,bc_type='periodic');variants={};out={}
for count in [5,6,7]:
 w=v.copy();cols=np.arange(n);t=np.clip((cols-28)/168,0,1);d=count-2;phase=d*t+(6-d)*(t-3*t*t+2*t*t*t);x=spline(phase%1);delta=x-profile;delta[(cols<=28)|(cols>=196)]=0
 for face in range(2):
  for z in range(layers):w[face*n*layers+z*n:face*n*layers+(z+1)*n,0]+=delta
 # Same paired front/back vector, fixed first/last full period, fixed Z and Y.
 assert np.allclose(w[n*layers:]-w[:n*layers],v[n*layers:]-v[:n*layers],atol=1e-12)
 A=np.c_[v,np.ones(len(v))]@m.T;B=np.c_[w,np.ones(len(w))]@m.T
 info={'target_nominal_cycles':count,'fixed_edge_columns':[0,28,196,224],'local_x_delta':delta.tolist(),'world_bounds_before':[A[:,:3].min(0).tolist(),A[:,:3].max(0).tolist()],'world_bounds_after':[B[:,:3].min(0).tolist(),B[:,:3].max(0).tolist()],'views':{}}
 for k in ['H','G','N642','665']:
  ab=[]
  for q in [A,B]:
   z=q@np.array(cams[k]['projection']).T;a=z[:,:2]/z[:,3:4];uv=np.c_[(a[:,0]+1)*960,(1-a[:,1])*540];ab.append(uv[ConvexHull(uv).vertices])
  rows=np.linspace(100,850,16);diff=[]
  for y in rows:
   bounds=[]
   for h in ab:
    xs=[a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]) for a,b in zip(h,np.roll(h,-1,axis=0)) if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(a[1]-b[1])>1e-8]
    bounds.append(None if not xs else [min(xs),max(xs)])
   if all(a is not None for a in bounds):diff.append({'y':float(y),'before':bounds[0],'after':bounds[1],'max_abs_edge_shift':float(np.max(np.abs(np.array(bounds[0])-bounds[1])))})
  info['views'][k]={'convex_outer_edge_samples':diff,'max_abs_edge_shift':max((a['max_abs_edge_shift'] for a in diff),default=None)}
 out[str(count)]=info
(P/'profile_candidates.json').write_text(json.dumps(out,indent=2));print({k:{v:q['max_abs_edge_shift'] for v,q in a['views'].items()} for k,a in out.items()})
