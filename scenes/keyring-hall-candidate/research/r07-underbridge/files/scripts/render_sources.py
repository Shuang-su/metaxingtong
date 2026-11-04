import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];records=[]
for variant in ['material','white']:
 f=R/'models'/f'r07b-{variant}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=64 if variant=='material' else 32;s.cycles.use_denoising=False;s.render.resolution_percentage=100
 for cam in ['source17-conditional','source20-conditional','source21-conditional']+(['inspection-05'] if variant=='material' else []):
  s.camera=s.objects[cam];p=R/'renders'/f'{variant}-{cam}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);records.append({'file':str(p.relative_to(R)),'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'camera':cam,'samples':s.cycles.samples,'dimensions':[1192,671],'source_lights':'original R06 three AREA and World only; NO diagnostic fill','object_visibility':'all unchanged; no camera-specific hiding'})
(R/'docs/render-records.json').write_text(json.dumps(records,indent=2))
