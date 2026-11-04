import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];dg=bpy.context.evaluated_depsgraph_get();geo=[];cam=[];extra=[]
for ob in sorted(bpy.data.objects,key=lambda o:o.name):
 if ob.type in {'MESH','CURVE'}:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();geo.append((ob.name,[tuple(ev.matrix_world@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]));ev.to_mesh_clear()
 if ob.type=='CAMERA':
  c=(ob.name,[list(v) for v in ob.matrix_world],ob.data.type,ob.data.lens,ob.data.ortho_scale)
  (extra if ob.name.startswith('DIAG') else cam).append(c)
fp=dict(geometry_sha256=hashlib.sha256(json.dumps(geo,separators=(',',':')).encode()).hexdigest(),cameras_sha256=hashlib.sha256(json.dumps(cam,separators=(',',':')).encode()).hexdigest(),geometric_objects=len(geo),cameras=len(cam))
base=json.loads((R/'qa/R07_material_white_identity.json').read_text())['white'];res=dict(diagnostic_blend_sha256=hashlib.sha256((R/'models/R07_diagnostic_views_ONLY.blend').read_bytes()).hexdigest(),base_white=base,diagnostic_original_subset=fp,geometry_and_original_cameras_identical=base==fp,additional_camera_count=len(extra),additional_cameras=extra,visibility_overrides=[o.name for o in bpy.data.objects if o.hide_render])
(R/'qa/R07_diagnostic_identity.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
