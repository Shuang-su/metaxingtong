import bpy,pathlib,json
from mathutils.bvhtree import BVHTree
R=pathlib.Path('forest-diagnostic-replay-20261104').resolve();bpy.ops.wm.open_mainfile(filepath=str(R/'models/R09_material.blend'));out=[]
for i in range(11):
 names=['FLOWER_%02d_stem'%i,'FLOWER_%02d_centre'%i]+['FLOWER_%02d_petal_%d'%(i,j) for j in range(5)]
 objects={n:bpy.data.objects[n] for n in names};trees={n:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons],all_triangles=False) for n,o in objects.items()};edges=[];near=[]
 for a in range(len(names)):
  for b in range(a+1,len(names)):
   na,nb=names[a],names[b];overlap=trees[na].overlap(trees[nb]);dist=min(trees[nb].find_nearest(objects[na].matrix_world@v.co)[3] for v in objects[na].data.vertices)
   if overlap:edges.append([na,nb,len(overlap)])
   near.append([na,nb,dist])
 seen={names[0]}
 for _ in names:
  for a,b,_ in edges:
   if a in seen or b in seen:seen.update([a,b])
 out.append(dict(flower=i,surface_intersection_edges=edges,unconnected_to_stem_by_surface_intersection=[n for n in names if n not in seen],one_direction_vertex_to_surface_min=near))
(R/'qa/flower-connection-check.json').write_text(json.dumps({'method':'actual triangle BVH surface overlap and one-way vertex-to-surface nearest distances; disjoint surfaces can still fully contain another object; graph is evidence not general union proof','flowers':out},indent=2));print([(x['flower'],x['unconnected_to_stem_by_surface_intersection']) for x in out])
