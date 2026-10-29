import bpy,json,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c27';O=P/'renders';O.mkdir(exist_ok=True);out={'settings':{'engine':'CYCLES','samples':16,'denoise':False,'seed':0,'threads':8,'resolution':[1920,1080]},'renders':[]}
for kind,views in [('MATERIAL',['H','G','N642']),('WHITE',['H','G'])]:
 f=P/('hospital_C27_bank1_'+kind+'_CONDITIONAL.blend');sha=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.view_layers[0].cycles.use_denoising=False;s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
 for k in views:
  c=bpy.data.objects['C14_N642_fixed_windows_CONDITIONAL' if k=='N642' else 'C10_'+k+'_shared_sofa_height_CONDITIONAL'];s.camera=c;p=O/(k+'_C27_'+kind+'_RAW_1920x1080.png');s.render.filepath=str(p);t=time.time();bpy.ops.render.render(write_still=True)
  out['renders'].append({'kind':kind,'view':k,'camera':c.name,'camera_world_matrix':[list(r) for r in c.matrix_world],'lens':c.data.lens,'source_model_sha256':sha,'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':time.time()-t});(P/'render_manifest.json').write_text(json.dumps(out,indent=2)+'\n');print('C27_RENDER_READY',kind,k,flush=True)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==sha
