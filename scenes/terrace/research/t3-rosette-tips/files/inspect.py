import bpy,json
from mathutils import Vector
s=bpy.context.scene
out=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  vs=[o.matrix_world@Vector(v) for v in o.bound_box]
  mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)]
  if mn[0]>3.1 and mx[0]<3.95 and mn[1]>.6 and mx[1]<1.5 and mn[2]>.7 and mx[2]<1.6:
   out.append(dict(name=o.name,bounds=[mn,mx],materials=[m.name for m in o.data.materials],vertices=len(o.data.vertices),collections=[c.name for c in o.users_collection]))
print(json.dumps(out,indent=2));print('SETTINGS',s.cycles.samples,s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.view_settings.view_transform)
open('/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2/decor_objects.json','w').write(json.dumps(out,indent=2))
