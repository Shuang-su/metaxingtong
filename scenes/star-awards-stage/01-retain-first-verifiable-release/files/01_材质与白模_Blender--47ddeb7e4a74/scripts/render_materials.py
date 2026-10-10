import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Star_Awards_Candidate.blend'));sc=bpy.context.scene;sc.cycles.use_denoising=False;sc.render.threads=4
mode=sys.argv[-1]
if mode=='source':names=['源机位_A','源机位_B','源机位_C'];sc.cycles.samples=24;sc.render.resolution_x=1180;sc.render.resolution_y=663
else:names=sorted(o.name for o in sc.objects if o.type=='CAMERA' and o.name.startswith('普通'));sc.cycles.samples=12;sc.render.resolution_x=800;sc.render.resolution_y=450
for n in names:
 sc.camera=bpy.data.objects[n];sc.render.resolution_percentage=100;sc.render.filepath=str(P/'renders'/f'{n}_材质.png');bpy.ops.render.render(write_still=True)
