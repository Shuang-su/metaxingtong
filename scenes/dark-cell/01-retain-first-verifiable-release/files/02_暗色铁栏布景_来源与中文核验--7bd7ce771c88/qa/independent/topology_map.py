import json,numpy as np
from collections import Counter
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1/qa/independent';j=json.load(open(R+'/surface_examples.json'));r={}
for n,a in j['blend'].items():
 a=np.array(a);b=np.array(j['glb'][n]);vertices=np.unique(a.reshape(-1,3),axis=0)
 def ids(q):
  ds=((q.reshape(-1,1,3)-vertices[None,:,:])**2).sum(2);ix=ds.argmin(1);return Counter(tuple(sorted(t)) for t in ix.reshape(-1,3)),float(np.sqrt(ds[np.arange(len(ix)),ix]).max())
 ia,ea=ids(a);ib,eb=ids(b);r[n]={'triangle_vertex_id_sets_equal':ia==ib,'max_nearest_vertex_error_units':eb}
json.dump(r,open(R+'/mapped_triangle_topology.json','w'),ensure_ascii=False,indent=2)
print('objects',len(r),'mismatch',[n for n,v in r.items() if not v['triangle_vertex_id_sets_equal']],'max_vertex_error',max(v['max_nearest_vertex_error_units'] for v in r.values()))
d=json.load(open(R+'/double_surface_result.json'));print('double max',max(v['double_precision_symmetric_distance'] for v in d.values()))
