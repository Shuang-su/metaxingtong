import bpy,json
from pathlib import Path
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/six_bay_candidate');s=bpy.context.scene
exec(Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/scripts/validate_six_bay_windows.py').read_text())
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/six_bay_candidate');s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for name in ['SOURCE_B','SOURCE_C','SOURCE_A','SOURCE_4298','SOURCE_4300','SOURCE_4310','MOTION_F_path_059','MOTION_F_path_073','MOTION_F_path_076','MOTION_F_path_080']:
 s.camera=bpy.data.objects[name];s.cycles.samples=16;s.render.filepath=str(p/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True);print('REGRESSION_DONE',name,flush=True)
print('TEN CANDIDATE VIEWS FINISHED')
