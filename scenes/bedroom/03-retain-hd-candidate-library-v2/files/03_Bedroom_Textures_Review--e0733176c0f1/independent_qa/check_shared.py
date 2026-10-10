import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/bedroom_hd_revision_20261010');out={}
for fn in ['01_HD_candidate_material.blend','02_HD_candidate_white.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models/hd_v2'/fn));bpy.context.view_layer.update();h=hashlib.sha256()
 for o in sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda x:x.name):
  h.update(repr((o.name,[list(o.matrix_world@v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])).encode())
 out[fn]={'world_geometry_sha256':h.hexdigest(),'exposure':bpy.context.scene.view_settings.exposure,'camera_clip':{o.name:o.data.clip_start for o in bpy.context.scene.objects if o.type=='CAMERA'}}
out['equal']=out['01_HD_candidate_material.blend']['world_geometry_sha256']==out['02_HD_candidate_white.blend']['world_geometry_sha256'];(R/'independent_qa/shared_geometry.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
