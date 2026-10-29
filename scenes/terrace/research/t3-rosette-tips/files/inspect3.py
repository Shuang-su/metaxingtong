import bpy,json
from mathutils import Vector
out=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.name=='Table_small_cup' or (o.location-Vector((3.5,1,.9))).length<.6 or 'succ' in o.name.lower()):
  out.append(dict(name=o.name,location=list(o.location),bounds=[list(v) for v in o.bound_box],matrix=[list(row) for row in o.matrix_world],vertices=len(o.data.vertices),materials=[m.name for m in o.data.materials]))
open('/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2/decor_objects.json','w').write(json.dumps(out,indent=2));print(json.dumps(out))
