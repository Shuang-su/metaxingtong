import bpy,json,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/ferris_remake_R04_material.blend'));ds=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];names=[];topology={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 eo=o.evaluated_get(ds);me=eo.to_mesh();edges=Counter(tuple(sorted((a,b))) for p in me.polygons for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]]));topology[o.name]={'boundary_edges':sum(x==1 for x in edges.values()),'non2face_edges':sum(x!=2 for x in edges.values()),'zero_area_faces':sum(p.area<1e-12 for p in me.polygons),'same_direction_shared_edges':sum(v==2 for v in Counter((a,b) for p in me.polygons for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]])).values())}
 if o.get('qa_group')=='structure':
  n=len(vs);vs += [o.matrix_world@v.co for v in me.vertices];fs += [tuple(n+i for i in p.vertices) for p in me.polygons];names += [o.name]*len(me.polygons)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs);A=json.loads((R/'qa/apertures-R02.json').read_text());P=json.loads((R/'qa/parameters-R02.json').read_text())['footprint']
def inside(x,y):
 hit=False
 for a,b in zip(P,P[1:]+P[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit

def through_inner_loop(name,origin,d):
 o=bpy.data.objects.get(name)
 if o is None:return False
 vs=[o.matrix_world@v.co for v in o.data.vertices];n=len(vs)//4
 for loop in [vs[n:2*n],vs[3*n:4*n]]:
  aa=loop[0];bb=max(loop,key=lambda p:(p.xy-aa.xy).length);u=Vector((bb.x-aa.x,bb.y-aa.y,0)).normalized();normal=Vector((u.y,-u.x,0));den=d.dot(normal)
  if abs(den)<1e-10:return False
  t=(aa-origin).dot(normal)/den
  if t<0:return False
  q=origin+d*t;x=q.dot(u);y=q.z;poly=[(p.dot(u),p.z) for p in loop];hit=False
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  if not hit:return False
 return True

def aperture(face,p,d):
 if face==0 and abs(p.x)<.505 and .05<p.z<2.56:return True
 if face==4 and through_inner_loop('door_window_bezel_4',O,d):return True
 for a in A:
  if a['face']!=face or not a['id'].startswith('window_'):continue
  suffix=a['id'][7:]
  if through_inner_loop('cream_bezel_'+suffix,O,d) and through_inner_loop('black_gasket_'+suffix,O,d):return True
 return False
counts=Counter();fail=[];O=Vector((0,0,1.3))
for j in range(8192):
 z=1-2*(j+.5)/8192;a=j*math.pi*(3-math.sqrt(5));rr=math.sqrt(1-z*z);d=Vector((rr*math.cos(a),rr*math.sin(a),z));cand=[]
 for i in range(8):
  aa=Vector((*P[i],0));bb=Vector((*P[(i+1)%8],0));u=(bb-aa).normalized();n=Vector((u.y,-u.x,0));den=d.dot(n)
  if den>1e-10:
   t=(aa-O).dot(n)/den;p=O+d*t
   if t>0 and 0<=(p-aa).dot(u)<=(bb-aa).length and .05<=p.z<=2.59:cand.append((t,i,p))
 if abs(d.z)>1e-10:
  z=2.59 if d.z>0 else .05;t=(z-O.z)/d.z;p=O+d*t
  if inside(p.x,p.y):cand.append((t,'horizontal',p))
 if not cand:counts['unclassified']+=1;continue
 t,face,p=min(cand,key=lambda x:x[0]);q,_,_,_=tree.ray_cast(O,d,t+.22)
 if q is not None:counts['hit']+=1
 elif aperture(face,p,d):counts['allowed_miss']+=1
 else:counts['unexpected_miss']+=1;fail.append({'direction':list(d),'face':face,'shell_point':list(p)})
# Per-frame geometric interior-visible cream face test, not camera registration.
visibility=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('cream_bezel_'):continue
 face=int(o.name.split('_')[2]);a=Vector((*P[face],0));b=Vector((*P[(face+1)%8],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0));v=[o.matrix_world@x.co for x in o.data.vertices];N=len(v)//4;hit=Counter()
 for j in range(N):
  # interior-face ring samples, no pane-center tests
  p=(v[j]+v[N+j])*.5;ori=p-n*.20;q,_,idx,dist=tree.ray_cast(ori,n,.4);hit[names[idx] if idx is not None else 'NO_HIT']+=1
 visibility.append({'object':o.name,'36_inner_face_samples':dict(hit)})
(R/'qa/additional-audit-R04.json').write_text(json.dumps({'central8192':dict(counts),'fails':fail,'evaluated_mesh_topology':topology,'cream_visibility':visibility,'limits':['Single mesh closed edges not assembly acceptance','Finite ray set only; central aperture rays intersect BOTH actual inner-loop end planes of cream and gasket, not nominal wall-plane classification','Cream tests local construction visibility, not source-camera projected width','No exhaustive self-intersection or optical glazing validation']},indent=2));print(dict(counts))
# Signed-volume and winding diagnostics. Face closure alone cannot prove normal orientation.
import bmesh
volume=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);volume.append({'object':o.name,'signed_volume_local':bm.calc_volume(signed=True),'matrix_determinant':o.matrix_world.to_3x3().determinant()});bm.free()
f=R/'qa/additional-audit-R04.json';j=json.loads(f.read_text());j['signed_volumes']=volume;f.write_text(json.dumps(j,indent=2))
