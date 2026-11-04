import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104/versions/R06/models/keyring-material.blend')
bpy.ops.wm.open_mainfile(filepath=str(R));dg=bpy.context.evaluated_depsgraph_get();D={};bad=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];b=BVHTree.FromPolygons(v,f,all_triangles=True);lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)];D[o.name]=(v,f,b,lo,hi)
 bm=bmesh.new();bm.from_mesh(m)
 for edge in bm.edges:
  if not edge.is_manifold:bad.append({'object':o.name,'linked_faces':len(edge.link_faces),'endpoints':[list(o.matrix_world@x.co) for x in edge.verts]})
 bm.free();e.to_mesh_clear()
out={'nonmanifold_edges':bad,'targets':{}}
for n in [n for n in D if n.startswith(('white-key-', 'black-key-'))]+['piano-open-lid','piano-soundboard']:
 a=D[n];neighbors=[];separate=0
 for k,b in D.items():
  if k==n:continue
  gaps=[max(a[3][i]-b[4][i],b[3][i]-a[4][i],0) for i in range(3)]
  if max(gaps)>1e-4:separate+=1;continue
  pairs=a[2].overlap(b[2]);ds=[b[2].find_nearest(v)[3] for v in a[0]]+[a[2].find_nearest(v)[3] for v in b[0]]
  neighbors.append({'object':k,'aabb_gap':gaps,'surface_pairs':len(pairs),'vertex_surface_distance_upper_bound':min(ds),'containment_not_tested':not bool(pairs) and max(gaps)==0})
 out['targets'][n]={'neighbors_within_1e-4_AABB':neighbors,'other_objects_strictly_separated_by_AABB_gt_1e-4':separate}
(O/'key-relations.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['targets'],indent=2))
