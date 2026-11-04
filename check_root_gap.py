import bpy,pathlib,json,hashlib,sys,math,numpy as np
from mathutils.bvhtree import BVHTree
D=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(D));from triangle_distance import triangle_triangle2,tests
p=D.parent/'forest-diagnostic-replay-20261104/models/R15_log-contact-diagnostic_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
def data(name):
 o=bpy.data.objects[name];o.data.calc_loop_triangles();v=np.array([list(o.matrix_world@x.co) for x in o.data.vertices]);return v,v[np.array([list(t.vertices) for t in o.data.loop_triangles])]
v,B=data('TREE_main_trunk');lo=B.min(1);hi=B.max(1);rows=[]
for i in range(8):
 name='TREE_main_buttress_%02d'%i;v,A=data(name);best=float('inf');pair=None;tested=0
 # First finite upper bound, then safe AABB Euclidean lower-bound pruning.
 best=triangle_triangle2(A[0].tolist(),B[0].tolist())
 for ai,a in enumerate(A):
  delta=np.maximum(np.maximum(lo-a.max(0),a.min(0)-hi),0);bound=np.sum(delta*delta,axis=1)
  for bi in np.argsort(bound):
   if bound[bi]>best+1e-15:break
   d=triangle_triangle2(a.tolist(),B[bi].tolist());tested+=1
   if d<best:best=d;pair=[ai,int(bi)]
   if best==0:break
  if best==0:break
 rows.append({'object':name,'main_trunk_min_surface_distance':math.sqrt(best),'triangle_pair':pair,'tested_pairs':tested,'object_triangles':len(A),'trunk_triangles':len(B),'early_exit_on_exact_zero':best==0});print(rows[-1],flush=True)
(D/'buttress-main-trunk-distance.json').write_text(json.dumps({'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'triangle feature/edge-face Euclidean minimum; AABB squared lower-bound pruning; float64; no model changes','unit_tests':tests(),'limitations':['Numerical surface distance, not observed/source distance','Zero surface intersection not Boolean union, stable load path or full collision acceptance','Containment without surface intersection requires separate classification'],'results':rows},indent=2))
