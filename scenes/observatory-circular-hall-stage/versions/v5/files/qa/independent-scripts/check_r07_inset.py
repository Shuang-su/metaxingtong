import bpy,json,pathlib,math,hashlib
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104');f=P/'models/R07_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));o=bpy.data.objects['FLOOR_four_point_inlay'];p=[Vector((v.co.x,v.co.y)) for v in o.data.vertices];rs=[]
def cross(a,b):return a.x*b.y-a.y*b.x
for i in range(8):
 j=(i+1)%8;a,b=p[i],p[j];c,d=p[8+i],p[8+j];u=b-a;v=d-c;n=Vector((-u.y,u.x)).normalized();ts=[(x-a).dot(u)/u.length_squared for x in [c,d]]
 rs.append({'edge':i,'normalized_cross':cross(u.normalized(),v.normalized()),'direction_dot':u.normalized().dot(v.normalized()),'signed_line_distance_start':(c-a).dot(n),'signed_line_distance_end':(d-a).dot(n),'inner_endpoints_projection_on_outer_segment_t':ts,'outer_length':u.length,'inner_length':v.length})
(Q/'R07-inset-independent.json').write_text(json.dumps({'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'edges':rs,'scope':'Distances between infinite supporting lines; inner endpoints projected on outer finite segment reported. Does not prove source band constant-width, corner shape or solid-plane thickness.'},indent=2));print(rs)
