from pathlib import Path
D=Path(__file__).resolve().parent
exec((D/'scan.py').read_text().split('base_other=')[0])
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=4;s.cycles.use_denoising=False
for deg in [40,45]:
 setangle(deg);s.camera=bpy.data.objects['SOURCE7_CONDITIONAL_NOT_CALIBRATED'];s.render.filepath=str(D/f'preview-angle-{deg}.png');bpy.ops.render.render(write_still=True)
setangle(45);s.camera=bpy.data.objects['DIAGNOSTIC_side'];s.render.filepath=str(D/'preview-angle-45-side.png');bpy.ops.render.render(write_still=True)
