import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];A=json.loads((R/'qa/apertures-R02.json').read_text());P=json.loads((R/'qa/parameters-R02.json').read_text())['footprint']
def state():
 return {o.name:{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world]} for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(R/'models/ferris_remake_R03_material.blend'));orig=state();ds=bpy.context.evaluated_depsgraph_get();bounds={};vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 e=o.evaluated_get(ds);m=e.to_mesh();ww=[o.matrix_world@v.co for v in m.vertices];bounds[o.name]=[[min(v[k] for v in ww),max(v[k] for v in ww)] for k in range(3)]
 if o.get('qa_group')=='structure':
  n=len(vs);vs+=ww;fs += [tuple(n+i for i in f.vertices) for f in m.polygons]
 e.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs)
def inside(x,y):
 hit=False
 for a,b in zip(P,P[1:]+P[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit

def opening(face,p):
 if face==0 and abs(p.x)<.505 and .05<p.z<2.56:return 'front entry'
 for a in A:
  if a['face']!=face:continue
  u=abs((p-Vector(a['plane'])).dot(Vector(a['u']))-a['center_u']);z=abs(p.z-a['center_z']);hw=a['inner_width']/2;hh=a['inner_height']/2;r=a['radius']
  if u<=hw and z<=hh and (max(u-hw+r,0)**2+max(z-hh+r,0)**2<=r*r):return a['id']
 return None
counts={'local_total':0,'local_hits':0,'allowed_aperture_miss':0,'unexpected_miss':0};fails=[]
def probe(face,p,n):
 counts['local_total']+=1;q,_,_,_=tree.ray_cast(p-n*.22,n,.44)
 if q is not None:counts['local_hits']+=1
 elif opening(face,p):counts['allowed_aperture_miss']+=1
 else:counts['unexpected_miss']+=1;fails.append({'face':face,'p':list(p)})
for i in range(8):
 a=Vector((*P[i],0));b=Vector((*P[(i+1)%8],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0))
 for j in range(100):
  for k in range(120):probe(i,a+(b-a)*((j+.5)/100)+Vector((0,0,.05+2.54*(k+.5)/120)),n)
for name,z,sign in [('floor',.05,-1),('ceiling',2.59,1)]:
 for j in range(100):
  for k in range(100):
   x=-1.62+3.24*(j+.5)/100;y=-1.85+3.7*(k+.5)/100
   if inside(x,y):probe(name,Vector((x,y,z)),Vector((0,0,sign)))
report={'sample':{'wall_grid':[100,120],'floor_ceiling_grid':[100,100],'max_distance':.44,'origin_offset':.22},'counts':counts,'fails':fails,'limits':['Finite rays not topology proof','Actual rounded aperture specification same as builder black inner shape','Open entrance intentional; door open state inferred','No source acceptance from structural sampling'],'bounds':bounds}
(R/'qa/structural-rays-R03.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(R/'models/ferris_remake_R03_white.blend'));ws=state();gray=[(o.name,[m.name for m in o.data.materials]) for o in bpy.context.scene.objects if o.type=='MESH'];same=ws==orig
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'models/ferris_remake_R03_material.glb'));ib={}
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  w=[o.matrix_world@v.co for v in o.data.vertices];ib[o.name]=[[min(v[k] for v in w),max(v[k] for v in w)] for k in range(3)]
missing=sorted(set(bounds)-set(ib));err=max([abs(bounds[n][k][j]-ib[n][k][j]) for n in bounds if n in ib for k in range(3) for j in range(2)] or [0]);(R/'qa/glb-white-R03.json').write_text(json.dumps({'original_meshes':len(orig),'white_meshes':len(ws),'white_geometry_exact':same,'persistent_white_materials':gray,'GLB_reimport_meshes':len(ib),'missing':missing,'max_bounds_delta':err,'contact_support_floor_model_units':0.165-.23/2-.05,'limits':'bounds/mesh checks not topology or source acceptance'},indent=2))
print('R03_CORE_QA_COMPLETE')
