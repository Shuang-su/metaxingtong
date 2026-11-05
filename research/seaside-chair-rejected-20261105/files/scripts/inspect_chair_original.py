import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/seaside-chair-candidate-20261105/models/material.blend')
a=[]
for o in bpy.data.objects:
 if o.name.startswith('C01'):
  a.append({'name':o.name,'vertices':len(o.data.vertices),'matrix':[list(r) for r in o.matrix_world],'world_vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'materials':[m.name for m in o.data.materials]})
json.dump(a,open('/workspace/scratch/fa58bfcf0425/seaside-chair-candidate-20261105/qa/chair-original-inspection.json','w'),indent=2)
print([(x['name'],x['vertices']) for x in a])
