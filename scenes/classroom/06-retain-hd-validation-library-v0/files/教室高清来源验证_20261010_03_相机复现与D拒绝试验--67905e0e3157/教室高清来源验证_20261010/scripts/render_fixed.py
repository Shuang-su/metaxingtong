import bpy,json,hashlib
from pathlib import Path
p=Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010');s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3
s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
mapping=[('classroom_0919_front','SOURCE_A'),('classroom_2123_key','SOURCE_B'),('classroom_4284_wide','SOURCE_C'),('classroom_5447_key','SOURCE_D')]
for name,cam in mapping:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(p/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
print('FOUR FIXED CAMERAS FINISHED')
