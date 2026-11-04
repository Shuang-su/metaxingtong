import sys
sys.path.pop(0)
import pathlib,json,numpy as np
from scipy.spatial import ConvexHull
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-exterior-fit-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-source15-qa-20261104');ns={'__file__':str(P/'fit.py')};exec((P/'fit.py').read_text().split('M=np.array')[0],ns);G=ns['G'];V=ns['V'];tr=json.loads((P/'trials.json').read_text());out=[]
for t in tr['trials']:
 p=t['parameters'];lens=t['lens'];uv,depth=ns['project'](V,p,lens);h=ConvexHull(uv).vertices;edges=[]
 for i,j in zip(h,np.roll(h,-1)):
  if np.linalg.norm(V[i,:2]-V[j,:2])<1e-6:edges.append((i,j))
 edges.sort(key=lambda ij:float((uv[ij[0],0]+uv[ij[1],0])/2));sel=[edges[0],edges[-1]];prov=[]
 for i,j in sel:
  a,b=V[i],V[j];candidates=[]
  for name,o in G['objects'].items():
   if not name.startswith(('WALL_','COLUMN_')):continue
   v=np.array(o['vertices']);ids=np.where(np.linalg.norm(v[:,:2]-a[:2],axis=1)<2e-7)[0]
   if len(ids):candidates.append({'object':name,'matching_vertex_ids':ids.tolist(),'zrange':[float(v[ids,2].min()),float(v[ids,2].max())],'spans_full_edge':bool(v[ids,2].min()<=min(a[2],b[2])+2e-7 and v[ids,2].max()>=max(a[2],b[2])-2e-7)})
  prov.append({'world_endpoints':[a.tolist(),b.tolist()],'objects':candidates})
 calc=ns['residual'](p,lens,True);cost=.5*sum(ns['residual'](p,lens)**2);C,R=ns['matrix'](p)
 out.append({'lens':lens,'projection_rotation_det':float(np.linalg.det(R)),'orthonormal_error':float(np.max(abs(R.T@R-np.eye(3)))),'recomputed_cost':cost,'saved_cost_delta':cost-t['cost'],'saved_wall_errors_max_delta':float(np.max(abs(np.array(calc['wall_errors_px'])-t['wall_errors_px']))),'edges':prov,'minimum_depth':float(depth.min())})
(Q/'camera-fit-math-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
