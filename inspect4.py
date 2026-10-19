import bpy,json
from bpy_extras.object_utils import world_to_camera_view
names=['Table_small_cup','Planter.003','Plant_leaf.036','Side_table_round_top','White_sphere_under_table']
out={}
for n in names:
 o=bpy.data.objects[n];vs=[o.matrix_world@v.co for v in o.data.vertices];mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)];out[n]={'bounds':[mn,mx],'matrix':[list(r) for r in o.matrix_world]}
print(json.dumps(out,indent=2));open('/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2/actual_bounds.json','w').write(json.dumps(out,indent=2))
