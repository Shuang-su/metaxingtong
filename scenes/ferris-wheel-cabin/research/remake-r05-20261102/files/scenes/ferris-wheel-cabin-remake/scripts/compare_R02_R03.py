import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def snap(stage):
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/ferris_remake_{stage}_material.blend'));items={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':items[o.name]=hashlib.sha256(b''.join(struct.pack('<3d',*(o.matrix_world@v.co)) for v in o.data.vertices)).hexdigest()
 cams={o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in bpy.context.scene.objects if o.type=='CAMERA'}
 return {'world_vertex_sha256':items,'cameras':cams}
a=snap('R02');b=snap('R03');assert a==b
old=json.loads((R/'qa/additional-audit-R02.json').read_text());O=Vector((0,0,1.3));details=[]
for ray in old['fails']:
 d=Vector(ray['direction']);candidates=[]
 for ob in bpy.context.scene.objects:
  if not (ob.name.startswith(('cream_bezel_','black_gasket_','door_window_bezel_'))):continue
  face=int(ob.name.split('_')[2]) if not ob.name.startswith('door_window') else int(ob.name.split('_')[-1])
  if face!=ray['face']:continue
  vv=[ob.matrix_world@v.co for v in ob.data.vertices];n=len(vv)//4;planes=[]
  for label,loop in [('inner_back',vv[n:2*n]),('inner_front',vv[3*n:4*n])]:
   aa=loop[0];bb=max(loop,key=lambda p:(p.xy-aa.xy).length);u=Vector((bb.x-aa.x,bb.y-aa.y,0)).normalized();normal=Vector((u.y,-u.x,0));den=d.dot(normal)
   if abs(den)<1e-10:continue
   t=(aa-O).dot(normal)/den;p=O+d*t;x=p.dot(u);z=p.z;poly=[(v.dot(u),v.z) for v in loop];hit=False
   for c,e in zip(poly,poly[1:]+poly[:1]):
    if (c[1]>z)!=(e[1]>z) and x<(e[0]-c[0])*(z-c[1])/(e[1]-c[1])+c[0]:hit=not hit
   planes.append({'side':label,'world_intersection':list(p),'ray_t':t,'inside_actual_inner_polygon':hit,'polygon_world':[list(v) for v in loop]})
  candidates.append({'object':ob.name,'planes':planes})
 details.append({'old_classification':'unexpected_miss_using_nominal_wall_point','old_ray':ray,'actual_aperture_intersections':candidates})
(R/'qa/R02-R03-worldvertex-and-ray-classification.json').write_text(json.dumps({'world_vertex_and_camera_exact':True,'snapshot':a,'nine_old_misses':details,'correction':'Same rays/geometry; test intersection with actual inner-loop planes. No aperture moved/expanded and no epsilon enlargement.'},indent=2));print('EXACT_WORLD_VERTEX_CAMERAS',len(a['world_vertex_sha256']))
