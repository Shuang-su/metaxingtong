import bpy
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/candidate');s=bpy.context.scene;s.render.resolution_x=800;s.render.resolution_y=450;s.render.resolution_percentage=100;s.cycles.samples=4;s.cycles.use_denoising=False
for vl in s.view_layers:vl.cycles.use_denoising=False
out=r/'ordinary_checks';out.mkdir(exist_ok=True)
for c in sorted([o for o in s.objects if o.type=='CAMERA' and any(o.name.startswith('VIEW_%02d'%i) for i in range(1,9))],key=lambda x:x.name):
 s.camera=c;s.render.filepath=str(out/(c.name+'.png'));bpy.ops.render.render(write_still=True)
