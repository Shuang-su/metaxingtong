import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');f=P/'models/R08_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
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
legs=['CASE_handle_leg_-0.66','CASE_handle_leg_-0.24'];body='COSMETIC_case_body';bar='CASE_handle_bar'
R={'sha256_before':hashlib.sha256(f.read_bytes()).hexdigest(),'case_top_world':bounds(body)[2][1],'before':{},'after':{},'changes':{}}
def relationships(n):return {a:len(cache[n][1].overlap(cache[a][1]))for a in cache if a!=n and cache[n][1].overlap(cache[a][1])}
for n in legs:R['before'][n]={'bounds':bounds(n),'body':dist(n,body),'bar':dist(n,bar),'aabb_candidates':candidates(n),'surface_relationships':relationships(n)}
for n in legs:
 o=bpy.data.objects[n];old=[tuple(v.co)for v in o.data.vertices];world=[tuple(o.matrix_world@v.co)for v in o.data.vertices];bottom=min(v[2]for v in world);ids=[i for i,v in enumerate(world)if abs(v[2]-bottom)<1e-7];target=R['case_top_world']-.001
 for i in ids:
  w=Vector(world[i]);w.z=target;o.data.vertices[i].co=o.matrix_world.inverted()@w
 o.data.update();bpy.context.view_layer.update();update_cache(n)
 new=[tuple(o.matrix_world@v.co)for v in o.data.vertices];bm=bmesh.new();bm.from_mesh(o.data)
 R['changes'][n]={'root_indices':ids,'old_local_root':[old[i]for i in ids],'old_world_root':[world[i]for i in ids],'new_local_root':[tuple(o.data.vertices[i].co)for i in ids],'new_world_root':[new[i]for i in ids],'other_vertices_exact_unchanged':all(tuple(o.data.vertices[i].co)==old[i]for i in range(len(old))if i not in ids),'world_xy_max_error':max(abs(new[i][j]-world[i][j])for i in range(len(old))for j in [0,1]),'target_world_z':target,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(x.calc_area()<1e-12 for x in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free()
for n in legs:
 R['after'][n]={'bounds':bounds(n),'body':dist(n,body),'bar':dist(n,bar),'aabb_candidates':candidates(n),'surface_relationships':relationships(n)}
 R['after'][n]['added_surface_objects']=sorted(set(R['after'][n]['surface_relationships'])-set(R['before'][n]['surface_relationships']))
 R['after'][n]['removed_surface_objects']=sorted(set(R['before'][n]['surface_relationships'])-set(R['after'][n]['surface_relationships']))
R['sha256_after']=hashlib.sha256(f.read_bytes()).hexdigest();(Q/'R08-handle-memory-trial.json').write_text(json.dumps(R,indent=2));print(json.dumps(R,indent=2))
