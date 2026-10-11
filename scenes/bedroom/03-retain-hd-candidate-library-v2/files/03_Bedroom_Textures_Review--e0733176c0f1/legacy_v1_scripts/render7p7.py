import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'final7p7'
bpy.ops.wm.open_mainfile(filepath=str(D/'models/01_bedroom_material.blend'));s=bpy.context.scene
s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads=4
cams=sorted([o for o in s.objects if o.type=='CAMERA' and o.name[:2].isdigit()],key=lambda o:o.name)
for n,stem in [('MATCH_front_50m07_same_axis','source_front'),('MATCH_close_50m10_same_axis','source_close')]:
 s.camera=bpy.data.objects[n];s.render.resolution_x=1188;s.render.resolution_y=668;s.render.filepath=str(D/'renders'/(stem+'_material.png'));bpy.ops.render.render(write_still=True)
for o in cams:
 s.camera=o;s.render.filepath=str(D/'renders'/(o.name+'.png'));bpy.ops.render.render(write_still=True)
