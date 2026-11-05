import bpy,pathlib,json,time
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R04D_contact8';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R04D_white.blend'));s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=50
log=[]
for name in sorted(o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('CHECK')):
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/f'{name}.png');t=time.time();bpy.ops.render.render(write_still=True)
 log.append({'camera':name,'location':list(s.camera.location),'matrix_world':[list(r) for r in s.camera.matrix_world],'image':s.render.filepath,'seconds':time.time()-t,'samples':8,'resolution_percentage':50})
 (out/'contact8-log.json').write_text(json.dumps(log,indent=2))
