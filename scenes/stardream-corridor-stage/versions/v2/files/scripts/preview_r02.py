import bpy,pathlib,hashlib,json,time
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R02';out.mkdir(exist_ok=True);rec=[]
for mode in ['white','material']:
 p=P/'models'/f'R02_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_percentage=60;s.render.threads_mode='FIXED';s.render.threads=4
 for cam in ['SOURCE_08_wide','SOURCE_23_oblique','SOURCE_26_side']:
  f=out/f'{mode}_{cam}_preview.png';s.camera=bpy.data.objects[cam];s.render.filepath=str(f);bpy.ops.render.render(write_still=True);rec.append({'file':str(f.relative_to(P)),'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'camera':cam,'samples':12,'percentage':60,'purpose':'low-sample preview, not source-resolution comparison'});(P/'qa/R02-preview-records.json').write_text(json.dumps(rec,indent=2))
