import bpy,bmesh,json,hashlib
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/candidate_b')
def read(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));ret={};bed={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  verts=[tuple(round(c,6) for c in o.matrix_world@v.co) for v in o.data.vertices];tris=sorted(tuple(sorted(verts[i] for i in f.vertices)) for f in o.data.polygons);ret[o.name]=hashlib.sha256(repr(tris).encode()).hexdigest()
  if 'observed endboard' in o.name:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bed={'nonmanifold_after_same_position_weld':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free()
 return ret,bed
m,mb=read(r/'hospital_endboard_shape_B.glb');w,wb=read(r/'hospital_endboard_shape_B_white.glb');q={'material_mesh_count':len(m),'white_mesh_count':len(w),'all_world_triangles_equal_rounded_1e-6':m==w,'different':[k for k in m if m.get(k)!=w.get(k)],'material_board':mb,'white_board':wb};(r/'white_glb_roundtrip_geometry_equality.json').write_text(json.dumps(q,indent=2))
