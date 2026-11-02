"""Normalize actual closed-solid face orientation only, preserve coordinates/cameras/materials."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];results=[]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/ferris_remake_R02_{mode}.blend'));changes=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  before=[tuple(v.co) for v in o.data.vertices];bm=bmesh.new();bm.from_mesh(o.data);old=bm.calc_volume(signed=True);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));new=bm.calc_volume(signed=True)
  if new<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));new=bm.calc_volume(signed=True)
  bm.to_mesh(o.data);bm.free();assert before==[tuple(v.co) for v in o.data.vertices];changes.append({'name':o.name,'signed_volume_before':old,'signed_volume_after':new,'coordinates_exact':True})
 bpy.context.scene['revision']='R03 normal-orientation correction, no coordinate change';bpy.ops.wm.save_as_mainfile(filepath=str(R/f'models/ferris_remake_R03_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(R/f'models/ferris_remake_R03_{mode}.glb'),export_format='GLB',export_apply=True);results.append({'mode':mode,'objects':changes})
(R/'qa/normal-correction-R03.json').write_text(json.dumps(results,indent=2));print('NORMAL_REPAIR_DONE')
