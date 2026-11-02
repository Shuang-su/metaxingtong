# Frozen conditional camera and identical geometry; native-size output, low-sample diagnostic.
import bpy
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/NOV2_CP02_workcamera_{typ}.blend'));s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads=2;s.cycles.samples=4;s.cycles.use_denoising=False;s.render.filepath=str(D/f'renders/NOV2_CP02_near_bay_{typ}_native4k.png');bpy.ops.render.render(write_still=True)
