import bpy,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
results=[]
for kind in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/arcade_remake_R01_{kind}.blend'));changed=[]
 for o in list(bpy.context.scene.objects):
  if '_LOW_ring_' not in o.name:continue
  poly=[v.co.copy()for v in o.data.vertices];out=[];z=.167
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=a.z>=z;ib=b.z>=z
   if ia:out.append(a)
   if ia!=ib:out.append(a+(b-a)*((z-a.z)/(b.z-a.z)))
  if len(out)==len(poly) and all((a-b).length<1e-8 for a,b in zip(out,poly)):continue
  changed.append(o.name)
  if len(out)<3:bpy.data.objects.remove(o,do_unlink=True)
  else:
   mats=list(o.data.materials);me=bpy.data.meshes.new(o.name+'_clipped');me.from_pydata(out,[],[list(range(len(out)))]);me.update();o.data=me
   for m in mats:me.materials.append(m)
 bpy.context.scene['status']='R02 clipped lower print to red panel; source camera and proportions FAIL'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/arcade_remake_R02_{kind}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/arcade_remake_R02_{kind}.glb'),export_format='GLB',export_cameras=True,export_lights=True);results.append({'kind':kind,'changed_print_segments':changed})
(D/'qa/R02_clip.json').write_text(json.dumps(results,indent=2))
