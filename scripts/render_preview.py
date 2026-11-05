import bpy
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r01.blend'))
bpy.context.scene.cycles.use_denoising=False
bpy.context.scene.render.filepath=str(P/'renders/preview11.png')
bpy.ops.render.render(write_still=True)
