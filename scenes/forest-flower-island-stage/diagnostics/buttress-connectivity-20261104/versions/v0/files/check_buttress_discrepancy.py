import bpy,json,sys,math,hashlib,itertools
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path('/workspace/scratch/fa58bfcf0425');sys.path.insert(0,str(R/'forest-buttress-connectivity-study-20261104'));from triangle_distance import point_triangle2,triangle_triangle2
p=R/'forest-diagnostic-replay-20261104/models/R15_log-contact-diagnostic_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p));tr=bpy.data.objects['TREE_main_trunk'];ob=bpy.data.objects['TREE_main_buttress_02'];tr.data.calc_loop_triangles();ob.data.calc_loop_triangles();v=[tr.matrix_world@x.co for x in tr.data.vertices];vv=[ob.matrix_world@x.co for x in ob.data.vertices];ids=[tuple(t.vertices)for t in tr.data.loop_triangles];polys=[tuple(f.vertices)for f in tr.data.polygons];poly=BVHTree.FromPolygons(v,polys);loop=BVHTree.FromPolygons(v,ids,all_triangles=True)
records={}
for label,tree in [('polygon',poly),('loop_triangles',loop)]:
 rows=[]
 for i,x in enumerate(vv):
  q,n,j,d=tree.find_nearest(x);rows.append({'vertex':i,'distance':d,'nearest':list(q),'target_index':j,'normal':list(n)})
 records[label]=min(rows,key=lambda x:x['distance'])
win=records['polygon'];q=vv[win['vertex']];pid=win['target_index'];face=polys[pid];comb=[]
for ti in itertools.combinations(face,3):comb.append({'indices':ti,'point_triangle_distance':math.sqrt(point_triangle2(tuple(q),*(tuple(v[i])for i in ti))),'nearestpoint_distance':math.sqrt(point_triangle2(win['nearest'],*(tuple(v[i])for i in ti)))})
actual=[{'triangle':i,'indices':ids[i],'vertex_distance':math.sqrt(point_triangle2(tuple(q),*(tuple(v[k])for k in ids[i])))}for i,t in enumerate(tr.data.loop_triangles)if t.polygon_index==pid]
exact=min((math.sqrt(point_triangle2(tuple(q),*(tuple(v[k])for k in ti))),i)for i,ti in enumerate(ids));pairs=[]
# Confirm full feature method at all buttress faces incident on winning vertex versus every trunk triangle.
for at in ob.data.loop_triangles:
 if win['vertex']not in at.vertices:continue
 a=[tuple(vv[k])for k in at.vertices]
 for bi,bt in enumerate(ids):pairs.append((math.sqrt(triangle_triangle2(a,[tuple(v[k])for k in bt])),at.index,bi))
j={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nearest_vertex_bounds':records,'polygon_face_indices':face,'polygon_all_triangle_combinations':comb,'actual_loop_triangles_of_polygon':actual,'winning_vertex_exact_all_loop_triangles_min':exact,'incident_faces_full_feature_min':min(pairs),'scope':'Buttress02 discrepancy only, no model changes'}
(R/'independent-forest-replay-qa-20261104/buttress-discrepancy-check.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
