import bpy,os
from pathlib import Path
os.sched_setaffinity(0,{sorted(os.sched_getaffinity(0))[-2]})
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R03_{mode}.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=16;s.cycles.use_denoising=False
 for name in ['SOURCE_P1_45','SOURCE_P2_32','SOURCE_P1_15']:
  p=D/f'renders/R03_{name}_{mode}_LOW.png'
  if p.exists():continue
  s.camera=bpy.data.objects[name];s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
print('LOW_DONE')
