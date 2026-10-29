import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=Path('/workspace/scratch/fa58bfcf0425/C27_geometry_candidate');p=r/'c28/hospital_C28_bank1_MATERIAL_CONDITIONAL.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;out={}
for o in bpy.data.objects:
 if 'Curtain' in o.name or 'rail end' in o.name:
  if o.type!='MESH':continue
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  
  if 'drape' in o.name:
   mesh={'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'verts_local':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]}
   (r/'c29_diagnosis/c28_curtain_mesh_readonly.json').write_text(json.dumps(mesh))
  out[o.name]={'world_bbox':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'vertex_count':len(pts)}
  out[o.name]['projected_bbox']={}
  for k,c in [('H','C10_H_shared_sofa_height_CONDITIONAL'),('G','C10_G_shared_sofa_height_CONDITIONAL'),('N642','C14_N642_fixed_windows_CONDITIONAL')]:
   pp=[world_to_camera_view(s,bpy.data.objects[c],v) for v in pts];out[o.name]['projected_bbox'][k]=[[min(v.x for v in pp)*1920,(1-max(v.y for v in pp))*1080],[max(v.x for v in pp)*1920,(1-min(v.y for v in pp))*1080]]
(r/'c29_diagnosis/c28_curtain_actual_geometry.json').write_text(json.dumps(out,indent=2))
print('DONE')
