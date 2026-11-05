import bpy,json,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
from mathutils.bvhtree import BVHTree
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(P/'models/R03_material.blend'))
def data(n):
 o=bpy.data.objects[n];d=o.data;d.calc_loop_triangles();v=[o.matrix_world@x.co for x in d.vertices];t=[tuple(x.vertices)for x in d.loop_triangles];return np.array([[tuple(v[i])for i in q]for q in t]),BVHTree.FromPolygons(v,t,all_triangles=True),v
out=[]
for label in ['UPPER','LOWER']:
 for vn in [f'VEIN_L_{label}_outer_boundary']:
  sn=f'WING_L_{label}_finite_outer_shell';a,ta,va=data(vn);b,tb,vb=data(sn);over=len(ta.overlap(tb));best=min([tb.find_nearest(v)[3]**2 for v in va]+[ta.find_nearest(v)[3]**2 for v in vb]);calls=0
  lo=b.min(axis=1);hi=b.max(axis=1)
  for tri in a:
   delta=np.maximum(0,np.maximum(lo-tri.max(axis=0),tri.min(axis=0)-hi));ids=np.where((delta*delta).sum(axis=1)<=best+1e-20)[0]
   for j in ids:best=min(best,triangle_triangle2(tri.tolist(),b[j].tolist()));calls+=1
  out.append({'vein':vn,'shell':sn,'surface_distance':math.sqrt(best),'bvh_overlap_pairs':over,'exact_feature_candidate_calls':calls,'scope':'continuous triangle surface distance; no mechanical support claim; zero does not quantify overlap volume'})
(O/'contact-distances.json').write_text(json.dumps(out,indent=2));print(out)
