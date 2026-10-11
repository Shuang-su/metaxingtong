import bpy,json,bmesh,math
from mathutils import Vector
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/xingtong_train')
bpy.ops.wm.open_mainfile(filepath=str(R/'original/01_train_material.blend'))
s=bpy.context.scene; d={'objects':[],'collections':{},'scene':{k:str(v) for k,v in s.items()},'cameras':[]}
for c in bpy.data.collections:d['collections'][c.name]={'objects':len(c.objects),'hide_render':c.hide_render,'hide_viewport':c.hide_viewport}
for o in bpy.data.objects:
 if o.type=='CAMERA':d['cameras'].append({'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens})
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
 if boundary or o.name.startswith(('End door','Sloped wood','Table brass','Seat lower','Continuous floor','Central warm')):
  bounds=[o.matrix_world@Vector(v) for v in o.bound_box]
  d['objects'].append({'name':o.name,'dim':list(o.dimensions),'loc':list(o.location),'bounds':[[min(p[i] for p in bounds) for i in range(3)],[max(p[i] for p in bounds) for i in range(3)]],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'mods':[(m.name,m.type) for m in o.modifiers],'hide_render':o.hide_render})
(R/'analysis/original_audit.json').write_text(json.dumps(d,indent=2))
print(json.dumps({'scene':d['scene'],'cameras':d['cameras'],'collections':d['collections'],'relevant_objects':d['objects'][:22]},indent=2))
