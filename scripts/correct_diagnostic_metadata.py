import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'qa/R07_extra_diagnostic_manifest.json';a=json.loads(p.read_text());scene=bpy.context.scene;bpy.context.view_layer.update()
for v in a['views']:
 o=bpy.data.objects[v['name']];d=o.data;v.update(matrix_world=[list(row) for row in o.matrix_world],location=list(o.location),rotation_euler=list(o.rotation_euler),lens=d.lens,sensor_width=d.sensor_width,sensor_height=d.sensor_height,sensor_fit=d.sensor_fit,clip_start=d.clip_start,clip_end=d.clip_end,pixel_aspect=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y])
a['actual_all_fixed_diagnostic_lights']=[dict(name=o.name,type=o.data.type,shape=o.data.shape,energy=o.data.energy,color=list(o.data.color),size=o.data.size,size_y=o.data.size_y,location=list(o.location),matrix_world=[list(row) for row in o.matrix_world]) for o in bpy.data.objects if o.type=='LIGHT']
a['correction']={'prior_failure':'R07_extra_diagnostic_manifest_PREPARE_ONLY_MATRIX_FAILURE.json','reason':'prepare-only builder read stale unit matrices before dependency graph update; rendered images and saved diagnostic blend had actual camera transforms.','evidence_source':'Read from actual saved R07_diagnostic_views_ONLY.blend after view-layer update; no image or model edit.','diagnostic_blend_sha256':hashlib.sha256((R/'models/R07_diagnostic_views_ONLY.blend').read_bytes()).hexdigest()}
p.write_text(json.dumps(a,indent=2));print([(v['name'],v['matrix_world'][0],v['clip_start'],v['clip_end']) for v in a['views']])
