import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).resolve().parent; R=O.parent/'seaside-arch-local-panel-study-20261105'; P=O.parent/'independent-seaside-r03-images-20261105/frozen/models/material.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.objects['SOURCE04 conditional'];moving=[bpy.data.objects[n] for n in ['W06 panel surround 03','W07 pink inset 03']]; meshes=[o for o in s.objects if o.type=='MESH'];base={o.name:o.matrix_world.copy() for o in s.objects};disk=bpy.data.objects['W08 lower circle 0'];origsha=hashlib.sha256(P.read_bytes()).hexdigest()
def bvh(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
def box(o):
 v=[o.matrix_world@v.co for v in o.data.vertices];return [(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
def pix(v):
 q=world_to_camera_view(s,c,v);assert q.z>0;return [q.x*1192,(1-q.y)*671]
def cross(o,y):
 vs=[pix(o.matrix_world@v.co) for v in o.data.vertices];xx=[]
 for e in o.data.edges:
  a,b=[vs[i] for i in e.vertices]
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(a[1]-b[1])>1e-8: xx.append(a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1]))
 return [min(xx),max(xx)] if xx else None
fixed={o.name:(box(o),bvh(o)) for o in meshes if o not in moving};db=box(disk);center=disk.matrix_world.translation;radius=(db[0][1]-db[0][0])/2
out={'model_sha256':origsha,'cases':[],'scope':'four discrete cases, not continuous safety domain; surface BVH does not rule out containment'}
for dx in [0,-.23,-.25,-.28]:
 for o in moving:
  m=base[o.name].copy();m.translation.x+=dx;o.matrix_world=m
 bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();changed=[o.name for o in s.objects if o.matrix_world!=base[o.name]]
 pairs=[]
 for o in moving:
  a=box(o);tree=bvh(o)
  for other in meshes:
   if o==other:continue
   b,t=fixed[other.name] if other not in moving else (box(other),bvh(other))
   if all(a[i][1]>=b[i][0] and b[i][1]>=a[i][0] for i in range(3)):pairs.append({'moving':o.name,'other':other.name,'surface_triangle_pairs':len(tree.overlap(t))})
 hits={}
 for rr in [0,.25,.5,.75,.9,.98,.995]:
  for j in range(720 if rr else 1):
   a=math.radians(j*.5);p=Vector((center.x+rr*radius*math.cos(a),db[1][0],center.z+rr*radius*math.sin(a)));d=p-c.matrix_world.translation
   hit,_,_,_,ob,_=s.ray_cast(dep,c.matrix_world.translation,d.normalized(),distance=d.length+.001);n=ob.name if hit else 'NO_HIT';hits[n]=hits.get(n,0)+1
 row={'dx':dx,'changed_objects':changed,'pairs':pairs,'hits':hits,'scanlines':{o.name:{str(y):cross(o,y) for y in [400,410,420,430,435]} for o in moving}}
 src=next(t for t in json.loads((R/'qa/sweep.json').read_text())['tests'] if t['shift_x']==dx)
 row['producer_hit_count_exact']=hits==src['circle_sample_first_hits']
 row['producer_surface_pairs_exact']=sorted((p['moving'],p['other'],p['surface_triangle_pairs']) for p in pairs)==sorted((p['moving'],p['other'],p['surface_triangle_pairs']) for p in src['pairs'])
 out['cases'].append(row)
out['file_unchanged']=hashlib.sha256(P.read_bytes()).hexdigest()==origsha
out['production_model_same_sha']=hashlib.sha256((O.parent/'seaside-arch-candidate-20261105/models/material.blend').read_bytes()).hexdigest()==origsha
(O/'check.json').write_text(json.dumps(out,indent=2));print('DONE',[(r['dx'],r['producer_hit_count_exact'],r['producer_surface_pairs_exact']) for r in out['cases']])
