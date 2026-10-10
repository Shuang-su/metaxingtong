import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'deliverables/01_train_material.blend'));s=bpy.context.scene;s.camera=bpy.data.objects['MATCH_B_45m12_left_booth'];s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/final_B_material.png');bpy.ops.render.render(write_still=True)
