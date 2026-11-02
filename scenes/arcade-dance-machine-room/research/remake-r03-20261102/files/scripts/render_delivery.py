import bpy
from pathlib import Path
D=Path(__file__).resolve().parents[1]
# PNG validity is checked outside Blender before resume; skip only validated names passed in file.
skip=set((D/'qa/valid_delivery_pngs.txt').read_text().splitlines()) if (D/'qa/valid_delivery_pngs.txt').exists() else set()
for kind,names in [('material',['MAIN','SRC_front','SRC_oblique']+[f'CHECK{i:02d}'for i in range(1,9)]),('white',['MAIN','SRC_front','SRC_oblique'])]:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/arcade_remake_R02_{kind}.blend'));s=bpy.context.scene;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=100
 for name in names:
  filename=f'R02_delivery_{kind}_{name}.png'
  if filename in skip:continue
  s.cycles.samples=16 if name.startswith('CHECK') else 24
  s.render.resolution_x=640 if name.startswith('CHECK') else 1920;s.render.resolution_y=360 if name.startswith('CHECK') else 1080
  s.camera=bpy.data.objects[name];s.render.filepath=str(D/'renders'/filename);bpy.ops.render.render(write_still=True)
