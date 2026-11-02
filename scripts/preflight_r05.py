import bpy,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'stages/r05-review-candidate';Q=O/'preflight';Q.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'harbor-r05-material.blend'));sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16;sc.render.resolution_x=768;sc.render.resolution_y=432
for name in ['SOURCE_PREVIEW_FRONT_CONDITIONAL','CHECK_LED_INNER','CHECK_LED_OUTER_FRONT','CHECK_LED_OUTER_BACK']:
    sc.camera=bpy.data.objects[name];sc.render.filepath=str(Q/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'harbor-r05-white.blend'));sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16;sc.render.resolution_x=768;sc.render.resolution_y=480
for i in [3,4,6,7]:
    name='CHECK_EFFECTIVE_%02d'%i;sc.camera=bpy.data.objects[name];sc.render.filepath=str(Q/(name+'.png'));bpy.ops.render.render(write_still=True)
print('R05_PREFLIGHT_READY')
