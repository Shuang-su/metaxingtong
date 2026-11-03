import bpy
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R06_{mode}.blend'))
 o=bpy.data.objects['WALL_rear_sill'];o.location.x+=1
 o['observation_status']='Inferred finite wall sill below observed opening; moved +1 x to align with R03 opening. Thickness and height not measured.'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R07_{mode}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(D/f'models/R07_{mode}.glb'),export_format='GLB',export_apply=True)
