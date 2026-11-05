import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');f=P/'models/R06_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
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
for i in range(17):
 a=f'COSMETIC_bottle_proxy_{i}';b=f'COSMETIC_cap_proxy_{i}';ca=set(candidates(a))-{b};cb=set(candidates(b))-{a}
 if not ca and not cb:R['safe_indices'].append(i)
 else:R['rejected'][str(i)]={'body_other_AABB_candidates':sorted(ca),'cap_other_AABB_candidates':sorted(cb)}
top=bounds('TABLE_top')[2][1]
for i in R['safe_indices']:
 a=f'COSMETIC_bottle_proxy_{i}';b=f'COSMETIC_cap_proxy_{i}';bottom=bounds(a)[2][0];dz=top-.0003-bottom
 for n in [a,b]:bpy.data.objects[n].location.z+=dz
 bpy.context.view_layer.update()
 for n in [a,b]:update_cache(n)
 R['trials'][str(i)]={'delta_z':dz,'actual_body_table':dist(a,'TABLE_top'),'actual_body_cap':dist(a,b),'body_AABB_candidates':candidates(a),'cap_AABB_candidates':candidates(b),'relationships':{n:{other:len(cache[n][1].overlap(cache[other][1]))for other in cache if other!=n and cache[n][1].overlap(cache[other][1])}for n in [a,b]}}
R['sha256_after']=hashlib.sha256(f.read_bytes()).hexdigest();R['scope']='memory-only simultaneous safe subset Z translation; no file save, no XY changes; only exact original AABB-separated body+cap pairs included'
(Q/'safe-bottle-memory-trial.json').write_text(json.dumps(R,indent=2));print('safe',R['safe_indices']);print(R['trials'])
