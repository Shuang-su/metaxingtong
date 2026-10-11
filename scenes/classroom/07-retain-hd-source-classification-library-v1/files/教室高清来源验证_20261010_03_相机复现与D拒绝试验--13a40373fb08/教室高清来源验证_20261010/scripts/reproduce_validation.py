"""Portable replay. Uses existing frozen classroom Blend; does not distribute/change it."""
import argparse,pathlib,json,hashlib,subprocess,textwrap
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--baseline',required=True);ap.add_argument('--blender',default='/usr/bin/blender');ap.add_argument('--root',default=str(pathlib.Path(__file__).resolve().parents[1]));ap.add_argument('--outdir');ap.add_argument('--rejected-trial',action='store_true');args=ap.parse_args();root=pathlib.Path(args.root).resolve();baseline=pathlib.Path(args.baseline).resolve();out=pathlib.Path(args.outdir).resolve() if args.outdir else root/'reproduced';out.mkdir(exist_ok=True,parents=True)
expected='77be8336b43f7cf6c413369c6bef2bd46b5e8508f1958b0fb4d8a172e457c908';actual=hashlib.sha256(baseline.read_bytes()).hexdigest();assert actual==expected,'Wrong baseline Blend; do not silently substitute another version.'
for m in json.loads((root/'source/capture_manifest.json').read_text()):
 f=root/'source'/pathlib.Path(m['crop_filename']).name;assert hashlib.sha256(f.read_bytes()).hexdigest()==m['crop_sha256']
job={'root':str(root),'out':str(out),'rejected':args.rejected_trial};(out/'replay_job.json').write_text(json.dumps(job))
worker=r'''
import bpy,json,sys
from pathlib import Path
j=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());root=Path(j['root']);out=Path(j['out']);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
f=json.loads((root/'qa/motion_camera_fit.json').read_text());c=bpy.data.objects.new('HD_E_reproduced',bpy.data.cameras.new('HD_E_reproduced'));s.collection.objects.link(c);c.location=f['camera_location'];c.rotation_euler=f['camera_rotation_xyz'];c.data.lens=f['lens_mm'];c.data.sensor_width=36;bpy.context.view_layer.update()
views=[('classroom_0919_front','SOURCE_A',16),('classroom_2123_key','SOURCE_B',16),('classroom_4284_wide','SOURCE_C',64),('classroom_5447_key','SOURCE_D',64),('classroom_motion_4282',c.name,16)]
if j['rejected']:
 for prefix,dy in [('R2C1',-.3),('R3C2',-.2)]:
  for o in bpy.data.objects:
   if o.name.startswith(prefix+' '):o.location.y+=dy
 bpy.context.view_layer.update();views=[('classroom_4284_wide','SOURCE_C',16),('classroom_5447_key','SOURCE_D',16)]
for name,cam,samples in views:
 s.camera=bpy.data.objects[cam];s.cycles.samples=samples;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
'''
workerpath=out/'replay_blender.py';workerpath.write_text(worker);subprocess.run([args.blender,'-b',str(baseline),'-t','3','--python',str(workerpath),'--',str(out/'replay_job.json')],check=True)
for render in out.glob('classroom_*.png'):
 if render.stem.endswith('_50percent'):continue
 source=root/'source'/(render.stem+'_video.png');a=Image.open(source).convert('RGB');b=Image.open(render).convert('RGB');assert a.size==b.size==(1180,664);Image.blend(a,b,.5).save(out/(render.stem+'_50percent.png'))
assert hashlib.sha256(baseline.read_bytes()).hexdigest()==expected
(out/'replay_status.json').write_text(json.dumps({'baseline_sha256':expected,'baseline_not_written':True,'rejected_trial':args.rejected_trial,'note':'Monte Carlo render bytes may vary by platform. Geometry/camera/source coordinates, not output image hash, are the cross-platform comparison target.'},indent=2));print(out)
