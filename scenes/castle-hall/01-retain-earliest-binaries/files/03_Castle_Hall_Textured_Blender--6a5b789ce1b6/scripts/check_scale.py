import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_Textured.blend'));s=bpy.context.scene;s.camera=bpy.data.objects['MATCH_A_45m15_empty_aisle'];s.cycles.samples=16;s.render.resolution_percentage=65;s.render.threads=3;s.render.filepath=str(R/'renders/scale_check_A.png');bpy.ops.render.render(write_still=True)
