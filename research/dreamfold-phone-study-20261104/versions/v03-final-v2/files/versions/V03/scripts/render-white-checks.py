import bpy
from pathlib import Path
V=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(V/'models/phone-white.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=16;s.cycles.use_denoising=False
for name,cam in [('white-source7','SOURCE7_CONDITIONAL_NOT_CALIBRATED'),('white-diagnostic-side','DIAGNOSTIC_side')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(V/f'renders/{name}.png');bpy.ops.render.render(write_still=True)
