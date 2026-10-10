import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];item=next(x for x in json.loads((R/'frozen_r03/freeze_manifest.json').read_text())['blends'] if x['kind']=='material');p=Path(item['file']);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;lightnames=[o.name for o in s.objects if o.type=='LIGHT'];worldname=s.world.name;settings={'exposure':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'gamma':s.view_settings.gamma}
glb=R/'deliverables/03_train_material.glb';gh=hashlib.sha256(glb.read_bytes()).hexdigest();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene
with bpy.data.libraries.load(str(p),link=False) as (src,dst):dst.objects=lightnames;dst.worlds=[worldname]
for o in dst.objects:
 if o:s.collection.objects.link(o)
s.world=dst.worlds[0]
for k,v in settings.items():setattr(s.view_settings,k,v)
s.camera=bpy.data.objects['INSPECT_01_forward_aisle'];s.render.engine='CYCLES';s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=16;s.cycles.use_denoising=False;s.cycles.max_bounces=8;s.cycles.transmission_bounces=6;s.render.resolution_x=590;s.render.resolution_y=332;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';out=R/'renders_r03/material_GLB_reimport_50.png';s.render.filepath=str(out)
meta={'input_glb':glb.name,'input_glb_sha256':gh,'input_blend_sha256_at_load':item['sha256'],'appended_from_blend':'lights and world only; no geometry/materials appended','camera':'INSPECT_01_forward_aisle','render_pixels':[590,332],'samples':16,'threads':2,'postprocess':'none raw'};out.with_suffix('.input.json').write_text(json.dumps(meta,indent=2));bpy.ops.render.render(write_still=True);meta['output_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.json').write_text(json.dumps(meta,indent=2))
