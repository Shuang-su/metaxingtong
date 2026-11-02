import bpy,math,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
records=[]
def mat(n,c,metal=0,rough=.45,emit=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
red=mat('red cabinet observed',(.42,.018,.012),.12,.35);black=mat('dark glossy panels',(.012,.012,.015),.3,.22);rubber=mat('speaker rubber',(.018,.016,.019),.1,.42);gold=mat('observed gold markings',(.65,.32,.075),.4,.4);white=mat('white LED',(.8,.88,1),0,.3,2);placeholder=mat('unobserved graphic neutral',(.055,.06,.065));cyan=mat('display placeholder not source texture',(.12,.28,.43),0,.4,.3);wall=mat('red wall fine grid',(.24,.018,.015));floor=mat('checker floor observed',(.3,.3,.3),.1,.25)
n=floor.node_tree.nodes;l=floor.node_tree.links;tc=n.new('ShaderNodeTexCoord');ch=n.new('ShaderNodeTexChecker');ch.inputs['Scale'].default_value=2.4;ch.inputs['Color1'].default_value=(.65,.66,.67,1);ch.inputs['Color2'].default_value=(.018,.018,.02,1);l.new(tc.outputs['Object'],ch.inputs['Vector']);l.new(ch.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
n=wall.node_tree.nodes;l=wall.node_tree.links;tc=n.new('ShaderNodeTexCoord');b=n.new('ShaderNodeTexBrick');b.inputs['Scale'].default_value=5;b.inputs['Mortar Size'].default_value=.01;b.inputs['Brick Width'].default_value=.5;b.inputs['Row Height'].default_value=.5;b.offset=0;b.inputs['Color1'].default_value=(.25,.014,.01,1);b.inputs['Color2'].default_value=(.32,.022,.015,1);b.inputs['Mortar'].default_value=(.075,.005,.004,1);l.new(tc.outputs['Generated'],b.inputs['Vector']);l.new(b.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
def mark(o,n,m,e='Observed type/count; working dimensions and hidden rear inferred',kind='solid'):
 o.name=n;o.data.materials.append(m);o['evidence']=e;o['validation_class']=kind;records.append({'id':n,'evidence':e,'class':kind});return o

def box(n,loc,sz,m,bev=.015,e=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=sz;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  mod=o.modifiers.new('physical bevel','BEVEL');mod.width=bev;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return mark(o,n,m,e or 'Observed surface/assembly; dimensions inferred')
def sphere(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return mark(o,n,m)
def disk(n,x,y,z,r,m):
 verts=[(x+r*math.cos(k*2*math.pi/48),y,z+r*math.sin(k*2*math.pi/48))for k in range(48)];me=bpy.data.meshes.new(n);me.from_pydata(verts,[],[list(range(48))]);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);return mark(o,n,m,'Observed printed flat mark; radius/location working inference','printed_sheet')
def strip(n,pts,m,r=.01):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1;cu.use_fill_caps=True;p=cu.splines.new('POLY');p.points.add(len(pts)-1)
 for a,v in zip(p.points,pts):a.co=(*v,1)
 o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False);return mark(o,n,m,'Printed/light graphic represented by thin strip, not raised sculptural detail','graphic_strip')
# Closed provisional room. All dimensions arbitrary working model units, no observed front/ceiling/openings.
box('ROOM_floor',(0,-5.35,-.12),(12.4,13.5,.24),floor,0,'Floor seen; full observer-side extent inferred')
box('ROOM_ceiling',(0,-5.35,5.32),(12.4,13.5,.24),placeholder,0,'Ceiling entirely inferred')
box('ROOM_back',(0,1.4,2.6),(12.4,.24,5.2),wall,0,'Back wall visible, exact position/height inferred')
box('ROOM_front',(0,-12.1,2.6),(12.4,.24,5.2),placeholder,0,'Observer-side boundary entirely inferred, not a camera feasibility bound')
for side in [-1,1]:box('ROOM_side_'+str(side),(side*6.2,-5.35,2.6),(.24,13.5,5.2),wall,0,'Right wall visible in oblique; left extent/height inferred')
for i,cx in enumerate([-3.5,0,3.5],1):
 p=f'M{i:02d}';box(p+'_plinth',(cx,.20,.075),(2.8,1.0,.15),gold,.015)
 box(p+'_body',(cx,.38,1.48),(2.7,.78,2.66),red,.035)
 box(p+'_lower_face',(cx,-.025,.51),(2.65,.12,.70),red,.025)
 box(p+'_coin_bay',(cx,.005,1.10),(2.6,.12,.45),red,.015)
 box(p+'_shelf',(cx,-.13,.84),(2.73,.5,.045),black,.01)
 box(p+'_screen_frame',(cx,-.07,2.04),(2.72,.24,1.62),red,.05)
 box(p+'_screen_recess',(cx,-.202,2.12),(2.45,.03,1.16),black,.07)
 box(p+'_display',(cx,-.223,2.12),(2.32,.012,1.03),cyan,.065,'Display graphics are placeholder, no source texture yet')
 box(p+'_control',(cx,-.19,1.43),(2.65,.16,.33),red,.02)
 for side in [-1,1]:
  box(p+'_gold_button_'+str(side),(cx+side*1.03,-.284,1.43),(.27,.014,.23),gold,.015)
  for k,(dx,dz)in enumerate([(0,0),(-.11,0),(.11,0),(0,.09),(0,-.09)]):disk(p+f'_LED_{side}_{k}',cx+side*.62+dx,-.285,1.43+dz,.025,white)
  for layer,rad,y,thick in [('outer',.24,-.12,.06),('cone',.19,-.155,.025),('dome',.075,-.18,.035)]:sphere(p+f'_LOW_{side}_{layer}',(cx+side*.94,y,.49),(rad,thick,rad),rubber)
 box(p+'_coin_gold',(cx-.62,-.075,1.09),(.60,.025,.40),gold,.025)
 box(p+'_coin_slot',(cx-.50,-.096,1.08),(.08,.015,.19),black,.006)
 # Source-supported separate unknown prop, not a coin button; working back/feet and copying remain inferred.
 px=cx-.92;py=-.22;z=.8625
 for side in [-1,1]:box(p+f'_PROP_foot_{side}',(px+side*.035,py,z+.012),(.055,.07,.024),red,.005)
 sphere(p+'_PROP_body',(px,py,z+.13),(.09,.065,.12),red);sphere(p+'_PROP_head',(px,py,z+.29),(.07,.06,.07),red);sphere(p+'_PROP_front',(px,py-.062,z+.29),(.03,.027,.03),gold)
 for side in [-1,1]:box(p+f'_PROP_stub_{side}',(px+side*.035,py,z+.37),(.018,.024,.065),red,.005)
 # Higher header, unknown cut top plain closure; four circles, no fabricated full poster.
 box(p+'_header',(cx,.055,3.66),(2.72,.32,1.58),red,.025,'Four circles and tall board observed; absolute top/back inferred')
 box(p+'_header_blue',(cx,-.118,3.66),(1.72,.024,1.54),placeholder,.005,'Central source image pending conservative partial projection; unknown remains gray')
 for side in [-1,1]:
  for row,z in enumerate([3.12,3.58]):
   for layer,rad,y,depth in [('outer',.19,-.127,.035),('cone',.15,-.161,.02),('dome',.052,-.182,.025)]:sphere(p+f'_TOP_{side}_{row}_{layer}',(cx+side*1.08,y,z),(rad,depth,rad),rubber)
 for lab,x,z,r in [('L1',-1.146,4.383,.028),('L2',-1.206,4.273,.039),('L3',-1.207,4.111,.044),('L4',-1.103,3.996,.059),('L5',-.947,3.833,.078),('R1',1.139,3.993,.061),('R2',.977,3.835,.083)]:disk(p+'_HEADER_gold_'+lab,cx+x,-.106, z,r,gold)
 box(p+'_pad_base',(cx,-1.65,.095),(3.12,2.1,.19),red,.10)
 box(p+'_pad_top',(cx,-1.65,.194),(2.92,1.9,.012),black,.09)
 # Thin planar-ish light rings and arrows; physical raised heights not claimed.
 for k,(dx,dy,r)in enumerate([(0,0,.4),(-.9,-.58,.14),(.9,-.58,.14),(-.9,.58,.14),(.9,.58,.14)]):
  pts=[(cx+dx+r*math.cos(t*2*math.pi/64),-1.65+dy+r*math.sin(t*2*math.pi/64),.202)for t in range(65)];strip(p+'_PAD_ring_'+str(k),pts,white,.006)
 for j,(dx,dy)in enumerate([(-.75,0),(.75,0),(0,-.65),(0,.65)]):
  pts=[(cx+dx-.14,-1.65+dy+.09,.202),(cx+dx+.14,-1.65+dy,.202),(cx+dx-.14,-1.65+dy-.09,.202)];strip(p+'_PAD_arrow_'+str(j),pts,white,.007)

def camera(n,loc,target,lens=36):
 d=bpy.data.cameras.new(n);d.lens=lens;d.sensor_width=36;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['status']='Uncalibrated initial source hypothesis' if n.startswith('SRC')else'Geometry inspection only';return o
camera('SRC_front',(0,-10.5,2.0),(0,0,1.55),45);camera('SRC_oblique',(-4,-9,4.7),(.8,0,1.3),36)
camera('MAIN',(5,-9,4.2),(0,-.3,2),30)
for j,(loc,target)in enumerate([((-5,-8,3),(0,0,2)),((5,-8,3),(0,0,2)),((0,-10,4),(0,-.7,1.7)),((-5,-3,4.6),(0,-.5,1.8)),((5,-3,4.6),(0,-.5,1.8)),((0,-4,4.9),(0,-.5,.6)),((-4,-5,1.2),(0,0,1.3)),((4,-5,1.2),(0,0,1.3))],1):camera(f'CHECK{j:02d}',loc,target,24)
for n,loc,power,size in [('LARGE',(0,-4.5,4.8),1600,7),('FILL',(-4,-1.2,4.7),650,4),('RIGHT',(4,-1.2,4.7),650,4)]:
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
s.world.color=(.08,.08,.08);s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.camera=bpy.data.objects['MAIN'];s['status']='Nov2 genuine remake R00, not restored old bytes; source unaccepted'
(D/'qa/object_evidence_R00.json').write_text(json.dumps(records,indent=2))
def sig():return {o.name:{'matrix':[list(v)for v in o.matrix_world],'verts':[list(v.co)for v in o.data.vertices],'faces':[list(p.vertices)for p in o.data.polygons]}for o in s.objects if o.type=='MESH'}
a=sig();bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_remake_R00_material.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_remake_R00_material.glb'),export_format='GLB',export_cameras=True,export_lights=True)
w=mat('shared white',(.62,.62,.62),0,.6)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
assert a==sig();(D/'qa/shared_geometry_R00.json').write_text(json.dumps({'exact_material_white_vertices_topology_world':True,'mesh_count':len(a),'source_acceptance':False}))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_remake_R00_white.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_remake_R00_white.glb'),export_format='GLB',export_cameras=True,export_lights=True)
