import bpy,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'deliverables/01_train_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
for o in bpy.data.objects:
 if o.type=='MESH' and 'profiled end wall' in o.name:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=bm.edges,dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);print('END_WALL_EDGES_CLEANED',flush=True)
