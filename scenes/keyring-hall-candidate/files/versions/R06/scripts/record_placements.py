import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(r/'models/keyring-material.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);vs=[ev.matrix_world@v.co for v in ev.data.vertices];rows.append({'id':o.name,'world_matrix':[list(row) for row in o.matrix_world],'world_bounds_min':[min(v[i] for v in vs) for i in range(3)],'world_bounds_max':[max(v[i] for v in vs) for i in range(3)],'geometry_units':'unscaled model units; not metric evidence','source_instance_correspondence':'class/group conditional; individual source repeated-key identity/count not established','evidence':o.get('evidence')})
(r/'docs/object-placements.json').write_text(json.dumps(rows,indent=2))
