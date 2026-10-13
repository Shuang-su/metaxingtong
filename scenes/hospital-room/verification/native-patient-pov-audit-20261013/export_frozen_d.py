import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path('/workspace/scratch/fa58bfcf0425/hospital_d_recovery_20261013b/spatial_fit_d/hospital_spatial_D.blend');R=Path('/workspace/scratch/fa58bfcf0425/hospital_native_comparison_20261013')
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;d=bpy.context.evaluated_depsgraph_get()
a={'source_blend':str(P),'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'objects':{},'cameras':{},'scene':{'world':s.world.name,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma}}
for o in bpy.data.objects:
 if o.type=='MESH':
  e=o.evaluated_get(d);m=e.to_mesh();verts=[list(e.matrix_world@v.co) for v in m.vertices]
  a['objects'][o.name]={'vertices':verts,'bbox':[list(o.matrix_world@Vector(v)) for v in o.bound_box],'hide_render':o.hide_render,'material_names':[x.name if x else None for x in o.data.materials],'matrix_world':list(map(list,o.matrix_world))};e.to_mesh_clear()
 if o.type=='CAMERA':a['cameras'][o.name]={'matrix_world':list(map(list,o.matrix_world)),'lens_mm':o.data.lens,'sensor_width_mm':o.data.sensor_width,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end}
(R/'frozen_d_world_geometry.json').write_text(json.dumps(a,ensure_ascii=False))
print('EXPORTED',len(a['objects']))
