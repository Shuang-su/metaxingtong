import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).parent;R=O.parent/'dreamfold-phone-study-20261104';D=O.parent/'dreamfold-phone-v04-diagnosis-20261104';p=R/'versions/V03/models/phone-material.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;cam=s.camera;o=s.objects['P04_rear_leaf_unseen_geometry_INFERRED'];old=o.matrix_world.copy();f=json.load(open(R/'qa/camera-fit.json'));T=Matrix(f['rotation']).to_4x4();T.translation=Vector(f['translation']);out={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':[]};prod=json.load(open(D/'scan.json'))['scan']
def meshes():
 dg=bpy.context.evaluated_depsgraph_get();d={}
 for ob in s.objects:
  if ob.type!='MESH':continue
  e=ob.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();d[ob.name]=([ob.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles]);e.to_mesh_clear()
 return d
def winding(vs,fs,p):
 total=0.
 for f in fs:
  a,b,c=(vs[i]-p for i in f);la,lb,lc=a.length,b.length,c.length
  total+=2*math.atan2(a.dot(b.cross(c)),la*lb*lc+a.dot(b)*lc+b.dot(c)*la+c.dot(a)*lb)
 return total/(4*math.pi)
original=meshes();other={x.name:[list(r) for r in x.matrix_world] for x in s.objects if x!=o}
for angle in [25,30,35,40,45,50,55]:
 A=Matrix.Rotation(math.radians(angle),4,'X');A.translation=Vector((0,.6,-.025))+A.to_3x3()@Vector((0,-.6,0));o.matrix_world=T@A;bpy.context.view_layer.update();d=meshes();v,fs=d[o.name];ps=[world_to_camera_view(s,cam,x) for x in v];pts=[(q.x*1080,(1-q.y)*603) for q in ps];rows=[];fr=cam.data.view_frame(scene=s);x0,x1=min(q.x for q in fr),max(q.x for q in fr);y0,y1=min(q.y for q in fr),max(q.y for q in fr)
 for y in range(375,466):
  xs=[]
  for tri in fs:
   for a,b in zip(tri,tri[1:]+tri[:1]):
    aa,bb=pts[a],pts[b]
    if min(aa[1],bb[1])<=y<=max(aa[1],bb[1]) and abs(aa[1]-bb[1])>1e-10:xs.append(aa[0]+(y-aa[1])*(bb[0]-aa[0])/(bb[1]-aa[1]))
  x=max(xs);local=Vector((x0+(x-.75)/1080*(x1-x0),y1-y/603*(y1-y0),fr[0].z));direction=cam.matrix_world.to_3x3()@local;hit=s.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.matrix_world.translation,direction.normalized());sx=901+(y-375)*9/50 if y<=425 else 910+(y-425)*7/40;rows.append({'y':y,'x':x,'residual':x-sx,'first':hit[4].name if hit[0] else None})
 bv={n:BVHTree.FromPolygons(v,f,all_triangles=True) for n,(v,f) in d.items()};contacts=[]
 for n,(v2,f2) in d.items():
  if n==o.name:continue
  sep=max(max(min(x[k] for x in v2)-max(x[k] for x in v),min(x[k] for x in v)-max(x[k] for x in v2)) for k in range(3));cnt=len(bv[o.name].overlap(bv[n])); contained=None
  if sep<=0 and cnt==0:contained={'other_vertex_max_abs_winding_in_rear':max(abs(winding(v,fs,p)) for p in v2),'rear_vertex_max_abs_winding_in_other':max(abs(winding(v2,f2,p)) for p in v)}
  contacts.append({'containment_vertex_probe':contained,'object':n,'aabb_signed_separation':sep,'triangle_pairs':len(bv[o.name].overlap(bv[n])),'containment_excluded_by_aabb':sep>0})
 pr=next(x for x in prod if x['angle_degrees']==angle)
 out['rows'].append({'angle':angle,'original25_matrix_max_error':max(abs(old[i][j]-o.matrix_world[i][j]) for i in range(4) for j in range(4)) if angle==25 else None,'positive_depth_all_vertices':all(q.z>0 for q in ps),'projection_max_diff_from_producer':max(abs(x['x']-y['projected_right_x']) for x,y in zip(rows,pr['line_diagnostics'])),'mean_abs_residual':sum(abs(x['residual']) for x in rows)/91,'three_original_points':[x for x in rows if x['y'] in [375,425,465]],'self_visible_rows':sum(x['first']==o.name for x in rows),'other_world_geometry_exact':all(d[n]==original[n] for n in d if n!=o.name),'other_matrices_exact':other=={x.name:[list(r) for r in x.matrix_world] for x in s.objects if x!=o},'contacts':contacts})
(O/'check.json').write_text(json.dumps(out,indent=2));print([(x['angle'],x['projection_max_diff_from_producer'],x['self_visible_rows']) for x in out['rows']])
