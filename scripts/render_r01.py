import bpy,pathlib,sys,json,time
P=pathlib.Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'preview'
log=[]
for tag in ['white','material']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'models/R01_{tag}.blend'))
 s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=12 if mode=='preview' else 48
 s.render.resolution_percentage=50 if mode=='preview' else 100
 cams=['SOURCE02_conditional_front','SOURCE05_conditional_close'] if mode in ['preview','source'] else sorted(o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('CHECK'))
 out=P/'renders'/('R01_'+mode);out.mkdir(parents=True,exist_ok=True)
 for name in cams:
  s.camera=bpy.data.objects[name];s.render.filepath=str(out/f'{tag}_{name}.png');t=time.time();bpy.ops.render.render(write_still=True)
  log.append({'file':s.render.filepath,'camera':name,'material_mode':tag,'seconds':time.time()-t,'samples':s.cycles.samples,'percentage':s.render.resolution_percentage})
  (out/'render-log.json').write_text(json.dumps(log,indent=2))
