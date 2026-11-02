import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'stages/r06-review-candidate';Q=O/'preflight';Q.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'harbor-r06-material.blend'));s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=960;s.render.resolution_y=540
for name in ['SOURCE_PREVIEW_FRONT_CONDITIONAL','CHECK_BAND_L','CHECK_BAND_R','CHECK_LED_INNER','CHECK_LED_OUTER_BACK']:
    s.camera=bpy.data.objects[name];s.render.filepath=str(Q/(name+'.png'));bpy.ops.render.render(write_still=True)
print('R06_PREFLIGHT_READY')
