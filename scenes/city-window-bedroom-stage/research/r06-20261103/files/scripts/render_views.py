"""Render declared cameras from one frozen scene; never modify geometry per camera."""
import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
model, config, outdir = map(Path,args[:3]); outdir.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(model)); s=bpy.context.scene
cfg=json.loads(config.read_text()); s.render.engine='CYCLES'
s.cycles.samples=cfg.get('samples',16); s.cycles.use_denoising=False
s.cycles.max_bounces=6; s.cycles.diffuse_bounces=3; s.cycles.glossy_bounces=3; s.cycles.transmission_bounces=4
s.cycles.use_adaptive_sampling=True; s.cycles.adaptive_threshold=cfg.get('adaptive_threshold',.05); s.cycles.adaptive_min_samples=8
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
