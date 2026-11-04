import bpy,pathlib,json,hashlib,time
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];defs=json.loads((P/'qa/R08-diagnostic-cameras.json').read_text());out=P/'renders/R08';out.mkdir(exist_ok=True);records=[]
for stage in ['R07','R08']:
 p=P/'models'/f'{stage}_white.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=64;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
 for a in defs:
  if a['name'] not in bpy.data.objects:
   d=bpy.data.cameras.new(a['name']);d.lens=a['lens'];d.clip_start=.001;d.clip_end=100;o=bpy.data.objects.new(a['name'],d);bpy.context.collection.objects.link(o);o.location=a['position'];o.rotation_euler=(Vector(a['target'])-o.location).to_track_quat('-Z','Y').to_euler()
  s.camera=bpy.data.objects[a['name']];f=out/f'{stage}_white_{a["name"]}.png'
  if f.exists():raise RuntimeError('Refuse overwrite '+str(f))
  s.render.filepath=str(f);t=time.time();bpy.ops.render.render(write_still=True);data=f.read_bytes();records.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'model':str(p.relative_to(P)),'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':a,'samples':64,'denoise':False,'threads':6,'resolution':[1192,671],'seconds':time.time()-t,'scope':'synthetic contact macro; original lights/world; R07 temporary matching cameras only, no model save'});(P/'qa/R08-contact-render-records.json').write_text(json.dumps(records,indent=2))
