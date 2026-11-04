import bpy,pathlib,json,hashlib,time
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R09';out.mkdir(exist_ok=True);records=[];names=['SOURCE_13_high','SOURCE_14_front','SOURCE_15_exterior','SOURCE_21_high','CHECK_01','CHECK_03','CHECK_05','CHECK_07','MAIN_exterior']
for mode in ['material','white']:
 m=P/'models'/f'R09_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(m));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.threads_mode='FIXED';s.render.threads=6
 for name in names:
  f=out/f'{mode}_{name}.png'
  if f.exists():raise RuntimeError('Refuse overwrite: '+str(f))
  s.camera=bpy.data.objects[name];s.render.filepath=str(f);start=time.time();bpy.ops.render.render(write_still=True);records.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'model':str(m.relative_to(P)),'model_sha256':hashlib.sha256(m.read_bytes()).hexdigest(),'camera':name,'resolution':[1192,671],'samples':64,'denoise':False,'seconds':time.time()-start,'scope':'4 source hypotheses plus4 model check cameras and1 main; same geometry all views; source FAILED'});(P/'qa/R09-render-records.json').write_text(json.dumps(records,indent=2))
