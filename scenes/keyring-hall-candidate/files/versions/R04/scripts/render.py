import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/keyring-material.blend'))
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.use_denoising=False
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if 'preview' in args:s.render.resolution_percentage=40;s.cycles.samples=4
for name in ['source17-conditional','source20-conditional','source21-conditional'] if 'preview' in args else [o.name for o in s.objects if o.type=='CAMERA']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/((('preview-' if 'preview' in args else '')+name)+'.png'));bpy.ops.render.render(write_still=True)
