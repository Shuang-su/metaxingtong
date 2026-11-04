import bpy,pathlib,json,hashlib,time
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R07';out.mkdir(exist_ok=True);records=[]
for mode in ['material','white']:
 p=P/'models'/f'R07_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
 for name in ['CHECK_05','SOURCE_08_wide']:
  s.cycles.samples=32 if name.startswith('CHECK') else 64;f=out/f'{mode}_{name}.png'
  if f.exists():raise RuntimeError('Refuse overwrite '+str(f))
  s.camera=bpy.data.objects[name];s.render.filepath=str(f);t=time.time();bpy.ops.render.render(write_still=True);b=f.read_bytes();records.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'model':str(p.relative_to(P)),'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':name,'resolution':[1192,671],'samples':s.cycles.samples,'denoise':False,'threads':6,'seconds':time.time()-t,'scope':'R07 local grid repair, NOT full new suite/source validation'});(P/'qa/R07-render-records.json').write_text(json.dumps(records,indent=2))
