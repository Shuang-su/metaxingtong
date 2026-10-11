import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'));S=bpy.context.scene;changes=[]
for o in S.objects:
 if o.type!='MESH':continue
 if o.name.startswith('INF_Ceiling_panel_bead'):
  changed=0
  for v in o.data.vertices:
   if v.co.y < -11.9:v.co.y=-11.9;changed+=1
   if v.co.y > 21.9:v.co.y=21.9;changed+=1
  if changed:changes.append({'object':o.name,'clipped_vertices':changed,'reason':'Keep inferred ceiling bead inside rear enclosure.'})
 if o.name.startswith('ARCH_Side_wall_'):
  for v in o.data.vertices:v.co.y=max(-12,min(22,v.co.y))
  changes.append({'object':o.name,'reason':'Butt walls at inner front/back planes; avoid duplicate coplanar exterior corner faces.'})
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'),compress=True)
json.dump(changes,open(R/'qa/envelope_seam_fixes.json','w'),indent=2);print(changes)
