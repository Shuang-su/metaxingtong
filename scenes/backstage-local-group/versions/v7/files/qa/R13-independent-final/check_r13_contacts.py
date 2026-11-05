import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-layout-qa-20261104');f=P/'models/R13_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
for o in obs:
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];fi=[tuple(t.vertices) for t in o.data.loop_triangles];ts=[[tuple(v[i]) for i in t] for t in fi];cache[o.name]=(ts,BVHTree.FromPolygons(v,fi,all_triangles=True))
def dist(a,b):
 ts,t=cache[a];us,u=cache[b];pairs=t.overlap(u)
 best=math.inf
 for x in ts:
  xl=[min(p[i] for p in x) for i in range(3)];xh=[max(p[i] for p in x) for i in range(3)]
  for y in us:
   lo=sum(max(0,min(p[i] for p in y)-xh[i],xl[i]-max(p[i] for p in y))**2 for i in range(3))
   if lo>best:continue
   best=min(best,triangle_triangle2(x,y))
   if best==0:return {'distance':0.,'bvh_face_pairs':len(pairs)}
 return {'distance':math.sqrt(best),'bvh_face_pairs':len(pairs)}

def update_cache(n):
 o=bpy.data.objects[n];o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];fi=[tuple(t.vertices)for t in o.data.loop_triangles];cache[n]=([[tuple(v[i])for i in t]for t in fi],BVHTree.FromPolygons(v,fi,all_triangles=True))
def bounds(n):
 ts,_=cache[n];return [[min(p[i]for t in ts for p in t),max(p[i]for t in ts for p in t)]for i in range(3)]
def candidates(n):
 x=bounds(n);return [b for b in cache if b!=n and all(x[i][0]<=bounds(b)[i][1]+1e-7 and bounds(b)[i][0]<=x[i][1]+1e-7 for i in range(3))]
R={'sha256_before':hashlib.sha256(f.read_bytes()).hexdigest(),'safe_indices':[],'rejected':{},'trials':{}}
R['safe_indices']=[3,4,5,6,7,8]
top=bounds('TABLE_top')[2][1]
# Re-evaluate all six after all translations have completed.
R['final_simultaneous']={}
for i in R['safe_indices']:
 a=f'COSMETIC_bottle_proxy_{i}';b=f'COSMETIC_cap_proxy_{i}'
 R['final_simultaneous'][str(i)]={'body_table':dist(a,'TABLE_top'),'body_cap':dist(a,b),'body_AABB_candidates':candidates(a),'cap_AABB_candidates':candidates(b),'surface_relations':{n:{o:len(cache[n][1].overlap(cache[o][1])) for o in cache if o!=n and cache[n][1].overlap(cache[o][1])}for n in [a,b]}}
# Only unrelated remaining AABB overlap is bottle 4 / 5; independently check closed-solid containment using all vertices' solid-angle winding.
from mathutils import Vector
def winding(p,ts):
 total=0.
 for tri in ts:
  a,b,c=[Vector(v)-Vector(p)for v in tri];la,lb,lc=a.length,b.length,c.length
  num=a.dot(b.cross(c));den=la*lb*lc+a.dot(b)*lc+b.dot(c)*la+c.dot(a)*lb
  total+=2*math.atan2(num,den)
 return total/(4*math.pi)
a='COSMETIC_bottle_proxy_4';b='COSMETIC_bottle_proxy_5'
R['bottle4_5']={'continuous_triangle_distance':dist(a,b),'vertex_winding_in_other':{n:[winding(p,cache[o][0])for p in sorted(set(v for t in cache[n][0]for v in t))]for n,o in [(a,b),(b,a)]},'scope':'Closed connected bottle solids; positive continuous surface distance plus all vertices outside excludes one fully contained in the other.'}
R['all17_body_table']={str(i):dist(f'COSMETIC_bottle_proxy_{i}','TABLE_top')for i in range(17)}
R['sha256_after']=hashlib.sha256(f.read_bytes()).hexdigest();R['scope']='Read-only actual saved R13 material; no translation applied. Six selected pairs and all seventeen bodies against finite table; no model save/render.'
(Q/'R13-saved-contact-check.json').write_text(json.dumps(R,indent=2));print('safe',R['safe_indices']);print(R['trials'])
