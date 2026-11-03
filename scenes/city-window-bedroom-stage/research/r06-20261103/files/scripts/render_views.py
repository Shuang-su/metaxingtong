"""Render declared cameras from one frozen scene; never modify geometry per camera."""
import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
model, config, outdir = map(Path,args[:3]); outdir.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(model)); s=bpy.context.scene
cfg=json.loads(config.read_text()); s.render.engine='CYCLES'
s.cycles.samples=cfg.get('samples',16); s.cycles.use_denoising=False
s.render.threads_mode='FIXED';s.render.threads=cfg.get('threads',4)
s.render.image_settings.file_format='PNG'; s.render.resolution_percentage=100
records=[]
for item in cfg['views']:
    cam=bpy.data.objects[item['camera']]
    assert cam.type=='CAMERA'
    s.camera=cam;s.render.resolution_x=item['width'];s.render.resolution_y=item['height']
    s.render.filepath=str(outdir/item['filename'])
    bpy.ops.render.render(write_still=True)
    records.append(dict(item,actual_path=s.render.filepath,rendered=True))
    (outdir/'render-status.json').write_text(json.dumps({'input':str(model),'views':records},indent=2))
