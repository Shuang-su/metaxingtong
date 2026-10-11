import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010')
s=bpy.context.scene
r={'cameras':[], 'objects':[], 'render':{'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'world':s.world.name}}
for o in bpy.data.objects:
 if o.type=='CAMERA':r['cameras'].append({'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens,'sensor_width':o.data.sensor_width,'shift':[o.data.shift_x,o.data.shift_y]})
 if o.type=='MESH':
  a=[o.matrix_world@Vector(v) for v in o.bound_box]
  r['objects'].append({'name':o.name,'min':[min(v[i] for v in a) for i in range(3)],'max':[max(v[i] for v in a) for i in range(3)],'hide':o.hide_render})
(p/'qa/scene_inspection.json').write_text(json.dumps(r,indent=2))
