import bpy,json,math,hashlib
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parent/'dreamfold-phone-study-20261104';bpy.ops.wm.open_mainfile(filepath=str(R/'versions/V03/models/phone-material.blend'));s=bpy.context.scene;cam=s.camera;o=bpy.data.objects['P04_rear_leaf_unseen_geometry_INFERRED'];f=json.load(open(R/'qa/camera-fit.json'));T=Matrix(f['rotation']).to_4x4();T.translation=Vector(f['translation']);pivot=Vector((0,.6,-.025))
def setangle(deg):
 a=math.radians(deg);A=Matrix.Rotation(a,4,'X');A.translation=pivot+A.to_3x3()@Vector((0,-.6,0));o.matrix_world=T@A;bpy.context.view_layer.update()
def convex(pts):
 p=sorted(set(pts))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lo=[];hi=[]
 for q in p:
  while len(lo)>1 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>1 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return lo[:-1]+hi[:-1]
def projection(obj):
 pts=[]
 for v in obj.data.vertices:
  p=world_to_camera_view(s,cam,obj.matrix_world@v.co);pts.append((1080*p.x,603*(1-p.y)))
 return convex(pts)
def right_x(poly,y):
 xs=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if min(a[1],b[1])<=y<=max(a[1],b[1]) and abs(a[1]-b[1])>1e-10:xs.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
 return max(xs) if xs else None
def bvh(obj):return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons])
base_other={ob.name:[list(row) for row in ob.matrix_world] for ob in s.objects if ob!=o};result=[]
for deg in [25,30,35,40,45,50,55]:
 setangle(deg);poly=projection(o);ds=[];ray=[]
 for y in range(375,466):
  x=right_x(poly,y);sx=901+(y-375)*9/50 if y<=425 else 910+(y-425)*7/40;tol=6 if y<=425 else 6+(y-425)/40
  direction=Vector(((x-.75-540)/1000,(301.5-y)/1000,-1)).normalized();hit=s.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.location,direction)
  ray.append(hit[4].name if hit[0] else None);ds.append({'y':y,'projected_right_x':x,'source_interpolated_x':sx,'subjective_x_half_band':tol,'signed_residual':x-sx,'outside_band':max(0,abs(x-sx)-tol),'visible_owner_inward_0_75px':ray[-1]})
 bv=bvh(o);contacts=[]
 for ob in s.objects:
  if ob.type=='MESH' and ob!=o:contacts.append({'object':ob.name,'triangle_overlap_pairs':len(bv.overlap(bvh(ob)))})
 result.append({'angle_degrees':deg,'projected_rear_hull':poly,'line_diagnostics':ds,'mean_abs_x_residual':sum(abs(d['signed_residual']) for d in ds)/len(ds),'max_abs_x_residual':max(abs(d['signed_residual']) for d in ds),'mean_outside_subjective_band':sum(d['outside_band'] for d in ds)/len(ds),'rows_outside_band':sum(d['outside_band']>0 for d in ds),'rear_visible_rows':ray.count(o.name),'total_rows':len(ray),'intersection_diagnostics':contacts,'all_other_object_matrices_exact':base_other=={ob.name:[list(row) for row in ob.matrix_world] for ob in s.objects if ob!=o}})
json.dump({'source_model':'V03 material BLEND at f8b81787d488c7341ca51304e507e5ec746793c1','constraint':'Single uncertain middle edge only; x-band interpolated along y375..465, not independent91 landmarks or calibrated statistics. Original P04 length,width,thickness fixed. Pivot inferred existing top axis. Only angle varies. Rear bottom/unknown ascending band excluded.','scan':result},open(D/'scan.json','w'),indent=2)
print([(x['angle_degrees'],x['mean_abs_x_residual'],x['mean_outside_subjective_band'],x['rows_outside_band'],x['rear_visible_rows']) for x in result])
