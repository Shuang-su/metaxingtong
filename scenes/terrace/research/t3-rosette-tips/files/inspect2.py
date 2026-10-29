import bpy,json
from mathutils import Vector
bpy.context.view_layer.update()
o=bpy.data.objects['Table_small_cup']; print('CUP',list(o.matrix_world.translation),list(o.location),o.parent)
c=o.matrix_world.translation
out=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)];ctr=Vector([(mn[i]+mx[i])/2 for i in range(3)])
  if (ctr-c).length<.8:out.append(dict(name=o.name,bounds=[mn,mx],materials=[m.name for m in o.data.materials],vertices=len(o.data.vertices),collections=[x.name for x in o.users_collection]))
open('/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2/decor_objects.json','w').write(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
