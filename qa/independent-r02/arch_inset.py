import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
Q=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(Q/'frozen/models/material.blend'));rows=[]
for i in range(3):
 a=bpy.data.objects[f'A{i:02d} vertical arch solid'];a.data.calc_loop_triangles();av=[a.matrix_world@v.co for v in a.data.vertices];t=[tuple(x.vertices)for x in a.data.loop_triangles];tree=BVHTree.FromPolygons(av,t,all_triangles=True)
 for j in range(2):
  b=bpy.data.objects[f'A{i:02d} inset {j}'];bv=[b.matrix_world@v.co for v in b.data.vertices];gap=min(v.y for v in av)-max(v.y for v in bv);ub=min(tree.find_nearest(v)[3]for v in bv);rows.append({'arch':a.name,'inset':b.name,'separating_y_plane_lower_bound':gap,'actual_vertex_to_triangle_upper_bound':ub,'equal_within':abs(ub-gap)})
(Q/'arch-inset.json').write_text(json.dumps(rows,indent=2));print(rows)
