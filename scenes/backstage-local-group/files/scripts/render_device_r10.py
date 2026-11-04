import bpy,pathlib,json,hashlib
from mathutils import Matrix
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R10';out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(P/'models/R10_material.blend'));c=bpy.data.objects['DIAG_device_front'];M=[list(r) for r in c.matrix_world];lens=c.data.lens;clip=c.data.clip_start;records=[]
for version in ['R09','R10']:
 for mode in ['material','white']:
  model=P/'models'/f'{version}_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;c=bpy.data.objects.get('DIAG_device_front')
  if c is None:
   d=bpy.data.cameras.new('DIAG_device_front');d.lens=lens;d.clip_start=clip;c=bpy.data.objects.new('DIAG_device_front',d);bpy.context.collection.objects.link(c);c.matrix_world=Matrix(M)
  s.camera=c;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6;s.render.filepath=str(out/f'{version}_{mode}_DIAG_device_front.png');bpy.ops.render.render(write_still=True);f=pathlib.Path(s.render.filepath);records.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'model':str(model.relative_to(P)),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'camera':'DIAG_device_front','camera_matrix':[list(r) for r in c.matrix_world],'lens':c.data.lens,'clip_start':c.data.clip_start,'samples':64,'denoise':False,'resolution':[1192,671],'scope':'one artificial macro; R09 camera added in memory only, no historical model overwritten'});(P/'qa/R10-render-records.json').write_text(json.dumps(records,indent=2))
