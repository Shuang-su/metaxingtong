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

import bmesh
from mathutils import Vector
n='COSMETIC_case_body';o=bpy.data.objects[n]
def state():
 bm=bmesh.new();bm.from_mesh(o.data);r={'bounds':bounds(n),'table':dist(n,'TABLE_top'),'aabb_candidates':candidates(n),'surface_relations':{a:len(cache[n][1].overlap(cache[a][1]))for a in cache if a!=n and cache[n][1].overlap(cache[a][1])},'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'volume':bm.calc_volume(signed=True)};bm.free();return r
R={'model_sha_before':hashlib.sha256(f.read_bytes()).hexdigest(),'before':state()};before={x.name:([tuple(v.co)for v in x.data.vertices],[tuple(p.vertices)for p in x.data.polygons],[[tuple(d.uv)for d in l.data]for l in x.data.uv_layers])for x in bpy.context.scene.objects if x.type=='MESH'};bottom=bounds(n)[2][0];top=bounds('TABLE_top')[2][1];changes=[]
for v in o.data.vertices:
 w=o.matrix_world@v.co
 if abs(w.z-bottom)<1e-7:
  old=list(v.co);oldw=list(w);w.z=top-.0003;v.co=o.matrix_world.inverted()@w;changes.append({'index':v.index,'old_local':old,'new_local':list(v.co),'old_world':oldw,'new_world':list(o.matrix_world@v.co)})
o.data.update();bpy.context.view_layer.update();update_cache(n);R['changes']=changes;R['after']=state();after={x.name:([tuple(v.co)for v in x.data.vertices],[tuple(p.vertices)for p in x.data.polygons],[[tuple(d.uv)for d in l.data]for l in x.data.uv_layers])for x in bpy.context.scene.objects if x.type=='MESH'};R['changed_mesh']=[x for x in before if before[x]!=after[x]];R['faces_uv_unchanged']=before[n][1:]==after[n][1:];R['added_surface_objects']=sorted(set(R['after']['surface_relations'])-set(R['before']['surface_relations']));R['removed_surface_objects']=sorted(set(R['before']['surface_relations'])-set(R['after']['surface_relations']));R['model_sha_after']=hashlib.sha256(f.read_bytes()).hexdigest();(Q/'R09-case-bottom-memory-trial.json').write_text(json.dumps(R,indent=2));print(json.dumps(R))
