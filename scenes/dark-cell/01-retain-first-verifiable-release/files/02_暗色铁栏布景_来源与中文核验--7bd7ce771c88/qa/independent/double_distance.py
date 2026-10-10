import json,numpy as np
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1/qa/independent';d=json.load(open(R+'/surface_examples.json'));res={}
def dist(p,t):
 a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;ap=p-a;n=np.cross(ab,ac);n2=(n*n).sum(1);dp=(ap*n).sum(1);q=p-dp[:,None]/n2[:,None]*n
 # Cross-product barycentric test avoids thin triangle Gram determinant cancellation.
 u=(np.cross(b-q,c-q)*n).sum(1)/n2;v=(np.cross(c-q,a-q)*n).sum(1)/n2;w=1-u-v
 inside=(u>=-1e-10)&(v>=-1e-10)&(w>=-1e-10);ds=np.where(inside,dp*dp/n2,np.inf)
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;f=np.clip(((p-x)*e).sum(1)/(e*e).sum(1),0,1);z=x+f[:,None]*e;ds=np.minimum(ds,((p-z)**2).sum(1))
 k=ds.argmin();return float(np.sqrt(ds[k])),int(k)
for name in d['blend']:
 a=np.array(d['blend'][name],dtype=np.float64);b=np.array(d['glb'][name],dtype=np.float64);worst=[]
 for x,y in [(a,b),(b,a)]:
  best=(0,None,None)
  pts=np.concatenate([x.reshape(-1,3),x.mean(1)])
  for p in pts:
   value,k=dist(p,y)
   if value>best[0]:best=(value,p.tolist(),y[k].tolist())
  worst.append(best)
 res[name]={'double_precision_symmetric_distance':max(w[0] for w in worst),'worst_directions':worst}
json.dump(res,open(R+'/double_surface_result.json','w'),ensure_ascii=False,indent=2);print(json.dumps(res,ensure_ascii=False,indent=2))
