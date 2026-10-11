import bpy,json,hashlib,sys
from pathlib import Path
r=Path(__file__).parent;only_c='--only-c' in sys.argv;records=[x for x in json.loads((r/'render_manifest.json').read_text()) if x['variant']=='B'] if only_c else []
for variant,path in [('B',r.parent/'candidate_b/hospital_endboard_shape_B.blend'),('C',r/'hospital_recess_outline_C.blend')]:
 if only_c and variant=='B':continue
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;original={'samples':s.cycles.samples,'use_adaptive_sampling':s.cycles.use_adaptive_sampling,'seed':s.cycles.seed};s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
 for vl in s.view_layers:vl.cycles.use_denoising=False
 for tag,name in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed')]:
  s.camera=bpy.data.objects[name];out=r/f'{tag}_{variant}_same_camera_16spp_raw.png';s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
  records.append({'path':out.name,'role':'new controlled comparison raw render','variant':variant,'source_blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_video_seconds':None,'original_saved_render_settings':original,'engine':s.render.engine,'samples':16,'adaptive_sampling':False,'denoise':False,'seed':s.cycles.seed,'threads':2,'resolution':[1920,1080],'camera':name,'camera_matrix_world':list(map(list,s.camera.matrix_world)),'lens_mm':s.camera.data.lens,'shift_x':s.camera.data.shift_x,'shift_y':s.camera.data.shift_y,'sensor_width':s.camera.data.sensor_width,'sensor_fit':s.camera.data.sensor_fit,'blender_version':bpy.app.version_string,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()});(r/'render_manifest.json').write_text(json.dumps(records,indent=2))
