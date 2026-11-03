import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parents[1]
records=json.load(open(D/'qa/R05-camera-fit.json'))
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R04_{mode}.blend'))
 for a in records:
  o=bpy.data.objects[a['camera']];o.location=a['fitted'][:3];o.rotation_euler=Matrix(a['rotation_matrix']).to_euler()
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R05_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R05_{mode}.glb'),export_format='GLB',export_apply=True)
