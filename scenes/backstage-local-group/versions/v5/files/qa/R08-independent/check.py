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

targets=[n for n in cache if n.startswith(('COSMETIC_','CASE_','NECKLACE_','CLOCK_'))];r={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'surface_relationships':{},'table_distances':{},'aabb_candidates':{}}
bounds={n:[[min(p[i] for t in ts for p in t),max(p[i] for t in ts for p in t)]for i in range(3)]for n,(ts,bvh) in cache.items()}
for a in targets:
 r['surface_relationships'][a]={b:len(cache[a][1].overlap(cache[b][1])) for b in cache if b!=a and cache[a][1].overlap(cache[b][1])}
 r['table_distances'][a]=dist(a,'TABLE_top');x=bounds[a];r['aabb_candidates'][a]=[b for b,y in bounds.items() if b!=a and all(x[i][0]<=y[i][1]+1e-7 and y[i][0]<=x[i][1]+1e-7 for i in range(3))]
r['group_links']={}
for a in targets:
 if a.startswith('COSMETIC_bottle'):r['group_links'][a]=dist(a,a.replace('bottle','cap'))
for a,b in [('CLOCK_red_case_proxy','CLOCK_blank_face_unread_numbers'),('COSMETIC_case_body','CASE_handle_leg_-0.66'),('COSMETIC_case_body','CASE_handle_leg_-0.24'),('CASE_handle_bar','CASE_handle_leg_-0.66'),('CASE_handle_bar','CASE_handle_leg_-0.24')]:r['group_links'][a+' -> '+b]=dist(a,b)
(Q/'R06-tabletop.json').write_text(json.dumps(r,indent=2));print('DONE')
