import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene';bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_Textured.blend');bpy.context.view_layer.update()
def w(o):return [o.matrix_world@v.co for v in o.data.vertices]
def centers(o):
 vs=w(o);return np.array([list(sum(vs[i:i+5],Vector())/5) for i in range(0,60,5)])
def tree(o):return BVHTree.FromPolygons(w(o),[tuple(p.vertices) for p in o.data.polygons])
def linked(a,b):
 c=a.mean(0);u,s,v=np.linalg.svd(a-c);basis=v[:2];n=v[2];aa=(a-c)@basis.T;cross=[]
 for p,q in zip(b,np.roll(b,-1,axis=0)):
  d1=np.dot(p-c,n)-1e-6;d2=np.dot(q-c,n)-1e-6
  if d1*d2<0:
   r=p+(q-p)*d1/(d1-d2);pt=(r-c)@basis.T;ds=[]
   for x,y in zip(aa,np.roll(aa,-1,axis=0)):ds.append(np.cross(y-x,pt-x))
   cross.append(all(x>=-1e-7 for x in ds) or all(x<=1e-7 for x in ds))
 return len(cross)==2 and sum(cross)==1
rows=[]
for span in range(74):
 objs=[bpy.data.objects[f'Chain_span_{span:02d}_link_{j:02d}'] for j in range(16)];cc=[centers(o) for o in objs];tt=[tree(o) for o in objs]
 anchor_gaps=[]
 for ci,bi in [(0,span),(-1,span+1)]:
  bt=tree(bpy.data.objects[f'Coastal_block_{bi:02d}']);ds=[]
  for p in w(objs[ci]):
   loc,n,idx,dist=bt.find_nearest(p);ds.append(dist if (p-loc).dot(n)>0 else -dist)
  anchor_gaps.append(min(ds))
 rows.append({'anchor_min_signed_distance':anchor_gaps,'span':span,'unlinked_neighbor_pairs':[j for j in range(15) if not linked(cc[j],cc[j+1])],'surface_intersect_neighbor_pairs':[j for j in range(15) if tt[j].overlap(tt[j+1])],'anchor_surface_intersections':[len(tt[0].overlap(tree(bpy.data.objects[f'Coastal_block_{span:02d}']))),len(tt[-1].overlap(tree(bpy.data.objects[f'Coastal_block_{span+1:02d}'])))]})
json.dump(rows,open(R+'/independent_qa/chains.json','w'),indent=2);print('SUMMARY',sum(len(x['unlinked_neighbor_pairs']) for x in rows),sum(len(x['surface_intersect_neighbor_pairs']) for x in rows),sum(not a for x in rows for a in x['anchor_surface_intersections']))
