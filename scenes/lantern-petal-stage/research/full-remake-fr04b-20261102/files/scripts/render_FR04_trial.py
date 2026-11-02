import bpy
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/FR04_{typ}.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.samples=8;s.view_settings.exposure=-1.3
 for cam in ['CHECK0','CHECK1','AUG23_CIRCLE_CONDITION_NOT_CALIBRATED']:
  s.camera=bpy.data.objects[cam];s.render.resolution_x=960 if cam.startswith('AUG') else 640;s.render.resolution_y=540 if cam.startswith('AUG') else 360;s.render.filepath=str(D/f'renders/FR04_{cam}_{typ}.png');bpy.ops.render.render(write_still=True)
