"""Render all common cameras from the saved material BLEND without mutations."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];stage=sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=str(root/'models'/stage/'piano_seaside_material.blend'));sc=bpy.context.scene
names=['source_N6318','source_N4037','source_N2518','source_N2453','source_N6766','main','detail_cheek_right','detail_cheek_left','detail_bench']+[f'check_{i:02d}' for i in range(8)]+['check_top']
for name in names:
 sc.camera=bpy.data.objects[name];sc.render.resolution_x=960 if name.startswith('check') else 1920;sc.render.resolution_y=540 if name.startswith('check') else 1080;sc.render.filepath=str(root/'qa'/stage/(name+'.png'));bpy.ops.render.render(write_still=True)
print('SAVED_REVIEW_COMPLETE',len(names))
