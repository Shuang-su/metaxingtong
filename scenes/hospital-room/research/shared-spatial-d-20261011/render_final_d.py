import os
import bpy,json,hashlib,time
from pathlib import Path
r=Path(__file__).parent;rec=[]
for variant,path,views in [('D',r/'hospital_spatial_D.blend','FGH'),('B',Path(os.environ.get('HOSPITAL_B_BASELINE',str(r.parent/'candidate_b/hospital_endboard_shape_B.blend'))),'H')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=2
 for vl in s.view_layers:vl.cycles.use_denoising=False
 for k in views:
  n={'F':'MATCH_F_Turning_Right','G':'MATCH_G_Sofa_And_Bed','H':'MATCH_H'}[k];s.camera=bpy.data.objects[n];out=r/f'{k}_{variant}_full_1920_16spp_raw.png';s.render.filepath=str(out);ts=time.monotonic();bpy.ops.render.render(write_still=True)
  rec.append({'view':k,'variant':variant,'path':out.name,'source_blend':path.name,'source_blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':n,'camera_world_matrix':list(map(list,s.camera.matrix_world)),'lens_mm':s.camera.data.lens,'sensor_width_mm':s.camera.data.sensor_width,'engine':s.render.engine,'device':s.cycles.device,'threads':s.render.threads,'resolution':[1920,1080],'samples':s.cycles.samples,'adaptive_sampling':s.cycles.use_adaptive_sampling,'seed':s.cycles.seed,'denoise':False,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'runtime_seconds':time.monotonic()-ts,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()});(r/'render_manifest.json').write_text(json.dumps(rec,indent=2))
