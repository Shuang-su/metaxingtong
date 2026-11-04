import bpy,sys,json
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(__file__).resolve().parents[1];version=args[0] if args else 'R01';mode=args[1] if len(args)>1 else 'source'
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.cycles.use_denoising=False;scene.cycles.samples=48;scene.render.resolution_x=320;scene.render.resolution_y=176;scene.render.resolution_percentage=100
out=ROOT/'renders'/version;out.mkdir(exist_ok=True)
cams=[o for o in bpy.data.objects if o.type=='CAMERA' and (o.name.startswith('SRC') if mode=='source' else o.name.startswith('CHECK'))]
for c in cams:
 scene.camera=c;scene.view_layers['MATERIAL'].use=True;scene.view_layers['WHITE'].use=False
 scene.render.filepath=str(out/(c.name+'_material.png'));bpy.ops.render.render(write_still=True)
 if mode=='source':
  scene.view_layers['MATERIAL'].use=False;scene.view_layers['WHITE'].use=True
  scene.render.filepath=str(out/(c.name+'_white.png'));bpy.ops.render.render(write_still=True)
