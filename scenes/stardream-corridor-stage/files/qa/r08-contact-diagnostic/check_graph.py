import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-ceiling-qa-20261105');f=P/'models/R08_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
for o in obs:
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];fi=[tuple(t.vertices) for t in o.data.loop_triangles];ts=[[tuple(v[i]) for i in t] for t in fi];cache[o.name]=(ts,BVHTree.FromPolygons(v,fi,all_triangles=True))
def dist(a,b):
 ts,t=cache[a];us,u=cache[b];pairs=t.overlap(u)
 best=math.inf
 for x in ts:
  xl=[min(p[i] for p in x) for i in range(3)];xh=[max(p[i] for p in x) for i in range(3)]
  for y in us:
   lo=sum(max(0,min(p[i] for p in y)-xh[i],xl[i]-max(p[i] for p in y))**2 for i in range(3))
   if lo>best:continue
   best=min(best,triangle_triangle2(x,y))
   if best==0:return {'distance':0.,'bvh_face_pairs':len(pairs)}
 return {'distance':math.sqrt(best),'bvh_face_pairs':len(pairs)}
bounds={n:[[min(p[i] for t in ts for p in t),max(p[i] for t in ts for p in t)] for i in range(3)] for n,(ts,bvh) in cache.items()}
names=sorted(cache);edges=[];rejected=[];adj={n:set() for n in names};tol=1e-6
for i,a in enumerate(names):
 for b in names[i+1:]:
  x,y=bounds[a],bounds[b];lower=math.sqrt(sum(max(0,x[k][0]-y[k][1],y[k][0]-x[k][1])**2 for k in range(3)))
  if lower>tol:continue
  r=dist(a,b)
  if r['distance']<=tol:
   adj[a].add(b);adj[b].add(a);edges.append({'a':a,'b':b,**r})
  else:rejected.append({'a':a,'b':b,**r})
left=set(names);comps=[]
while left:
 todo=[left.pop()];group=set(todo)
 while todo:
  for n in adj[todo.pop()]:
   if n in left:left.remove(n);group.add(n);todo.append(n)
 comps.append(sorted(group))
R={'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'tolerance':tol,'mesh_count':len(names),'edges':edges,'aabb_candidates_not_surface_contact':rejected,'components':sorted(comps,key=len,reverse=True),'scope':'surface-distance graph only; not Boolean, mechanical load, full containment or collision acceptance'}
(Q/'R08-contact-graph.json').write_text(json.dumps(R,indent=2));print('DONE',len(edges),[len(c) for c in comps])
