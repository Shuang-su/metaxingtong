import bpy,json,bmesh
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene/delivery/models/Garden_Complete_Textured.blend')
a=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 b=bmesh.new();b.from_mesh(o.data)
 a.append(dict(name=o.name,verts=len(b.verts),faces=len(b.faces),boundary=sum(e.is_boundary for e in b.edges),nonmanifold=sum(not e.is_manifold for e in b.edges),degenerate=sum(f.calc_area()<1e-10 for f in b.faces),lo=[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],hi=[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]));b.free()
json.dump(a,open('/workspace/scratch/fa58bfcf0425/castle_garden_fullscene/openings_geometry.json','w'),indent=2)
