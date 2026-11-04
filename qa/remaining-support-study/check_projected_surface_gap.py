import bpy,numpy as np,json,pathlib,hashlib
D=pathlib.Path(__file__).resolve().parent;p=D.parent/'forest-diagnostic-replay-20261104/models/R14_anchor-diagnostic_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
def tris(name):
 o=bpy.data.objects[name];o.data.calc_loop_triangles();v=np.array([list(o.matrix_world@x.co) for x in o.data.vertices]);return v[np.array([list(t.vertices) for t in o.data.loop_triangles])]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def clip(poly,tri):
 if cross(tri[1]-tri[0],tri[2]-tri[0])<0:tri=tri[::-1]
 for a,b in zip(tri,np.roll(tri,-1,axis=0)):
  out=[]
  if not len(poly):break
  s=poly[-1];ds=cross(b-a,s-a)
  for e in poly:
   de=cross(b-a,e-a)
   if (de>=-1e-12)!=(ds>=-1e-12):out.append(s+(e-s)*ds/(ds-de))
   if de>=-1e-12:out.append(e)
   s=e;ds=de
  poly=out
 return poly
T=tris('TERRAIN_finite_working_domain');T=T[np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0])[:,2]>1e-10];lo=T[:,:,:2].min(1);hi=T[:,:,:2].max(1);planes=[np.linalg.solve(np.column_stack([t[:,:2],np.ones(3)]),t[:,2]) for t in T];rows=[]
for name in ['TREE_main_buttress_02','LOG_left_fallen']:
 O=tris(name);best=(float('inf'),None);pairs=0;skip=0;negative=0
 for i,t in enumerate(O):
  area=cross(t[1,:2]-t[0,:2],t[2,:2]-t[0,:2])
  if abs(area)<1e-12:skip+=1;continue
  po=np.linalg.solve(np.column_stack([t[:,:2],np.ones(3)]),t[:,2]);a=t[:,:2].min(0);b=t[:,:2].max(0)
  for j in np.where(np.all(hi>=a,axis=1)&np.all(lo<=b,axis=1))[0]:
   poly=clip(list(t[:,:2]),T[j,:,:2])
   if not len(poly):continue
   pairs+=1
   for xy in poly:
    q=np.r_[xy,1];gap=float(q@(po-planes[j]));negative+=gap<0
    if gap<best[0]:best=(gap,{'object_triangle':i,'terrain_top_triangle':int(j),'xy':xy.tolist(),'object_z':float(q@po),'terrain_z':float(q@planes[j])})
 rows.append({'object':name,'triangles':len(O),'projected_near_degenerate_skipped':skip,'nonempty_projected_pairs':pairs,'minimum_vertical_gap':best[0],'minimum_witness':best[1],'negative_polygon_vertex_values':negative})
 print(name,best[0],'skipped',skip,flush=True)
(D/'projected-surface-gap.json').write_text(json.dumps({'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Float64 convex XY triangle clipping; affine surface-height difference extrema over every nonempty projected intersection polygon, using upward terrain triangles','numerical_limits':'1e-12 projected area/inside tolerance; vertical triangles skipped and counted; mesh triangulation not ideal continuous original smooth surface; finite terrain only; not source measurement','objects':rows},indent=2))
