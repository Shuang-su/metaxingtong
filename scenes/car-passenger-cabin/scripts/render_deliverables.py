import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_material.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.use_denoising=False;s.cycles.samples=96;s.render.resolution_percentage=100
s.render.image_settings.color_mode='RGB';s.render.image_settings.file_format='PNG'
jobs=[('MAIN_passenger_local',1,'renders/main/car_passenger_cabin_main.png',1920,1080,128,'normal bounded-candidate main view'),
 ('SRC_S01_closed',1,'renders/source/S01_render_closed.png',1920,1080,72,'uncalibrated source comparison'),
 ('SRC_S02_open',2,'renders/source/S02_render_open.png',1920,1080,72,'uncalibrated source comparison, explicit open state'),
 ('SRC_S03_closed',1,'renders/source/S03_render_closed.png',1920,1080,72,'uncalibrated source comparison'),
 ('CTX_S04_forward_not_registered',1,'renders/source/S04_context_only_render.png',1920,1080,40,'conditional narrative context; forward controls not reconstructed')]
jobs += [(f'CHECK_{i:02}',1,f'renders/checks/check_{i:02}_closed.png',1280,960,48,'arbitrary geometry inspection; fixed diagnostic light') for i in range(1,9)]
jobs += [('MAIN_passenger_local',2,'renders/checks/check_09_open_state.png',1280,960,48,'additional explicit open state inspection')]
filtered='--' in sys.argv
if filtered:
 sel=sys.argv[sys.argv.index('--')+1:];jobs=[j for j in jobs if j[0] in sel]
manifest=json.loads((R/'qa/render-manifest.json').read_text()) if filtered and (R/'qa/render-manifest.json').exists() else []
for cam,frame,path,w,h,samples,role in jobs:
 s.camera=bpy.data.objects[cam];s.frame_set(frame);s.render.resolution_x=w;s.render.resolution_y=h;s.cycles.samples=samples;s.render.filepath=str(R/path)
 bpy.ops.render.render(write_still=True)
 entry={'camera':cam,'frame':frame,'state':'closed' if frame==1 else 'open','path':path,'dimensions':[w,h],'samples':samples,'role':role,'location':list(s.camera.location),'rotation_euler':list(s.camera.rotation_euler),'lens_mm':s.camera.data.lens,'geometry_digest':s.get('geometry_digest'),'camera_calibration':'manual approximation; not accepted','lighting':'identical fixed neutral diagnostic rig in all views','mesh_visibility':'all meshes present; no per-camera switches'}
 matches=[i for i,x in enumerate(manifest) if x['path']==path]
 if matches:manifest[matches[0]]=entry
 else:manifest.append(entry)
 (R/'qa/render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
