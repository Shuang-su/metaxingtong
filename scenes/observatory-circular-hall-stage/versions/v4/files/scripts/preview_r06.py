import bpy,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
for mode in ('white','material'):
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));s=bpy.context.scene;s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_percentage=50;s.render.threads=4
 for name in ('SOURCE_15_exterior','SOURCE_13_high','SOURCE_14_front','SOURCE_21_high'):
  s.camera=bpy.data.objects[name];s.render.filepath=str(P/'renders'/f'R06_{mode}_{name}_preview.png');bpy.ops.render.render(write_still=True)
