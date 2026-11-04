import bpy,json,pathlib,hashlib
from mathutils import Matrix
P=pathlib.Path(__file__).resolve().parents[1];D=json.load(open(P/'qa/R08-exterior-trials/trials.json'));t=next(x for x in D['trials'] if x['lens']==18);audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R07_{mode}.blend'));c=bpy.data.objects['SOURCE_15_exterior'];old=[list(row) for row in c.matrix_world];m=Matrix.Identity(4)
 for i in range(3):
  for j in range(3):m[i][j]=t['camera_rotation'][i][j]
  m[i][3]=t['camera_position'][i]
 c.matrix_world=m;c.data.lens=18;c['R08_scope']='Conditional wall-column silhouette and finite spire-top camera trial. Same 18mm focal length; no geometry changes. Exterior details, roof shape, doors and platform remain FAILED. Manual source screenshot, not native calibration.'
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R08_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R08_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True)
 audit[mode]={'camera_before':old,'camera_after':[list(row) for row in c.matrix_world],'lens':c.data.lens,'model_sha256':hashlib.sha256((P/'models'/f'R08_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R08-applied.json').write_text(json.dumps(audit,indent=2))
