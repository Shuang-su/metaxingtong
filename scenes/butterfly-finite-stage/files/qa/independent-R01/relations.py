import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R01_material.blend'));obs={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'};trees={};bounds={};bad={}
for n,o in obs.items():
 d=o.data;d.calc_loop_triangles();v=[o.matrix_world@x.co for x in d.vertices];t=[tuple(x.vertices)for x in d.loop_triangles];trees[n]=BVHTree.FromPolygons(v,t,all_triangles=True);bounds[n]=[(min(x[i]for x in v),max(x[i]for x in v))for i in range(3)]
 bm=bmesh.new();bm.from_mesh(d);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();e=[{'verts':[x.index for x in e.verts],'coordinates':[list(x.co)for x in e.verts],'linked_faces':len(e.link_faces)}for e in bm.edges if not e.is_manifold]
 if e:bad[n]=e
 bm.free()
def near(a,b):return all(a[i][0]<=b[i][1]and b[i][0]<=a[i][1]for i in range(3))
result={}
for n in obs:
 if not n.startswith(('VEIN_','WING_')):continue
 cand=[k for k in obs if k!=n and near(bounds[n],bounds[k])];pairs={k:len(trees[n].overlap(trees[k]))for k in cand};result[n]={'aabb_candidates':cand,'surface_overlap_pairs':{k:v for k,v in pairs.items()if v}}
(O/'relations.json').write_text(json.dumps({'nonmanifold':bad,'relations':result,'bounds':bounds},indent=2));print('DONE')
