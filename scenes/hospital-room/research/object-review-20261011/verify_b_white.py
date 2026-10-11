import bpy,json,hashlib
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/candidate_b')
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));return {o.name:hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],list(map(list,o.matrix_world)))).encode()).hexdigest() for o in bpy.context.scene.objects if o.type=='MESH'}
a=read(r/'hospital_endboard_shape_B.blend');b=read(r/'hospital_endboard_shape_B_white.blend');q={'mesh_objects_material':len(a),'mesh_objects_white':len(b),'mesh_geometry_and_transform_equal':a==b};(r/'white_geometry_equality.json').write_text(json.dumps(q,indent=2))
