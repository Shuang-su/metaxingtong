import bpy,pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');O=pathlib.Path(__file__).parent;records=[]
for case in ['H0_original','H1_upper_opening_plus1p2']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models/R09_material.blend'));s=bpy.context.scene;s.camera=bpy.data.objects['SOURCE_15_exterior'];change=[]
 if case.startswith('H1'):
  ob=bpy.data.objects['DOOR_00_upper']
  for v in ob.data.vertices:
   if v.co.z<5.49:
    old=list(v.co);v.co.z+=1.2;change.append({'index':v.index,'before':old,'after':list(v.co)})
  ob.data.update();bpy.context.view_layer.update()
 s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=2
 # Diagnostic source-pixel ROI only: x550..800, y375..565. No source alignment/warping.
 s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=550/1192;s.render.border_max_x=800/1192;s.render.border_min_y=1-565/671;s.render.border_max_y=1-375/671
 f=O/(case+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);records.append({'hypothesis':case,'base_model_sha256':hashlib.sha256((P/'models/R09_material.blend').read_bytes()).hexdigest(),'changed_mesh':'DOOR_00_upper' if change else None,'changes':change,'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'scope':'In-memory diagnostic only; 1.2 arbitrary conditional opening extension, not inferred dimension; no saved model or source acceptance; lower original inner gold frame deliberately retained.'})
(O/'trial-records.json').write_text(json.dumps(records,indent=2))
