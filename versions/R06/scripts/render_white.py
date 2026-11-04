import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/keyring-white.blend'))
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=False;s.cycles.samples=32;s.render.resolution_percentage=100
for name in ['source17-conditional','source20-conditional','source21-conditional']+['inspection-%02d'%i for i in range(1,9)]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/('white-'+name+'.png'));bpy.ops.render.render(write_still=True)
