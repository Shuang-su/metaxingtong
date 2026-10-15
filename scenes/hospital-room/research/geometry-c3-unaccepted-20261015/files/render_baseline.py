import bpy,json,time,hashlib
from pathlib import Path
r=Path(__file__).parent;out=r/'renders_D_baseline';out.mkdir(exist_ok=True);s=bpy.context.scene
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True; s.view_layers[0].cycles.use_denoising=False; # inherited raw-noise layer state, explicitly retained
s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=4
manifest=[]
for k,n in [('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H'),('F','MATCH_F_Turning_Right')]:
 s.camera=bpy.data.objects[n];s.render.filepath=str(out/f'{k}_D_RAW_1920x1080.png');t=time.time();bpy.ops.render.render(write_still=True);p=Path(s.render.filepath);manifest.append({'view':k,'camera':n,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':time.time()-t,'samples':16,'denoising':True,'render_transform':'none','geometry':'unchanged D'});(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
