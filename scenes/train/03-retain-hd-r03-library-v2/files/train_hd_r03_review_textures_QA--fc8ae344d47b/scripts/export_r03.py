import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];f=json.loads((R/'frozen_r03/freeze_manifest.json').read_text());rows=[]
for item in f['blends']:
 p=Path(item['file']);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==item['sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 out=R/'deliverables'/('03_train_material.glb' if item['kind']=='material' else '04_train_white.glb')
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h;rows.append({'input_blend':p.name,'input_sha256':h,'output':out.name,'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'limit_18MB_pass':out.stat().st_size<18_000_000})
(R/'deliverables/frozen_export_manifest.json').write_text(json.dumps(rows,indent=2))
