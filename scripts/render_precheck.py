import bpy,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for kind,names in [('material',['MAIN','SRC_front','SRC_oblique']+[f'CHECK{i:02d}'for i in range(1,9)]),('white',['MAIN'])]:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/arcade_remake_R00_{kind}.blend'));s=bpy.context.scene;s.cycles.samples=4;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
 for name in names:
  s.camera=bpy.data.objects[name];s.render.filepath=str(D/f'renders/R00_precheck_{kind}_{name}.png');bpy.ops.render.render(write_still=True)
