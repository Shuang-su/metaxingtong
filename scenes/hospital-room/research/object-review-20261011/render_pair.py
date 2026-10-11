import bpy
from pathlib import Path
root=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit')
for variant,path in [('baseline',root/'models/extracted/hospital_complete_materials.blend'),('candidate',root/'candidate/hospital_endboard_shape_candidate.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_denoising=False
 for vl in s.view_layers:vl.cycles.use_denoising=False
 for tag,name in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed')]:
  s.camera=bpy.data.objects[name];s.render.filepath=str(root/'candidate'/f'{tag}_{variant}_legacy_camera_1920.png');bpy.ops.render.render(write_still=True)
