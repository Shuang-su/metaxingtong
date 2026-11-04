import bpy,json,pathlib,hashlib
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R08';out.mkdir(exist_ok=True);records=[]
for version in ['R07','R08']:
 for mode in ['material','white']:
  model=P/'models'/f'{version}_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.camera=bpy.data.objects['SOURCE_15_exterior'];s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_percentage=100;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.filepath=str(out/f'{version}_{mode}_SOURCE15.png');bpy.ops.render.render(write_still=True)
  records.append({'path':str(pathlib.Path(s.render.filepath).relative_to(P)),'sha256':hashlib.sha256(pathlib.Path(s.render.filepath).read_bytes()).hexdigest(),'bytes':pathlib.Path(s.render.filepath).stat().st_size,'model':str(model.relative_to(P)),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'camera':'SOURCE_15_exterior','resolution':[1192,671],'samples':64,'denoise':False});(P/'qa/R08-render-records.json').write_text(json.dumps(records,indent=2))
