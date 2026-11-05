import runpy,bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent.parent
g=runpy.run_path(str(P/'scripts/precheck_single_left_fill.py'));s=g['s'];body=g['tree'];vv=g['vv'];tt=g['tt'];outline=g['outline'];front=g['front'];back=g['back'];pairs=g['out']['pairs']
def prism_status(p):
 if p.y<front-1e-6 or p.y>back+1e-6:return 'outside'
 x,z=p.x,p.z;inside=False
 for i,(ax,az) in enumerate(outline):
  bx,bz=outline[(i+1)%len(outline)];dx=bx-ax;dz=bz-az;u=max(0,min(1,((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz)))
  if (x-ax-u*dx)**2+(z-az-u*dz)**2<1e-12:return 'boundary'
  if (az>z)!=(bz>z) and x<(bx-ax)*(z-az)/(bz-az)+ax:inside=not inside
 if not inside:return 'outside'
 return 'boundary' if abs(p.y-front)<1e-6 or abs(p.y-back)<1e-6 else 'inside'
directions=[Vector(v).normalized() for v in [(1,.314159,.271828),(-.176,.91,.379),(.419,.237,.875)]]
def parity_status(tree,p):
 near=tree.find_nearest(p)
 if near[0] is not None and near[3]<1e-6:return 'boundary'
 parity=[]
 for d in directions:
  origin=p.copy();count=0
  for k in range(100):
   loc,no,ix,dist=tree.ray_cast(origin,d,100)
   if loc is None:break
   count+=1;origin=loc+d*1e-5
  else:return 'ambiguous'
  parity.append(count%2)
 return 'inside' if parity==[1,1,1] else ('outside' if parity==[0,0,0] else 'ambiguous')
def counter(vals):
 r={k:0 for k in ['inside','outside','boundary','ambiguous']}
 for v in vals:r[v]+=1
 return r
body_samples=vv+[sum((vv[i] for i in t),Vector())/3 for t in tt];trees={};points={};tris={}
for pair in pairs:
 o=bpy.data.objects[pair['object']];v=[o.matrix_world@x.co for x in o.data.vertices];o.data.calc_loop_triangles();t=[tuple(x.vertices) for x in o.data.loop_triangles];trees[o.name]=BVHTree.FromPolygons(v,t,all_triangles=True);points[o.name]=v;tris[o.name]=t
rows=[]
for pair in pairs:
 name=pair['object'];v=points[name];t=tris[name];samples=v+[sum((v[i] for i in tri),Vector())/3 for tri in t]
 rows.append({'object':name,'intentional_cloud_contact':pair['expected_contact'],'surface_triangle_overlap_count':pair['triangle_overlap_count'],'existing_samples_in_proposed_prism':counter(prism_status(p) for p in samples),'existing_sample_count':len(samples),'proposed_body_samples_in_existing_mesh':counter(parity_status(trees[name],p) for p in body_samples),'body_sample_count':len(body_samples)})
oldcloud=[n for n in trees if n.startswith('CLOUD_0')];neighbors=[n for n in trees if not n.startswith('CLOUD_0')];baseline=[]
for c in oldcloud:
 for n in neighbors:
  overlap=trees[c].overlap(trees[n]);baseline.append({'original_cloud_tube':c,'neighbor':n,'existing_surface_triangle_overlap_count':len(overlap)})
result={'no_model_saved':True,'method':'body containment uses exact proposed constant-y prism and point-in-polygon; old meshes use 3-direction repeated BVH ray parity, eps1e-5, max100hits; classify sampled vertices plus triangle centroids, not certified full intersection volume or whole-mesh containment absence','body_point_count':len(body_samples),'body_to_existing_tests':rows,'unchanged_old_tube_neighbor_baseline':baseline,'decision':'REJECT CURRENT FILL: new solid surface intersects roof/ribs/gable; expected cloud contact cannot negate it. No new model, render, relocation or avoidance holes.','source_semantics':'original procedural contour is not source shape; filling category is not accurate reconstruction'}
(P/'results/left-fill-containment-and-baseline.json').write_text(json.dumps(result,indent=2));print('containment checks completed',len(rows))
