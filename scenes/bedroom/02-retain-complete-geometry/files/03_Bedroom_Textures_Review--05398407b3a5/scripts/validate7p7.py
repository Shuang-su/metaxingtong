import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;D=R/'final7p7';bpy.ops.wm.open_mainfile(filepath=str(D/'models/01_bedroom_material.blend'));s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
meshes=[o for o in s.objects if o.type=='MESH'];errors=[];nonman=[];neg=[];flat=[];digest=hashlib.sha256()
for o in sorted(meshes,key=lambda x:x.name):
 bm=bmesh.new();bm.from_mesh(o.data)
 deg=sum(f.calc_area()<1e-12 for f in bm.faces)
 if deg:errors.append([o.name,deg])
 nm=sum(not e.is_manifold for e in bm.edges)
 if nm:nonman.append([o.name,nm])
 if not nm and bm.calc_volume(signed=True)<-1e-9:neg.append(o.name)
 bm.free();digest.update(o.name.encode());digest.update(str(tuple(tuple(r) for r in o.matrix_world)).encode())
 for v in o.data.vertices:digest.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:digest.update(str(tuple(p.vertices)).encode())
def ray(a,b):
 a=Vector(a);v=Vector(b)-a;hit,loc,norm,idx,o,mat=s.ray_cast(dg,a,v.normalized(),distance=v.length)
 return {'hit':hit,'object':o.name if o else None,'position':list(loc) if hit else None,'normal':list(norm) if hit else None}
# Corner top/middle/base probes from interior and exterior. Reach <.3 beyond expected wall.
rays=[]
for z in [.18,1.5,3.26]:
 for x in [-3.5,3.9]:
  for y in [-7.68,-.031]:
   center=(x,y,z)
   for axis,end in [('x',(-3.8 if x<0 else 4.2,y,z)),('y',(x,-8.0 if y<-2 else .3,z))]:rays.append({'a':center,'b':end,**ray(center,end)})
# Opening ray passes shell, glass expected in window. Door threshold excluded by z.
openings={'door_center':ray((-2.35,-7.45,1.4),(-2.35,-8.1,1.4)),'door_left_jamb':ray((-2.95,-7.45,1.4),(-2.95,-8.1,1.4)),'door_header':ray((-2.35,-7.45,2.36),(-2.35,-8.1,2.36)),'window_center':ray((-3.3,-2.6,1.8),(-3.9,-2.6,1.8)),'window_bottom':ray((-3.3,-2.6,1.05),(-3.9,-2.6,1.05))}
# Direct shell local ray through window should return no hit; glass is a separate object.
sh=bpy.data.objects['完整四墙_厚0.18_真实门窗洞'];mi=sh.matrix_world.inverted();a=mi@Vector((-3.3,-2.6,1.8));b=mi@Vector((-3.9,-2.6,1.8));opening_wall_clear=not sh.ray_cast(a,(b-a).normalized(),distance=(b-a).length)[0]
lights=[]
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='AREA':
  r=o.data.size/2;pts=[o.matrix_world@Vector((r*math.cos(2*math.pi*i/128),r*math.sin(2*math.pi*i/128),0)) for i in range(128)]
  clearance=min(min(p.x+3.52,3.92-p.x,p.y+5.55,-.011-p.y,p.z,3.3-p.z) for p in pts)
  lights.append({'name':o.name,'boundary_samples':128,'entire_disk_inside_by_horizontal_analytic_extent':clearance>0,'minimum_clearance':clearance,'size':o.data.size})
# Support: ray from representative near underside points down to first support.
supports=[]
for name,xy,z in [('床台底座',(0,-1.5),.028),('地毯',(1.4,-2.7),.008),('花盆',(2.92,-.96),.008),('床柜右脚',(1.693,-.64),.008)]:
 supports.append({'name':name,'expected_bottom':z,'down_from_below':ray((*xy,z-.0005),(*xy,-.05))})
# Human-width route from entrance left of bed, at ankle/torso/head levels and +/- .30 width.
path=[(-2.35,-7.55),(-2.35,-6),(-2.35,-4),(-2.35,-2.7),(-2.35,-1)]
path_collisions=[]
for z in [.15,1,1.8]:
 for off in [-.3,0,.3]:
  for a,b in zip(path,path[1:]):
   r=ray((a[0]+off,a[1],z),(b[0]+off,b[1],z))
   if r['hit']:path_collisions.append(r)
# All mesh bounds against full exterior box. Door frame/purposeful sill may exceed wall extents by <= .1.
extent=[]
for o in meshes:
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 if any(p.x < -3.86 or p.x>4.2 or p.y< -8.0 or p.y>.31 or p.z<-.161 or p.z>3.461 for p in pts):extent.append(o.name)
report={'geometry_sha256':digest.hexdigest(),'mesh_count':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'faces':sum(len(o.data.polygons) for o in meshes),'degenerate_faces':errors,'nonmanifold_objects':nonman,'negative_signed_volume_objects':neg,'corner_rays':rays,'corner_rays_all_hit':all(r['hit'] for r in rays),'openings':openings,'window_shell_ray_clear':opening_wall_clear,'area_lights':lights,'supports':supports,'support_note':'左床柜脚位于软地毯边缘，穿入绒面约0.02模型单位；右脚/花盆接木地板。床底接地毯。','walkway_test_width':.6,'walkway_collisions':path_collisions,'exterior_bounds_exceptions':extent,'source_fit':'NOT_MET: no independent side reference, moved old exterior camera inside finite room; two frontal zoom comparisons only'}
(D/'analysis/structure_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['corner_rays','supports']},ensure_ascii=False,indent=2))
