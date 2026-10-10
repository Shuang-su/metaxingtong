import bpy
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Star_Awards_Candidate.blend'));sc=bpy.context.scene;sc.cycles.samples=6;sc.render.threads=2;sc.render.resolution_percentage=50;sc.camera=bpy.data.objects['源机位_C'];sc.render.filepath=str(P/'qa/preview_C.png');bpy.ops.render.render(write_still=True)
