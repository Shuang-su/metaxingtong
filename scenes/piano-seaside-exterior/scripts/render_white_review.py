"""White material inspection only, with the same geometry, cameras and lights."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];stage=sys.argv[-1];qa=root/'qa'/stage
bpy.ops.wm.open_mainfile(filepath=str(root/'models'/stage/'piano_seaside_white.blend'));sc=bpy.context.scene
for name in ['main','detail_cheek_right','detail_cheek_left','detail_bench']:
 sc.camera=bpy.data.objects[name];sc.render.resolution_x=1920 if name=='main' else 960;sc.render.resolution_y=1080 if name=='main' else 540;sc.render.filepath=str(qa/('white_'+name+'.png'));bpy.ops.render.render(write_still=True)
