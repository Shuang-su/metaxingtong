import bpy,math,json,pathlib,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,c,rough=.55,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*c,1);n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal
 if emit:n.inputs['Emission Color'].default_value=(*c,1);n.inputs['Emission Strength'].default_value=emit
 return m
wall=mat('Warm_wall_proxy',(.23,.20,.16),.76);trim=mat('Dark_trim',(.075,.055,.035),.48);floor=mat('Stone_floor_proxy',(.19,.18,.16),.48);gold=mat('Gold_footline',(.48,.33,.14),.32,.65);dark=mat('Lantern_bronze',(.07,.045,.018),.35,.7);glass=mat('Warm_diffuser_proxy',(.9,.69,.35),.4,0,2);panel=mat('Ceiling_luminous_panel',(.9,.82,.69),.5,0,2);door=mat('Dark_red_door',(.12,.025,.018),.55);red=mat('Red_lit_text',(.9,.025,.008),.35,0,4);black=mat('Black_sign_back',(.015,.008,.005),.6);clay=mat('WHITE_clay',(.7,.7,.7),.8)
def assign(o,name,m):o.name=name;o.data.materials.append(m);o['source_status']='UNACCEPTED inferred dimensions; report screenshots not native';return o
def cube(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return assign(o,n,m)
def cyl(n,loc,r,dep,m,verts=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=dep,location=loc);return assign(bpy.context.object,n,m)
def rod(n,a,b,r,m,verts=12):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m,verts);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def frustum(n,loc,r1,r2,dep,m,verts=6):
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=dep,location=loc);return assign(bpy.context.object,n,m)
def sphere(n,loc,r,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=loc);return assign(bpy.context.object,n,m)
# Explicit finite shell; all dimensions working units and unknown rear structure inferred.
cube('FLOOR_finite_slab',(0,0,-.12),(5.36,12.36,.24),floor)
cube('CEILING_finite_slab',(0,0,3.92),(5.36,12.36,.24),wall)
for side in [-1,1]:
 cube(f'WALL_side_{side}',(side*2.59,0,1.9),(.18,12.36,3.8),wall)
 cube(f'BASEBOARD_{side}',(side*2.475,0,.055),(.05,12,.11),gold)
 cube(f'SOFFIT_{side}',(side*1.875,0,3.64),(1.25,12,.32),trim)
 for j,y in enumerate([-6,-4,-2,0,2,4,6]):cube(f'WALL_BATTEN_{side}_{j}',(side*2.48,y,1.95),(.045,.055,3.7),trim)
 # Four right lamp housings observed in image23; left-four symmetry is inferred. Image08 count/state unconfirmed.
 for j,y in enumerate([-2.5,0,2.5,5.0]):
  prefix=f'LANTERN_{side}_{j}';x=side*2.18;z=2.42
  back=cyl(prefix+'_wall_plate',(side*2.472,y,z-.08),.095,.04,dark);back.rotation_euler[1]=math.pi/2
  rod(prefix+'_bracket',(side*2.46,y,z-.12),(x,y,z+.11),.018,dark)
  frustum(prefix+'_diffuser',(x,y,z),.075,.13,.30,glass)
  frustum(prefix+'_roof',(x,y,z+.19),.15,.035,.08,dark)
  cyl(prefix+'_bottom_ring',(x,y,z-.155),.08,.025,dark,6)
  sphere(prefix+'_finial',(x,y,z+.25),.027,dark)
  frustum(prefix+'_lower_tip',(x,y,z-.20),.012,.075,.065,dark)
  for k in range(6):
   a=k*math.tau/6;rod(prefix+f'_rib{k}',(x+.075*math.cos(a),y+.075*math.sin(a),z-.15),(x+.13*math.cos(a),y+.13*math.sin(a),z+.15),.009,dark,8)
  ld=bpy.data.lights.new(prefix+'_light','POINT');ld.energy=12;ld.color=(1,.72,.36);ld.shadow_soft_size=.09;lo=bpy.data.objects.new(prefix+'_light',ld);bpy.context.collection.objects.link(lo);lo.location=(x-side*.10,y,z)
 for j,y in enumerate([-4.8,-2.4,0,2.4,4.8]):
  cyl(f'SPOT_rim_{side}_{j}',(side*1.8,y,3.466),.06,.025,dark)
  cyl(f'SPOT_diffuser_{side}_{j}',(side*1.8,y,3.449),.043,.008,panel)
# Real door opening framed by wall pieces; closed door leaf is independent solid.
for end in [-1,1]:
 y=end*6.09;w=1.15 if end==1 else 1.6;h=2.35 if end==1 else 2.5
 for side in [-1,1]:cube(f'WALL_end_{end}_jamb_{side}',(side*(2.5+w/2)/2,y,1.9),(2.5-w/2,.18,3.8),wall)
 cube(f'WALL_end_{end}_lintel',(0,y,(h+3.8)/2),(w,.18,3.8-h),wall)
 for side in [-1,1]:cube(f'DOOR_trim_{end}_{side}',(side*(w/2+.035),end*5.97,h/2),(.07,.08,h),trim)
 cube(f'DOOR_trim_{end}_top',(0,end*5.97,h+.035),(w+.14,.08,.07),trim)
 leaf=cube(f'DOOR_leaf_{end}',(0,end*6.035,h/2),(w-.025,.055,h-.02),door);leaf['evidence']='End+1 ON AIR visible; End-1 inferred unseen closure, not observed connected room'
 rod(f'DOOR_handle_{end}',(.36,end*5.985,1.05),(.36,end*5.91,1.05),.025,gold)
 cube(f'BASEBOARD_end_{end}_left',(-(2.5+w/2)/2,end*5.975,.055),(2.5-w/2,.05,.11),gold)
 cube(f'BASEBOARD_end_{end}_right',((2.5+w/2)/2,end*5.975,.055),(2.5-w/2,.05,.11),gold)
cube('ONAIR_sign_back',(0,5.94,2.64),(.65,.08,.25),black)
bpy.ops.object.text_add(location=(0,5.892,2.565));o=bpy.context.object;o.name='ONAIR_text';o.data.body='ON AIR';o.data.align_x='CENTER';o.data.size=.18;o.data.extrude=.002;o.rotation_euler=(math.pi/2,0,0);bpy.ops.object.convert(target='MESH');o.data.materials.append(red)
# Two rows of luminous ceiling panels, fixed warm state for every camera.
for j,y in enumerate([-4.8,-2.88,-.96,.96,2.88,4.8]):
 for side in [-1,1]:
  cube(f'CEILING_panel_{side}_{j}',(side*.60,y,3.775),(1.07,1.70,.05),panel)
  if j%2==1:
   ld=bpy.data.lights.new(f'CEILING_area_{side}_{j}','AREA');ld.energy=55;ld.shape='RECTANGLE';ld.size=1.;ld.size_y=1.5;ld.color=(1,.88,.72);lo=bpy.data.objects.new(ld.name,ld);bpy.context.collection.objects.link(lo);lo.location=(side*.60,y,3.71)
 cube(f'CEILING_crossrail_{j}',(0,y-.9,3.74),(2.5,.10,.12),trim)
cube('CEILING_center_rail',(0,0,3.74),(.13,12,.12),trim)
# Source hypotheses, same scene and lighting; no lens shift or hidden geometry.
def camera(n,pos,target,lens=24,roll=0):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();
 if roll:
  from mathutils import Quaternion
  o.rotation_mode='QUATERNION';o.rotation_quaternion=o.rotation_euler.to_quaternion()@Quaternion((0,0,1),roll)
 d.lens=lens;d.sensor_width=36;o['status']='manual uncalibrated camera hypothesis, source FAILED';return o
camera('SOURCE_08_wide',(0,-4.7,1.75),(0,4,1.85),22)
camera('SOURCE_23_oblique',(-.25,-3.9,1.25),(.1,4.3,1.95),20,math.radians(-15))
camera('SOURCE_26_side',(-2.1,-.5,1.45),(2.5,.3,1.5),23)
camera('MAIN_corridor',(-1.65,-4.9,1.7),(.15,3.1,1.8),23)
checks=[((-1.9,-5.25,2.8),(0,2,1.8)),((1.9,-5.25,1.1),(0,2.4,1.8)),((-1.9,5.25,2.8),(0,-2,1.8)),((1.9,5.25,1.1),(0,-2.4,1.8)),((0,0,.3),(0,3,2.3)),((0,0,3.4),(0,-3,.3)),((-2,0,1.9),(2.5,0,1.8)),((2,0,1.9),(-2.5,0,1.8))]
for i,(p,t) in enumerate(checks,1):camera(f'CHECK_{i:02d}',p,t,19)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.world.color=(.045,.045,.045);s.view_settings.view_transform='AgX';s.camera=bpy.data.objects['MAIN_corridor']
from mathutils import Matrix
for name,rec in json.load(open(P/'qa/R02-line-fit.json')).items():
 o=bpy.data.objects[name];o.rotation_mode='QUATERNION';o.matrix_world=Matrix(rec['matrix_world']);o.data.lens=rec['lens'];o['status']='UNACCEPTED line-support trained camera; no source acceptance'
bpy.context.view_layer.update()
# Material model first; white variant shares full geometry, lamps/cameras; only mesh material replaced.
records={}
for mode in ['material','white']:
 if mode=='white':
  for o in bpy.data.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
 f=P/'models'/f'R02_{mode}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R02_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);records[mode]={'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'camera_count':sum(o.type=='CAMERA' for o in bpy.data.objects),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'qa/R02-build-summary.json').write_text(json.dumps(records,indent=2))
