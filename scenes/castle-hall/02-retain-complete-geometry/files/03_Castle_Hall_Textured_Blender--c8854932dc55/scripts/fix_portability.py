import bpy,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'))
for im in bpy.data.images:
 if im.source=='FILE':
  p=R/'restored/textures'/os.path.basename(im.filepath)
  if p.exists():
   if im.packed_file:im.unpack(method='REMOVE')
   im.filepath=str(p);im.reload();im.pack();im.filepath='//../textures/'+p.name
for m in bpy.data.materials:
 if m.users:m.use_backface_culling=True
bpy.context.scene.cycles.use_denoising=False;bpy.context.scene.cycles.samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'),compress=True)
print('PACKED',[(im.name,bool(im.packed_file),im.filepath) for im in bpy.data.images if im.source=='FILE'])
