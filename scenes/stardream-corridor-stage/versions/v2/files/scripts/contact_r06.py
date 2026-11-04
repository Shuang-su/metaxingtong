import bpy,json,pathlib,hashlib
P=pathlib.Path(__file__).resolve().parents[1];records={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R05_{mode}.blend'));changes={}
 for side in [-1,1]:
  for j in range(4):
   o=bpy.data.objects[f'LANTERN_{side}_{j}_wall_plate'];rows=[]
   # Plate local +Z is world +X on both sides. Extend only wall-facing cap, front/rod-facing cap unchanged.
   for v in o.data.vertices:
    if v.co.z*side>0:
     old=list(v.co);v.co.z+=side*.015;rows.append({'index':v.index,'old':old,'new':list(v.co)})
   o.data.update();changes[o.name]=rows;o['contact_note']='Wall-facing cap extended.015 arbitrary units into wall; not actual measured plate thickness or structural strength'
 for end in [-1,1]:
  o=bpy.data.objects[f'DOOR_handle_{end}'];rows=[]
  # Local -Z is original start/root for both rods; only extend root .045, visible end unchanged.
  for v in o.data.vertices:
   if v.co.z<0:
    old=list(v.co);v.co.z-=.045;rows.append({'index':v.index,'old':old,'new':list(v.co)})
  o.data.update();changes[o.name]=rows;o['contact_note']='Root extended.045 into inferred door leaf; no measured door fitting or strength claimed'
 bpy.context.view_layer.update();f=P/'models'/f'R06_{mode}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R06_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);records[mode]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'changed_objects':changes,'limitations':'Intentional surface overlap, not Boolean welded assembly or source acceptance. No bracket/rib/roof changes, existing contact chain retained.'}
(P/'qa/R06-applied-contact.json').write_text(json.dumps(records,indent=2))
