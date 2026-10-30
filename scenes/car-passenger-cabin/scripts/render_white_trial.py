import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_white.blend'))
s=bpy.context.scene;s.render.resolution_percentage=50;s.cycles.samples=24;s.cycles.use_denoising=False
s.camera=bpy.data.objects['SRC_S03_closed'];s.render.filepath=str(R/'qa/white_trial_S03_960x540.png');bpy.ops.render.render(write_still=True)
