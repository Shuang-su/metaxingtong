import bpy,pathlib,json,hashlib,time
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R07';out.mkdir(exist_ok=True);records=[]
for mode in ('material','white'):
 path=P/'models'/f'R07_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.threads_mode='FIXED';s.render.threads=4
 for name in ['SOURCE_13_high','SOURCE_21_high']:
  f=out/f'{mode}_{name}.png'
  if f.exists():raise RuntimeError('Refuse overwriting existing final image: '+str(f))
  s.camera=bpy.data.objects[name];s.render.filepath=str(f);start=time.time();bpy.ops.render.render(write_still=True);b=f.read_bytes();records.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'model':str(path.relative_to(P)),'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':name,'resolution':[1192,671],'samples':32,'denoise':False,'seconds':time.time()-start,'status':'Diagnostic unaccepted; source cameras FAILED'});(P/'qa/R07-render-records.json').write_text(json.dumps(records,indent=2))
