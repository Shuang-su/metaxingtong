import bpy,json
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/C27_geometry_candidate');bpy.ops.wm.open_mainfile(filepath=str(r/'c28/hospital_C28_bank1_MATERIAL_CONDITIONAL.blend'));out={}
for o in bpy.data.objects:
 if (o.type=='MESH' and ('Bed ' in o.name)) or (o.type=='CAMERA' and ('C10_' in o.name or 'C14_N642' in o.name)):
  d={'matrix_world':[list(a) for a in o.matrix_world],'hide_render':o.hide_render}
  if o.type=='MESH':d['verts_local']=[list(v.co) for v in o.data.vertices];d['faces']=[list(p.vertices) for p in o.data.polygons]
  else:d.update({'lens':o.data.lens,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end})
  out[o.name]=d
(r/'c30_diagnosis/c28_actual_bed_objects.json').write_text(json.dumps(out))
