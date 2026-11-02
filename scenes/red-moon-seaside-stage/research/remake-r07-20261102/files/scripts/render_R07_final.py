import bpy,os,json,hashlib,time
from pathlib import Path
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[-6:]))
D=Path(__file__).resolve().parents[1];OUT=D/'renders/final-R07';OUT.mkdir(exist_ok=True)
source_sizes={'SOURCE_P1_45':(1920,1080),'SOURCE_P2_32':(3840,2160),'SOURCE_P1_15':(1920,1080)}
for mode in['material','white']:
 path=D/f'models/R07_{mode}.blend';modelsha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=32;s.cycles.use_denoising=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.resolution_percentage=100
 jobs=list(source_sizes.items())
 if mode=='material':jobs += [('MAIN',(1600,1000))]+[(f'CHECK_{i:02d}',(1200,800))for i in range(8)]
 for name,wh in jobs:
  png=OUT/f'R07_{name}_{mode}.png';meta=png.with_suffix('.json')
  if png.exists() and meta.exists():
   old=json.loads(meta.read_text());assert old['model_sha256']==modelsha;assert hashlib.sha256(png.read_bytes()).hexdigest()==old['png_sha256'];continue
  s.camera=bpy.data.objects[name];s.render.resolution_x,s.render.resolution_y=wh;s.render.filepath=str(png);t=time.time();bpy.ops.render.render(write_still=True)
  meta.write_text(json.dumps({'version':'R07','model':str(path.relative_to(D)),'model_sha256':modelsha,'camera':name,'size_wh':wh,'role':'same-camera-native-size render'if name in source_sizes else 'internal check, NOT source viewpoint','all_three_sources_are_training':True,'same_geometry_no_per_camera_hiding':True,'samples':32,'denoise':False,'cpu_threads':6,'seconds':time.time()-t,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'png_bytes':png.stat().st_size},indent=2));print('PERSISTED',png,flush=True)
print('R07_FINAL_15_RENDERS_COMPLETE',flush=True)
