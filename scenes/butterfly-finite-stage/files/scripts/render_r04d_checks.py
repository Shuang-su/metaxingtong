import bpy,pathlib,json,time,hashlib
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R04D_checks';out.mkdir(exist_ok=True);log=[]
for tag in ['white','material']:
 inp=P/f'models/R04D_{tag}.blend';bpy.ops.wm.open_mainfile(filepath=str(inp));s=bpy.context.scene
 s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=96;s.cycles.use_denoising=False;s.render.resolution_percentage=100
 for name in sorted(o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('CHECK')):
  s.camera=bpy.data.objects[name];s.render.filepath=str(out/f'{tag}_{name}.png');t=time.time();bpy.ops.render.render(write_still=True)
  log.append({'input':str(inp.relative_to(P)),'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'file':str(pathlib.Path(s.render.filepath).relative_to(P)),'camera':name,'lens':s.camera.data.lens,'camera_world_matrix':[list(r) for r in s.camera.matrix_world],'material_mode':tag,'seconds':time.time()-t,'samples':96,'resolution':[1192,671],'percentage':100,'status':'diagnostic view of finite hypothesized shell; NOT source evidence'})
  (out/'render-log.json').write_text(json.dumps(log,indent=2))
