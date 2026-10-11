import bpy
from pathlib import Path
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/six_bay_candidate/baseline_renders');p.mkdir(exist_ok=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.cycles.samples=16
for n in ['SOURCE_4298','SOURCE_4300','SOURCE_4310']:
 s.camera=bpy.data.objects[n];s.render.filepath=str(p/(n+'.png'));bpy.ops.render.render(write_still=True)
