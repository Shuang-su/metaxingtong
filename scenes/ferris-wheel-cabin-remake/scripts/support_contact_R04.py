"""New shared support-top contact correction, not a source-measured support design."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];records=[]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/ferris_remake_R03_{mode}.blend'));rows=[]
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.name.startswith('bench_') and '_support_' in o.name:
   before=[list(v.co) for v in o.data.vertices]
   for v in o.data.vertices:v.co.z=.05+(v.co.z-.05)*(.27/.23)
   rows.append({'object':o.name,'vertices_before':before,'vertices_after':[list(v.co) for v in o.data.vertices],'old_floor_gap':0,'old_apron_gap':.04,'new_floor_gap_target':0,'new_apron_gap_target':0,'source_status':'inferred support design; contact engineering correction not source acceptance'})
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.13,depth=.03,location=(0,0,2.585));mount=bpy.context.object;mount.name='ceiling_lamp_mount';mount.data.materials.append(bpy.data.materials['persisted neutral white'] if mode=='white' else bpy.data.materials['deep red enamel']);mount['qa_group']='lamp';mount['source_status']='visible lamp housing, exact mounting dimensions inferred; joins diffuser to ceiling';rows.append({'object':mount.name,'new_geometry':'cylinder radius.13 height.03 z2.57..2.60','old_diffuser_ceiling_gap':.0125,'new_mount_diffuser_overlap':.0075,'new_mount_ceiling_overlap':.01})
 bpy.context.scene['revision']='R04 four support tops extended to existing apron undersides; no source-camera change';bpy.ops.wm.save_as_mainfile(filepath=str(R/f'models/ferris_remake_R04_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(R/f'models/ferris_remake_R04_{mode}.glb'),export_format='GLB',export_apply=True);records.append({'mode':mode,'changes':rows})
(R/'qa/support-contact-correction-R04.json').write_text(json.dumps(records,indent=2));print('R04_SUPPORT_DONE')
