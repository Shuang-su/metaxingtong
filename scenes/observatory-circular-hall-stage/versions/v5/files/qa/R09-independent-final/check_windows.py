import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-window-qa-20261104');f=P/'models/R08_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
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

from mathutils import Vector
R={'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'windows':{}}
for n in sorted(cache):
 if not n.startswith('WINDOW_'):continue
 k=int(n.split('_')[1]);wall=f'WALL_{k:02d}_perforated';a=-math.pi/2+k*math.tau/16;normal=Vector((math.cos(a),math.sin(a),0))
 def radial_bounds(name):
  ts,_=cache[name];r=[normal.dot(Vector(p))for t in ts for p in t];return [min(r),max(r)]
 rb,wb=radial_bounds(n),radial_bounds(wall);lower=wb[0]-rb[1];verts=[bpy.data.objects[n].matrix_world@v.co for v in bpy.data.objects[n].data.vertices];near=[]
 for i,v in enumerate(verts):
  x,no,ix,d=cache[wall][1].find_nearest(v)
  if x is not None:near.append((d,i,list(v),list(x),ix))
 upper=min(near);R['windows'][n]={'wall':wall,'normal':list(normal),'normal_coordinate_lip':rb,'normal_coordinate_wall':wb,'parallel_slab_distance_lower_bound':lower,'nearest_vertex_upper_bound':upper,'allscene_AABB_candidates':candidates(n),'allscene_surface_pairs':{b:len(cache[n][1].overlap(cache[b][1]))for b in cache if b!=n and cache[n][1].overlap(cache[b][1])},'bvh_wall_pairs':len(cache[n][1].overlap(cache[wall][1]))}
(Q/'R08-window-contact.json').write_text(json.dumps(R,indent=2));print([(n,v['parallel_slab_distance_lower_bound'],v['nearest_vertex_upper_bound'][0],v['allscene_AABB_candidates'])for n,v in R['windows'].items()])
