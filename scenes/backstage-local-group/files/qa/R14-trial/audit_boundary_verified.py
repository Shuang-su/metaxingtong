import bpy,json,math,pathlib,sys,hashlib,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts')
from triangle_distance import triangle_triangle2,point_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-pearl-seating-trial-20261104');F=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105/models/R13_material.blend');sha=hashlib.sha256(F.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(F));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];pearls=[o.name for o in obs if o.name.startswith('NECKLACE_pearl_proxy_')];cache={}
def update():
 bpy.context.view_layer.update()
 for o in obs:
  o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];faces=[tuple(t.vertices) for t in o.data.loop_triangles];ts=[[v[i] for i in t] for t in faces];edges=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3));cache[o.name]={'v':v,'ts':ts,'bvh':BVHTree.FromPolygons(v,faces,all_triangles=True),'bounds':[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)],'closed':all(n==2 for n in edges.values())}
def broad(a,b):return all(cache[a]['bounds'][i][0]<=cache[b]['bounds'][i][1]+1e-7 and cache[b]['bounds'][i][0]<=cache[a]['bounds'][i][1]+1e-7 for i in range(3))
def distance(a,b):
 best=math.inf
 for x in cache[a]['ts']:
  lo=[min(p[i] for p in x) for i in range(3)];hi=[max(p[i] for p in x) for i in range(3)]
  for y in cache[b]['ts']:
   lb=sum(max(0,min(p[i] for p in y)-hi[i],lo[i]-max(p[i] for p in y))**2 for i in range(3))
   if lb>best:continue
   best=min(best,triangle_triangle2(x,y))
   if best<1e-20:return 0.
 return math.sqrt(best)
def winding(p,ts):
 total=0.
 for t in ts:
  a,b,c=[v-p for v in t];la,lb,lc=a.length,b.length,c.length
  total+=2*math.atan2(a.dot(b.cross(c)),la*lb*lc+a.dot(b)*lc+b.dot(c)*la+c.dot(a)*lb)
 return total/(4*math.pi)
def inside(a,b):
 vals=[];boundary=0
 for p in cache[a]['v']:
  near2=min(point_triangle2(p,*t) for t in cache[b]['ts'])
  if near2<=1e-14:boundary+=1;continue
  vals.append(winding(p,cache[b]['ts']))
 return {'strict_inside_vertex_count':sum(abs(w)>.5 for w in vals),'boundary_vertex_count':boundary,'max_abs_winding_off_boundary':max([abs(w) for w in vals],default=0)}
def run():
 update();out={'table_bounds':cache['TABLE_top']['bounds'],'pearls':{},'relations':[]}
 for n in pearls:
  out['pearls'][n]={'vertices':len(cache[n]['v']),'triangles':len(cache[n]['ts']),'closed_manifold_edges':cache[n]['closed'],'bounds':cache[n]['bounds'],'table_distance':distance(n,'TABLE_top'),'all_mesh_AABB_candidates':[m for m in cache if m!=n and broad(n,m)]}
 pairs=sorted({tuple(sorted((n,m))) for n in pearls for m in cache if n!=m and broad(n,m)})
 for a,b in pairs:
  r={'a':a,'b':b,'bvh_triangle_pairs':len(cache[a]['bvh'].overlap(cache[b]['bvh'])),'distance':distance(a,b),'a_in_b':inside(a,b),'b_in_a':inside(b,a),'both_closed':cache[a]['closed'] and cache[b]['closed']};out['relations'].append(r)
 return out
R={'source':str(F),'sha256_before':sha,'scope':'Actual saved mesh, finite table continuous triangle distance, full-scene AABB candidates, BVH surface overlaps and all-vertex winding containment with explicit boundary exclusion. Memory-only uniform Z trial; no saves. Model units only.','mesh_count':len(obs),'pearl_count':len(pearls)}
R['before']=run();dz=cache['TABLE_top']['bounds'][2][1]-min(cache[n]['bounds'][2][0] for n in pearls);R['trial_dz']=dz
before_other={o.name:[list(row) for row in o.matrix_world] for o in bpy.context.scene.objects if o.name not in pearls}
for n in pearls:bpy.data.objects[n].location.z+=dz
R['after']=run();R['other_objects_world_matrices_unchanged']=all([list(row) for row in bpy.data.objects[n].matrix_world]==mat for n,mat in before_other.items());R['sha256_after']=hashlib.sha256(F.read_bytes()).hexdigest();(P/'audit_boundary_verified.json').write_text(json.dumps(R,indent=2));print('DONE',dz,'relations',len(R['before']['relations']),len(R['after']['relations']),'unchanged',R['other_objects_world_matrices_unchanged'])
