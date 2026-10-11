import bpy
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/candidate_b');s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=12;s.cycles.use_denoising=False
for vl in s.view_layers:vl.cycles.use_denoising=False
s.camera=bpy.data.objects['MATCH_H'];s.render.filepath=str(r/'H_B_legacy_camera_1920.png');bpy.ops.render.render(write_still=True)
