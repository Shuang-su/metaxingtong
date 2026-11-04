import bpy,pathlib,json,hashlib,time
P=pathlib.Path(__file__).resolve().parents[1];records=[]
for mode in ['material','white']:
 model=P/'models'/f'R06_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.camera=bpy.data.objects['MAIN_exterior'];s.cycles.samples=128;s.cycles.use_denoising=False;s.render.threads=4;s.render.resolution_percentage=100;s.render.resolution_x=1192;s.render.resolution_y=671;f=P/'renders/R06'/f'{mode}_MAIN_exterior_128s.png'
 if f.exists():raise RuntimeError('Do not overwrite completed high-sample main')
 s.render.filepath=str(f);start=time.time();bpy.ops.render.render(write_still=True);records.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'model':str(model.relative_to(P)),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'camera':'MAIN_exterior','samples':128,'resolution':[1192,671],'geometry_changed':False,'denoise':False,'seconds':time.time()-start,'purpose':'Lower-noise main only. Does not improve source alignment or acceptance.'});(P/'qa/R06-main-quality-records.json').write_text(json.dumps(records,indent=2))
