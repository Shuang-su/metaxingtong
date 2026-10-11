import bpy
from pathlib import Path
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=False;s.cycles.samples=16;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.camera=bpy.data.objects['JOINT_F_path_080'];s.render.filepath='/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/tracked_desks_white/renders/F_path_080.png';bpy.ops.render.render(write_still=True)
