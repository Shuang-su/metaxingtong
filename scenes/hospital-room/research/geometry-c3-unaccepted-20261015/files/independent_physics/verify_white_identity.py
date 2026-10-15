"""Read-only C2 material/white evaluated geometry and visibility identity audit."""
import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent/'models'
def snap(path):
 digest=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();meshes={};visibility={};cameras={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   eo=o.evaluated_get(dg);m=eo.to_mesh();m.calc_loop_triangles();dat={'vertices_world':[list(eo.matrix_world@v.co) for v in m.vertices],'triangles':[list(t.vertices) for t in m.loop_triangles]};meshes[o.name]=hashlib.sha256(json.dumps(dat,sort_keys=True).encode()).hexdigest();visibility[o.name]={'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'visible_camera':o.visible_camera,'visible_shadow':o.visible_shadow,'visible_diffuse':o.visible_diffuse,'visible_glossy':o.visible_glossy,'visible_transmission':o.visible_transmission};eo.to_mesh_clear()
  if o.type=='CAMERA':cameras[o.name]={'matrix_world':[list(x) for x in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end}
 return {'file':str(path),'sha256':digest,'geometry_hashes':meshes,'visibility':visibility,'cameras':cameras,'unchanged':digest==hashlib.sha256(path.read_bytes()).hexdigest()}
a=snap(ROOT/'hospital_C2_small_shared_geometry_UNACCEPTED.blend');b=snap(ROOT/'hospital_C2_small_shared_geometry_WHITE_UNACCEPTED.blend')
r={'material_file':a['file'],'white_file':b['file'],'material_sha256':a['sha256'],'white_sha256':b['sha256'],'evaluated_geometry_identical':a['geometry_hashes']==b['geometry_hashes'],'object_visibility_identical':a['visibility']==b['visibility'],'all_camera_parameters_identical':a['cameras']==b['cameras'],'mesh_count':len(a['geometry_hashes']),'geometry_hashes':a['geometry_hashes'],'camera_count':len(a['cameras']),'sources_unchanged':a['unchanged'] and b['unchanged'],'source_fidelity_accepted':False}
(OUT/'C2_material_white_identity.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print({k:v for k,v in r.items() if k!='geometry_hashes'})
