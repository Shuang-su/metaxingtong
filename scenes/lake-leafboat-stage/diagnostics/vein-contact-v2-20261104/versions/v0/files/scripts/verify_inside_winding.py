import bpy,pathlib,json,hashlib,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];p=R/'models/leaf-only-contact-candidate-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
shell=bpy.data.objects['LEAF_001_ThinConcaveShell'];m=shell.data;m.calc_loop_triangles();vv=[shell.matrix_world@v.co for v in m.vertices];ii=[tuple(t.vertices) for t in m.loop_triangles];tree=BVHTree.FromPolygons(vv,ii,all_triangles=True)
tri=np.asarray([[tuple(vv[j]) for j in t] for t in ii],dtype=np.float64)
old=json.loads((R/'qa/embedded-ring-five-ray-parity.json').read_text());rows=[]
def winding(point):
 u=tri-np.asarray(point,dtype=np.float64);a,b,c=u[:,0],u[:,1],u[:,2];al,bl,cl=[np.linalg.norm(x,axis=1) for x in (a,b,c)]
 numerator=np.einsum('ij,ij->i',a,np.cross(b,c));denominator=al*bl*cl+np.einsum('ij,ij->i',a,b)*cl+np.einsum('ij,ij->i',b,c)*al+np.einsum('ij,ij->i',c,a)*bl
 return float(np.sum(2*np.arctan2(numerator,denominator))/(4*math.pi))
def ray(point,d,step):
 hits=[];c=Vector(point)
 for _ in range(32):
  h,n,idx,distance=tree.ray_cast(c,d,20)
  if h is None:break
  hits.append(dict(point=list(h),triangle=idx,distance_from_cursor=distance));c=h+d*step
 else:raise AssertionError('Ray limit')
 return dict(count=len(hits),inside=len(hits)%2==1,hits=hits)
for r in old['rows']:
 w=winding(r['point']);ds=[ray(r['point'],Vector(d),1e-5) for d in old['directions']]
 rows.append(dict(name=r['name'],ring=r['ring'],point=r['point'],generalized_winding_number=w,winding_inside=abs(abs(w)-1)<1e-6,parity_step_1e_5=ds,all_five_parities_inside=all(x['inside'] for x in ds)))
rechecks=[]
for r in old['rows']:
 if not r['all_inside']:
  rechecks.append(dict(name=r['name'],ring=r['ring'],step_1e_6=ray(r['point'],Vector(old['directions'][3]),1e-6),step_1e_5=ray(r['point'],Vector(old['directions'][3]),1e-5)))
out=dict(candidate_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),method='Independent float64 oriented triangle solid-angle sum over all 83648 shell triangles for every sampled embedded-ring minimum point, plus all five BVH parity rays at 1e-5 advance. Original failed 1e-6 advance results retained. No geometry changed.',scope='451 sampled ring minima, not every point in the tubes or a source-fit test.',rows=rows,small_step_failures_rechecked=rechecks,all_winding_inside=all(r['winding_inside'] for r in rows),all_parities_inside=all(r['all_five_parities_inside'] for r in rows))
(R/'qa/embedded-ring-winding-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('winding_inside',sum(r['winding_inside'] for r in rows),'parity_inside',sum(r['all_five_parities_inside'] for r in rows),flush=True)
assert out['all_winding_inside'] and out['all_parities_inside']
