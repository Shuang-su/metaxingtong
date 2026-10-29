import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for f in ['car_passenger_cabin_white.blend','car_passenger_cabin_material.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/f))
 for n in ['CHECK_02','CHECK_07']:bpy.data.objects[n].data.lens=26
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/f))
