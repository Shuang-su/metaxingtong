import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for variant in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/Xingtong_Classroom_{variant}.blend'))
 s=bpy.context.scene;s.cycles.samples=48;s.render.threads=6
 views=[('Level_Front','PANORAMA_Level_Front'),('Level_Windows','PANORAMA_Level_Windows')]
 if variant=='Textured': views += [('Match_A','MATCH_A_Front_00h15m19s'),('Match_B','MATCH_B_Windows_00h35m23s'),('Match_C_Wide','MATCH_C_Wide_01h11m24s'),('Desk_Detail','DETAIL_Desks_Podium')]
 for n,c in views:
  s.camera=bpy.data.objects[c];s.render.filepath=str(R/'renders'/f'Final_{variant}_{n}.png');bpy.ops.render.render(write_still=True)
