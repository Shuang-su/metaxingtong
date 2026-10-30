"""Read-only finite-shell audit; no bpy save operations. Polygon apertures from mesh inner loops."""
import bpy,json,math,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
POLY=[(-1.12,-1.85),(1.12,-1.85),(1.62,-1.35),(1.62,1.35),(1.12,1.85),(-1.12,1.85),(-1.62,1.35),(-1.62,-1.35)]
def inside(p,poly):
 x,y=p;hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit

def audit(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));ds=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[];rings={}
 prefixes=('floor_slab','ceiling_slab','pillar_','sill_','head_','jamb_','cream_bezel_','black_gasket_','door_')
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith(prefixes):continue
  if o.name.startswith(('cream_bezel_','black_gasket_','door_window_bezel_')):
   # ring() builds 4 equally-sized loops: outer-back, inner-back, outer-front, inner-front.
   n=len(o.data.vertices)//4
   rings[o.name]=[o.matrix_world@v.co for v in o.data.vertices[n:2*n]]
  ob=o.evaluated_get(ds);me=ob.to_mesh();off=len(verts);verts += [o.matrix_world@v.co for v in me.vertices];faces += [tuple(off+i for i in p.vertices) for p in me.polygons];names += [o.name]*len(me.polygons);ob.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,faces)
 def through_ring(name,origin,d):
  ps=rings.get(name)
  if not ps:return False
  # ring plane normal, tangent from horizontal farthest pair avoids rounded-corner assumptions
  low=min(ps,key=lambda v:v.z);high=max(ps,key=lambda v:v.z)
  pairs=max(((a,b) for a in ps for b in ps),key=lambda ab:(ab[1].xy-ab[0].xy).length)
  u=Vector((pairs[1].x-pairs[0].x,pairs[1].y-pairs[0].y,0)).normalized();n=Vector((u.y,-u.x,0));den=d.dot(n)
  if abs(den)<1e-10:return False
  t=(ps[0]-origin).dot(n)/den
  if t<0:return False
  p=origin+d*t
  return inside((p.dot(u),p.z),[(v.dot(u),v.z) for v in ps])
 def allowed(face,p,origin,d):
  if face==0 and abs(p.x)<.505 and .05<p.z<2.49:return 'fixed_front_entry'
  if face==4 and through_ring('door_window_bezel_4',origin,d):return 'rear_door_window'
  if isinstance(face,int):
   for name in rings:
    if name.startswith('cream_bezel_'+str(face)+'_'):
     suffix=name.removeprefix('cream_bezel_')
     if through_ring(name,origin,d) and through_ring('black_gasket_'+suffix,origin,d):return 'window_'+suffix
  return None
 counts=Counter();fail=[];hitobjects=Counter();ap=Counter()
 def probe(face,p,origin,d,maxdist,kind):
  aperture=allowed(face,p,origin,d);q,n,idx,dist=tree.ray_cast(origin,d,maxdist)
  counts[kind+'_total']+=1
  if q is not None:counts[kind+'_hit']+=1;hitobjects[names[idx]]+=1
  elif aperture:counts[kind+'_allowed_nohit']+=1;ap[aperture]+=1
  else:
   counts[kind+'_unexpected_nohit']+=1;fail.append({'kind':kind,'face':face,'shell_point':list(p),'origin':list(origin),'direction':list(d)})
 # Uniform surface probes, local inward origin: avoids seats/interior blocking thin shell gaps.
 for i in range(8):
  a=Vector((*POLY[i],0));b=Vector((*POLY[(i+1)%8],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0))
  for j in range(100):
   for k in range(120):
    p=a+(b-a)*((j+.5)/100)+Vector((0,0,.05+2.54*(k+.5)/120));probe(i,p,p-n*.22,n,.44,'surface')
 # Closed horizontal slab probes, excluding polygon exterior.
 for face,z,sgn in [('floor',.05,-1),('ceiling',2.59,1)]:
  for j in range(100):
   for k in range(100):
    x=-1.62+3.24*(j+.5)/100;y=-1.85+3.7*(k+.5)/100
    if inside((x,y),POLY):
     p=Vector((x,y,z));n=Vector((0,0,sgn));probe(face,p,p-n*.2,n,.4,'surface')
 # Isotropic central rays, classify using first intersection with finite nominal shell.
 origin=Vector((0,0,1.3))
 for j in range(8192):
  z=1-2*(j+.5)/8192;ang=j*math.pi*(3-math.sqrt(5));r=math.sqrt(1-z*z);d=Vector((r*math.cos(ang),r*math.sin(ang),z));candidates=[]
  for i in range(8):
   a=Vector((*POLY[i],0));b=Vector((*POLY[(i+1)%8],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0));den=d.dot(n)
   if den>1e-10:
    t=(a-origin).dot(n)/den;p=origin+d*t
    if t>0 and 0<=(p-a).dot(u)<=(b-a).length and .05<=p.z<=2.59:candidates.append((t,i,p))
  if abs(d.z)>1e-10:
   zz=2.59 if d.z>0 else .05;t=(zz-origin.z)/d.z;p=origin+d*t
   if inside((p.x,p.y),POLY):candidates.append((t,'ceiling' if d.z>0 else 'floor',p))
  if not candidates:counts['unclassified_direction']+=1;continue
  t,face,p=min(candidates,key=lambda a:a[0]);probe(face,p,origin,d,t+.22,'central')
 return {'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'counts':dict(counts),'unexpected_by_face':dict(Counter(str(x['face']) for x in fail)),'allowed_nohit_by_aperture':dict(ap),'unexpected_nohit':fail,'hit_object_counts':dict(hitobjects),'aperture_ring_names':sorted(rings),'status':'unexpected_leaks_detected' if fail else 'no_leaks_on_sampled_rays_only'}
report={'method':'Actual mesh inner polygon projection for both bezel and gasket. Rear door only its window. Front entry fixed x(-.505,.505),z(.05,2.49). All other wall/doorframe domains require structural hit. Surface probes remove furniture masking; central rays use first nominal finite shell intersection.','limitations':['Finite sampling, not watertight topology proof; sub-grid defects can be missed.','Nominal shell footprint/z bounds taken from build script; scene-source geometry not verified.','Rounded ring loop order assumes current ring generator; report ring names to permit review.','Structural hits anywhere within 0.22 model units of nominal shell count, so surface cracks covered by separate trim may count closed.','Open front doorway intentionally allowed; open door leaf fidelity not proved.','No absolute scale, source acceptance, self-intersection, material or optical-glass validation.'],'results':[]}
for name in ['ferris_cabin_material.blend','ferris_cabin_r06_material.blend']:
 p=R/'models'/name
 if p.exists():report['results'].append(audit(p))
 else:report['results'].append({'file':str(p),'status':'missing_not_tested'})
out=R/'qa/strict-aperture-audit.json';out.write_text(json.dumps(report,indent=2));print(json.dumps([{k:v for k,v in r.items() if k in ['file','counts','unexpected_by_face','status']} for r in report['results']],indent=2))
