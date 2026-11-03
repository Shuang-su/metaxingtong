import bpy,bmesh,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
records=[]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R01_{mode}.blend'))
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);oldv=len(bm.verts);oldf=len(bm.faces)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
  # Curves export cap vertices separately. Weld only coincident vertices, keep original geometry.
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  records.append({'mode':mode,'object':o.name,'old_vertices':oldv,'new_vertices':len(bm.verts),'old_faces':oldf,'new_faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)})
  bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R02_{mode}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(D/f'models/R02_{mode}.glb'),export_format='GLB',export_apply=True)
(D/'qa/R02-repair-record.json').write_text(json.dumps({'changes':'Weld coincident cap/end vertices; dissolve degenerate edges; outward normals. No intentional source geometry/camera/material changes.','objects':records},indent=2))
