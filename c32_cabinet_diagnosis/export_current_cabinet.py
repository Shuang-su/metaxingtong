import bpy, json, hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path('/workspace/scratch/fa58bfcf0425/C27_geometry_candidate')
OUT=ROOT/'c32_cabinet_diagnosis'
SOURCE=ROOT/'c29/hospital_C29_curtain_MATERIAL_CONDITIONAL.blend'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene
names=['Cabinet • bedside lower carcass','Cabinet • white counter']
D={'source':str(SOURCE.relative_to(ROOT)),'source_sha256_before':before,'blender_version':bpy.app.version_string,'render_performed':False,'saved_blend':False,'scene_units':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length},'objects':{},'cameras':{},'related_object_names':[o.name for o in bpy.data.objects if any(t in o.name.lower() for t in ['cabinet','drawer','handle','shelf','counter'])]}
for name in names:
 o=bpy.data.objects[name]
 world=[o.matrix_world @ v.co for v in o.data.vertices]
 rec={'type':o.type,'matrix_world':[list(r) for r in o.matrix_world],'vertices_local':[list(v.co) for v in o.data.vertices],'vertices_world':[list(v) for v in world],'edges':[list(e.vertices) for e in o.data.edges],'polygons':[list(p.vertices) for p in o.data.polygons],'dimensions':list(o.dimensions),'bounds_world':{'min':[min(v[i] for v in world) for i in range(3)],'max':[max(v[i] for v in world) for i in range(3)]},'materials':[m.name if m else None for m in o.data.materials],'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'projections':{}}
 for cn in ['C10_H_shared_sofa_height_CONDITIONAL','C10_G_shared_sofa_height_CONDITIONAL','C10_665_shared_sofa_height_CONDITIONAL','C14_N642_fixed_windows_CONDITIONAL']:
  c=bpy.data.objects[cn]
  pp=[world_to_camera_view(s,c,v) for v in world]
  pix=[[float(p.x*1920),float((1-p.y)*1080),float(p.z)] for p in pp]
  rec['projections'][cn]={'vertices_xy_depth':pix,'bbox_unclipped':[min(p[0] for p in pix),min(p[1] for p in pix),max(p[0] for p in pix),max(p[1] for p in pix)],'all_in_front_of_camera':all(p[2]>0 for p in pix)}
  if cn not in D['cameras']:
   D['cameras'][cn]={'matrix_world':[list(r) for r in c.matrix_world],'lens':c.data.lens,'sensor_width':c.data.sensor_width,'sensor_height':c.data.sensor_height,'sensor_fit':c.data.sensor_fit,'shift_x':c.data.shift_x,'shift_y':c.data.shift_y}
 D['objects'][name]=rec
D['source_sha256_after']=sha(SOURCE)
assert D['source_sha256_before']==D['source_sha256_after']
(OUT/'current_cabinet_mesh_readonly.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
print(json.dumps({'sha256_unchanged':True,'objects':{n:{'vertices':len(v['vertices_local']),'polygons':len(v['polygons']),'dimensions':v['dimensions'],'bounds_world':v['bounds_world'],'modifiers':v['modifiers'],'projection_bboxes':{k:p['bbox_unclipped'] for k,p in v['projections'].items()}} for n,v in D['objects'].items()},'related_object_names':D['related_object_names']},ensure_ascii=False,indent=2))
