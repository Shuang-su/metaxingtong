import bpy,pathlib,json,hashlib,time
P=pathlib.Path(__file__).resolve().parents[1];rec=[]
for mode in ['material','white']:
 f=P/'models'/f'R03_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=16
 for camera in ['MAIN_local','TABLE_high','RACK_local']:
  s.camera=bpy.data.objects[camera];p=P/'renders'/f'R03_{mode}_{camera}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);data=p.read_bytes();rec.append({'path':str(p.relative_to(P)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'camera':camera,'samples':16,'scope':'diagnostic local assemblage; no source match/no whole room'})
  (P/'qa/R01-preview-records.json').write_text(json.dumps(rec,indent=2))
