import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-window-qa-20261104');f=P/'models/R09_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
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
R={}
for mode in ['material','white']:
 f=P/'models'/f'R09_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));cache={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':update_cache(o.name)
 out={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'frames':{}}
 for name in sorted(cache):
  if not name.startswith(('WINDOW_','EXTERIOR_WINDOW_')):continue
  k=int(name.split('_')[2 if name.startswith('EXTERIOR') else 1]);a=-math.pi/2+k*math.tau/16;n=Vector((math.cos(a),math.sin(a),0));wall=f'WALL_{k:02d}_perforated'
  def rb(o):
   vs=[n.dot(bpy.data.objects[o].matrix_world@v.co)for v in bpy.data.objects[o].data.vertices];return [min(vs),max(vs)]
  out['frames'][name]={'normal_range':rb(name),'wall_range':rb(wall),'wall_distance':dist(name,wall),'allscene_AABB_candidates':candidates(name),'surface_relations':{o:len(cache[name][1].overlap(cache[o][1]))for o in cache if o!=name and cache[name][1].overlap(cache[o][1])},'shared_with_inner':bpy.data.objects[name].data==bpy.data.objects[f'WINDOW_{k:02d}_gold_lip'].data}
 R[mode]=out
(Q/'R09-window-contacts.json').write_text(json.dumps(R,indent=2))
