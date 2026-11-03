import bpy
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R09b_{mode}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(D/f'models/R09b_{mode}.glb'),export_format='GLB',export_apply=True,export_cameras=True)
