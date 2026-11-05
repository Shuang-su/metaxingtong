import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r05.blend'));s=bpy.context.scene
old=[o for o in s.objects if o.name.startswith('CLOUD_2')]
pts=[o.matrix_world@v.co for o in old for v in o.data.vertices]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
# Contour is manual DESIGN-FAMILY interpretation of source10 crop (810,170,1145,330).
poly=[(6,118),(30,107),(52,95),(69,93),(86,101),(100,100),(96,86),(101,72),(113,67),(112,58),(116,45),(128,39),(143,40),(151,29),(167,20),(186,16),(202,21),(213,29),(228,31),(242,40),(248,54),(260,57),(269,69),(286,69),(299,76),(316,79),(326,91),(326,109),(316,124),(299,129),(296,142),(285,152),(270,155),(251,148),(238,143),(225,147),(202,148),(185,144),(166,147),(145,143),(125,139),(104,132),(87,123),(72,115),(52,115),(35,121),(20,121)]
# Catmull-Rom smooth manual contour; no image-derived texture.
smooth=[]
for i in range(len(poly)):
 a,b,c,d=[Vector(poly[k%len(poly)]) for k in [i-1,i,i+1,i+2]]
 for j in range(4):
  t=j/4;smooth.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
x0,x1=bounds[0];z0,z1=bounds[2];cy=4.3
minu,maxu=min(p.x for p in smooth),max(p.x for p in smooth);minv,maxv=min(p.y for p in smooth),max(p.y for p in smooth)
def xz(u,v):return (x0+(u-minu)/(maxu-minu)*(x1-x0), z1-(v-minv)/(maxv-minv)*(z1-z0))
def front(x,z):
 u=(x-x0)/(x1-x0);v=(z-z0)/(z1-z0)
 return cy-.022-.035*math.exp(-((u-.65)**2/.09+(v-.5)**2/.20))
verts=[(x,cy,z) for x,z in [xz(p.x,p.y) for p in smooth]]
gold=old[0].data.materials[0]
for o in old:bpy.data.objects.remove(o,do_unlink=True)
me=bpy.data.meshes.new('CLOUD_2 relief design-family surface');me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.update()
o=bpy.data.objects.new('CLOUD_2 continuous shallow relief proxy',me);s.collection.objects.link(o);o.data.materials.append(gold)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True)
for v in bm.verts:v.co.y=front(v.co.x,v.co.z)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
bpy.context.view_layer.objects.active=o;o.select_set(True);so=o.modifiers.new('INFERRED 0.08 model-unit thickness','SOLIDIFY');so.thickness=.08;so.offset=1;bpy.ops.object.modifier_apply(modifier=so.name);o.select_set(False)
# Normalize outward orientation, positive enclosed volume; front/back unknown source thickness.
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
bm.to_mesh(me);bm.free();o['evidence_status']='design-family front surface; back/thickness/relief inferred, instance unknown'
# Separate shallow embedded raised line paths in manual source10 crop coordinates.
paths=[]
for u,v,rad,start,turn in [(170,103,30,0,1.65),(118,82,18,1,1.45),(273,121,22,0,1.5),(177,44,17,1.8,1.4)]:
 arr=[]
 for i in range(65):
  t=i/64;a=start+turn*2*math.pi*t;r=4+(rad-4)*t;arr.append((u+r*math.cos(a),v+r*math.sin(a)))
 paths.append(arr)
paths.append([(16,117),(40,108),(62,104),(85,115),(110,126),(141,133),(173,132),(202,123),(226,110)])
for idx,path in enumerate(paths):
 c=bpy.data.curves.new('CLOUD_2 internal raised line','CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=.018;c.bevel_resolution=2;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(len(path)-1)
 for p,(u,v) in zip(sp.points,path):
  x,z=xz(u,v);p.co=(x,front(x,z)-.008,z,1)
 ob=bpy.data.objects.new('CLOUD_2 embedded motif %02d'%idx,c);s.collection.objects.link(ob);ob.data.materials.append(gold);ob['evidence_status']='manual family motif; not observed precise groove depth';bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
# Store manual trace and assumptions, including exact original source coordinates.
(P/'research-r06/manual-outline.json').write_text(json.dumps({'source10_crop':[810,170,1145,330],'source10_outline_pixels':[[u+810,v+170] for u,v in poly],'trace_role':'manual family interpretation, not source11 exact instance or metric measurement','source11_constraint':'continuous multi-lobe area with left tail; only ~129x59 pixels','existing_cloud2_bounds':bounds,'unchanged_group_center':[4.1,4.3,4.7],'inferred_thickness':.08,'motif_radius':.018,'motif_embedding':.01,'motif_paths_crop_pixels':paths},indent=2))
s.camera=bpy.data.objects['SOURCE11 conditional camera'];bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r06-experiment.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r06-experiment.glb'),export_format='GLB',export_cameras=True,export_extras=True)
