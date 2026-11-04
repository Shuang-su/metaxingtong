import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');f=P/'models/R09_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
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

R={}
for mode in ['material','white']:
 f=P/'models'/f'R09_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));cache={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':update_cache(o.name)
 R[mode]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'checks':{}}
 for n in ['CASE_handle_leg_-0.66','CASE_handle_leg_-0.24']:
  R[mode]['checks'][n]={'bounds':bounds(n),'body':dist(n,'COSMETIC_case_body'),'bar':dist(n,'CASE_handle_bar'),'aabb_candidates':candidates(n),'surface_relations':{a:len(cache[n][1].overlap(cache[a][1]))for a in cache if a!=n and cache[n][1].overlap(cache[a][1])}}
 R[mode]['case_table']=dist('COSMETIC_case_body','TABLE_top')
(Q/'R09-saved-contacts.json').write_text(json.dumps(R,indent=2))
