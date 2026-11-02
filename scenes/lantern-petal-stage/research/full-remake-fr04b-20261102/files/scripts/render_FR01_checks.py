import bpy
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/FR01_{typ}.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.samples=4;s.render.resolution_x=640;s.render.resolution_y=360
 for i in range(8):
  s.camera=bpy.data.objects['CHECK'+str(i)];s.render.filepath=str(D/f'renders/FR01_CHECK{i}_{typ}.png');bpy.ops.render.render(write_still=True)
