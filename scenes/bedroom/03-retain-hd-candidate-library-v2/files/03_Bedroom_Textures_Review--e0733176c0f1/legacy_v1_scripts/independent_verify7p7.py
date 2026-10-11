import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,kdtree
R=Path('/workspace/scratch/fa58bfcf0425/bedroom_fullroom/final7p7'); F=R/'models/01_bedroom_material.blend'
bpy.ops.wm.open_mainfile(filepath=str(F));s=bpy.context.scene;bpy.context.view_layer.update();sh=bpy.data.objects['完整四墙_厚0.18_真实门窗洞'];dg=bpy.context.evaluated_depsgraph_get()
def objray(o,a,b):
 inv=o.matrix_world.inverted();a=inv@Vector(a);b=inv@Vector(b);return o.ray_cast(a,(b-a).normalized(),distance=(b-a).length)[0]
def ray(a,b):
 a=Vector(a);v=Vector(b)-a;hit,p,n,i,o,m=s.ray_cast(dg,a,v.normalized(),distance=v.length);return {'hit':hit,'object':o.name if o else None,'pos':list(p) if hit else None}
# Dense near-seam probes: 4 corners, each two faces, floor/top at distances down to 1e-5; 2176 perpendicular/diagonal rays.
miss=[];total=0
zs=[.00001,.0001,.001,.005,.02,.05]+[3.3*i/100 for i in range(1,100)]+[3.25,3.28,3.295,3.299,3.2999,3.29999]
for x0,sx in [(-3.52,1),(3.92,-1)]:
 for y0,sy in [(-7.7,1),(-.011,-1)]:
  for eps in [.00001,.0001,.001,.005,.02,.05,.1]:
   for z in zs:
    a=(x0+sx*eps,y0+sy*eps,z)
    for b in [(x0-sx*.3,a[1],z),(a[0],y0-sy*.3,z),(x0-sx*.3,y0-sy*.3,z)]:
     total+=1
     if not objray(sh,a,b):miss.append([a,b])
# Dense opening grid, omit frames by leaving .08 margins.
openfail=[];openn=0
for iy in range(1,20):
 for iz in range(1,15):
  a=(-3.3,-3.2+1.9*iy/20,1.15+1.4*iz/15);b=(-3.9,a[1],a[2]);openn+=1
  if objray(sh,a,b):openfail.append(['window',a])
for ix in range(1,20):
 for iz in range(1,24):
  a=(-2.9+1.1*ix/20,-7.45,2.3*iz/24);b=(a[0],-8.05,a[2]);openn+=1
  if objray(sh,a,b):openfail.append(['door',a])
# floor and roof seam coverage sampled inside 1e-5 from every perimeter, and outer thickness
seammiss=[];seamn=0
for z,name,d in [(.02,'实体地板_厚0.16',-.3),(3.28,'实体天花_厚0.16',3.6)]:
 o=bpy.data.objects[name]
 for i in range(201):
  t=i/200
  for xy in [(-3.52+7.44*t,-7.7+.00001),(-3.52+7.44*t,-.011-.00001),(-3.52+.00001,-7.7+7.689*t),(3.92-.00001,-7.7+7.689*t)]:
   seamn+=1
   if not objray(o,(*xy,z),(*xy,d)):seammiss.append([name,xy])
meshissues=[];hidden=[];mods=[]
for o in s.objects:
 if o.hide_render or o.hide_viewport:hidden.append([o.name,o.hide_render,o.hide_viewport])
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);nm=sum(not e.is_manifold for e in bm.edges);inc=sum(e.is_manifold and not e.is_contiguous for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);vol=bm.calc_volume(signed=True)
 if nm or inc or deg or vol<-1e-9:meshissues.append({'name':o.name,'nonmanifold':nm,'inconsistent_edge_normals':inc,'degenerate':deg,'volume':vol})
 bm.free()
 if o.modifiers:mods.append([o.name,[(m.type,m.show_render,m.show_viewport) for m in o.modifiers]])
lights=[]
for o in s.objects:
 if o.type!='LIGHT' or o.data.type!='AREA':continue
 d=o.data
 if d.shape in ['DISK','ELLIPSE']:pts=[Vector((d.size/2*math.cos(i*math.tau/4096),(d.size_y if d.shape=='ELLIPSE' else d.size)/2*math.sin(i*math.tau/4096),0)) for i in range(4096)]
 else:pts=[Vector((x*d.size/2,y*(d.size_y if d.shape=='RECTANGLE' else d.size)/2,0)) for x in [-1,1] for y in [-1,1]]
 pts=[o.matrix_world@p for p in pts];clear=min(min(p.x+3.52,3.92-p.x,p.y+5.55,-.011-p.y,p.z,3.3-p.z) for p in pts)
 lights.append({'name':o.name,'shape':d.shape,'samples':len(pts),'minimum_boundary_clearance':clear,'inside':clear>0})
# Swept width .6 entrance path, densely sampled horizontal and cross rays.
walk=[];walkn=0
for z in [.05,.15,.5,1,1.5,1.8]:
 for ix in range(13):
  x=-2.65+.6*ix/12;walkn+=1;r=ray((x,-7.85,z),(x,-.75,z))
  if r['hit']:walk.append({'x':x,'z':z,**r})
# Bounds for furniture support review.
bounds={}
for o in s.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ['plinth','skid','pot','rug','leg','cabinet','mattress']):
  pts=[o.matrix_world@v.co for v in o.data.vertices];bounds[o.name]=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
report={'file_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'wall_near_seam_rays':total,'wall_misses':miss,'floor_ceiling_perimeter_rays':seamn,'floor_ceiling_misses':seammiss,'opening_grid_rays':openn,'opening_shell_hits':openfail,'mesh_issues':meshissues,'hidden_objects':hidden,'modifiers':mods,'animation_data':[(o.name) for o in s.objects if o.animation_data],'handlers':[str(x) for x in bpy.app.handlers.render_pre],'lights':lights,'walkway_rays':walkn,'walkway_collisions':walk,'furniture_bounds':bounds}
(R/'analysis/independent_geometry_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='furniture_bounds'},ensure_ascii=False))
