import bpy,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
for mode in ('white','material'):
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R01_{mode}.blend'));s=bpy.context.scene;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=50;s.render.threads=4
 for name in ('MAIN_exterior','SOURCE_13_high','SOURCE_14_front'):
  s.camera=bpy.data.objects[name];s.render.filepath=str(P/'renders'/f'R01_{mode}_{name}_preview.png');bpy.ops.render.render(write_still=True)
