import bpy,json
from pathlib import Path
O=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(O.parent/'keyring-underbridge-r07-20261104/models/r07b-material.blend'));s=bpy.context.scene
out={'render':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'camera':{}}
for n in [17,20,21]:
 c=s.objects[f'source{n}-conditional'];out['camera'][str(n)]={'type':c.data.type,'scale':list(c.scale),'clip_start':c.data.clip_start,'clip_end':c.data.clip_end,'dof':c.data.dof.use_dof,'frame':[list(v) for v in c.data.view_frame(scene=s)]}
(O/'camera-scope.json').write_text(json.dumps(out,indent=2))
