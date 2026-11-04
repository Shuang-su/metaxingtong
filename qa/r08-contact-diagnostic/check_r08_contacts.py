import bpy,sys,pathlib,json,math,hashlib
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-ceiling-qa-20261105');f=P/'models/R08_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];cache={}
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
targets=[n for n in cache if n.startswith('SPOT_') or n in ['ONAIR_sign_back','ONAIR_text']];r={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'surface_intersections':{},'distances':{}}
for n in targets:r['surface_intersections'][n]={m:len(cache[n][1].overlap(v[1])) for m,v in cache.items() if m!=n and cache[n][1].overlap(v[1])}
for n in targets:
 if n.startswith('SPOT_rim_'):
  side=n.split('_')[2];diff=n.replace('rim','diffuser')
  for a,b in [(n,'SOFFIT_'+side),(diff,n),(diff,'SOFFIT_'+side)]:r['distances'][a+' -> '+b]=dist(a,b)
for a,b in [('ONAIR_sign_back','WALL_end_1_lintel'),('ONAIR_text','ONAIR_sign_back')]:r['distances'][a+' -> '+b]=dist(a,b)
(Q/'R08-spot-sign-contact.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
