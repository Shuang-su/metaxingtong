import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.012,.014,.026,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.15
s.view_settings.view_transform='AgX'
def material(n,c,metal=0,rough=.5,emission=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m
wall=material('Muted burgundy wall approximate',(.16,.055,.055));floor=material('Plum carpet approximate',(.14,.075,.12),rough=.87);ivory=material('Ivory trim',(.55,.48,.43));gold=material('Gold bed frame',(.5,.32,.085),.75,.26);fabric=material('Dusty rose bedding',(.3,.13,.19),rough=.9);pillow=material('Pale pillow',(.52,.38,.39),rough=.92);curtain=material('Grey pleated curtains',(.33,.32,.38),rough=.9);red=material('Red lacquer bar',(.42,.012,.038),.12,.28);wood=material('Warm wood stool',(.28,.15,.085),rough=.5);white=material('White hourglass stool',(.65,.62,.67),.05,.3);black=material('Dark city proxy',(.006,.008,.012));windowmat=material('Window glass',(.45,.5,.6),rough=.06);windowmat.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=1
white_mat=material('WHITE clay',(.62,.62,.62),rough=.7)
def finish(o,n,m,role='observed silhouette; dimensions and hidden construction inferred'):
 o.name=n;o.data.materials.append(m);o['observation_status']=role;o['object_role']=n.split('_')[0];return o
def cube(n,loc,dim,m,bev=0,role='observed silhouette; dimensions and hidden construction inferred'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n,m,role)
 if bev:
  mod=o.modifiers.new('Small edge rounding','BEVEL');mod.width=bev;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(n,loc,r,h,m,N=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=h,location=loc);return finish(bpy.context.object,n,m)
def rod(n,a,b,r,m,N=12):
 d=Vector(b)-Vector(a);o=cyl(n,(Vector(a)+Vector(b))/2,r,d.length,m,N);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def mesh(n,v,f,m,role='observed silhouette; dimensions and hidden construction inferred'):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);finish(o,n,m,role);return o
def extrude_xz(n,poly,y0,y1,m,role='observed silhouette; hidden thickness inferred'):
 N=len(poly);v=[(x,y,z) for y in [y0,y1] for x,z in poly];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]
 for i in range(N):j=(i+1)%N;f.append((i,j,N+j,N+i))
 return mesh(n,v,f,m,role)
def lathe(n,x,y,profile,m,N=64):
 v=[(x+r*math.cos(i*2*math.pi/N),y+r*math.sin(i*2*math.pi/N),z) for z,r in profile for i in range(N)];f=[]
 for k in range(len(profile)-1):
  for i in range(N):j=(i+1)%N;f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
 f+=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 return mesh(n,v,f,m)
def tube(n,pts,r,m):
 # Smooth polyline curve converted to explicit mesh, end caps enabled.
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,c);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False);return finish(o,n,m)
# Finite enclosure: only rear window zone observed; side/front/ceiling extents explicitly inferred.
cube('FLOOR_bounded',(0,-.8,-.12),(13,12,.24),floor,role='Observed floor; finite footprint and underside inferred')
cube('WALL_left_inferred',(-6.6,-.8,2.65),(.2,12,5.3),wall,role='Unseen side enclosure inferred, not source confirmed')
cube('WALL_right_inferred',(6.6,-.8,2.65),(.2,12,5.3),wall,role='Unseen side enclosure inferred, not source confirmed')
cube('WALL_front_inferred',(0,-6.9,2.65),(13.4,.2,5.3),wall,role='Unseen front enclosure inferred, not source confirmed')
cube('CEILING_inferred',(0,-.8,5.4),(13.4,12.4,.2),wall,role='Unseen ceiling construction inferred')
# Arched window aperture is real geometry, not a dark painted rectangle.
xc=.4; rx=4.4; zbase=.18; rz=4.65; y0=5.1;y1=5.3; N=64
pts=[(xc-rx*math.cos(math.pi*i/N),zbase+rz*math.sin(math.pi*i/N)) for i in range(N+1)]
for i in range(N):
 a,b=pts[i],pts[i+1];extrude_xz(f'WALL_arch_spandrel_{i:02}',[a,b,(b[0],5.3),(a[0],5.3)],y0,y1,wall)
cube('WALL_rear_left',((-6.7+xc-rx)/2,5.2,2.65),(xc-rx+6.7,.2,5.3),wall)
cube('WALL_rear_right',((6.7+xc+rx)/2,5.2,2.65),(6.7-xc-rx,.2,5.3),wall)
cube('WALL_rear_sill',(xc,5.2,zbase/2),(rx*2,.2,zbase),ivory)
# Trim as radial band, one curved mesh; genuine opening retained.
inner=pts; outer=[(xc-(rx+.075)*math.cos(math.pi*i/N),zbase+(rz+.075)*math.sin(math.pi*i/N)) for i in range(N+1)]
for i in range(N):extrude_xz(f'WINDOW_arch_trim_{i:02}',[inner[i],inner[i+1],outer[i+1],outer[i]],4.99,5.11,ivory)
extrude_xz('WINDOW_glazing',[*pts,(xc-rx,zbase)],5.16,5.18,windowmat,role='Observed dark glazing; flat plane and thickness inferred, curvature unconfirmed')
cube('WINDOW_central_mullion',(xc,5.06,(zbase+rz)/2),(.11,.16,rz-zbase),ivory)
cube('WINDOW_lower_rail',(xc,5.03,.24),(8.8,.15,.12),ivory)
# Curtains: pleated finite thick volume, gathered inward at a waist. Not photon-based depth geometry.
for side,sign in [('L',-1),('R',1)]:
 cols=40;rows=28;v=[]
 for back in [0,1]:
  for j in range(rows+1):
   t=j/rows;z=.3+4.55*t;wid=.55+1.25*(abs(t-.36)**.8);edge=xc+sign*(rx-.05-.45*t)
   for i in range(cols+1):
    u=i/cols;x=edge-sign*wid*u;y=4.82-.09*math.sin(u*12*math.pi)+back*.035
    v.append((x,y,z))
 stride=cols+1;layer=(rows+1)*stride;f=[]
 for sideindex in [0,1]:
  off=sideindex*layer
  for j in range(rows):
   for i in range(cols):
    a=off+j*stride+i; q=(a,a+1,a+1+stride,a+stride);f.append(q if sideindex==0 else tuple(reversed(q)))
 boundary=list(range(stride))+[j*stride+cols for j in range(1,rows+1)]+[rows*stride+i for i in range(cols-1,-1,-1)]+[j*stride for j in range(rows-1,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):f.append((a,b,b+layer,a+layer))
 mesh('CURTAIN_'+side,v,f,curtain)
 cube('CURTAIN_tie_'+side,(xc+sign*3.75,4.68,1.95),(.65,.10,.14),ivory,.025)
# Bed left: golden nested rounded arches, bedding and visible soft volumes.
bx=-3.8;by=2.5
cube('BED_base',(bx,by,.38),(2.45,3.55,.34),wood,.1)
cube('BED_mattress',(bx,by,.65),(2.45,3.55,.28),pillow,.12)
cube('BED_blanket',(bx,by-.45,.83),(2.49,2.7,.15),fabric,.10)
for j,x in enumerate([bx-.63,bx+.63]):cube(f'BED_pillow_{j}',(x,by+1.15,.93),(1.02,.65,.22),pillow,.16)
for x in [bx-1.06,bx+1.06]:
 for y in [by-1.5,by+1.5]:cyl('BED_support_leg',(x,y,.18),.045,.36,gold)
for side,yy in [('head',by+1.8),('foot',by-1.8)]:
 for k in range(5):
  x=bx-1.12+k*.56; h=1.2+(.6 if side=='head' else .05)*(1-abs(k-2)/3);w=.53
  points=[(x-w/2,yy,.3),(x-w/2,yy,h-.27)]+[(x+.265*math.cos(math.pi-a*math.pi/18),yy,h-.27+.265*math.sin(math.pi-a*math.pi/18)) for a in range(19)]+[(x+w/2,yy,.3)]
  tube(f'BED_{side}_arch_{k}',points,.024,gold)
# Lamp near left bed.
lx=-5.45;ly=2.8
lathe('LAMP_base',lx,ly,[(.01,.3),(.05,.34),(.09,.25)],gold,48);cyl('LAMP_stem',(lx,ly,1.4),.026,2.66,gold)
# Hollow frustum shade with physical thickness, open top and bottom.
ringprofile=[(2.50,.43),(3.15,.25),(3.15,.23),(2.50,.41),(2.50,.43)]
lathe('LAMP_shade',lx,ly,ringprofile,ivory,64)
# Red waterfall bar is a continuous rounded U slab in side elevation, extruded across depth.
barx=3.75;length=3.1;top=1.55;th=.16;yfront=2.25;yback=3.12
# Horizontal top and broad supporting end panels. Rounded transitions are explicitly approximated.
cube('BAR_top',(barx,(yfront+yback)/2,top),(length,yback-yfront,.16),red,.075)
for sign in [-1,1]:cube('BAR_waterfall_end_'+str(sign),(barx+sign*(length/2-.08),(yfront+yback)/2,.79),(.16,yback-yfront,1.58),red,.075)
# Wooden cafe stools: 4 splayed legs, circular braces and bent curved braces.
for k,x in enumerate([3.0,4.45]):
 y=1.76;lathe(f'BARSTOOL{k}_seat',x,y,[(1.00,.27),(1.07,.29),(1.12,.25)],wood,48)
 for j in range(4):
  a=math.pi/4+j*math.pi/2;bottom=(x+.30*math.cos(a),y+.30*math.sin(a),.04);upper=(x+.19*math.cos(a),y+.19*math.sin(a),1.02);rod(f'BARSTOOL{k}_leg{j}',bottom,upper,.025,wood)
  rod(f'BARSTOOL{k}_brace{j}',(x+.25*math.cos(a),y+.25*math.sin(a),.36),(x+.25*math.cos(a+math.pi/2),y+.25*math.sin(a+math.pi/2),.36),.018,wood)
for k in range(4):
 x=3.3+k*.17;lathe(f'BAR_cup_{k}',x,2.89,[(1.63,.055),(1.78,.06),(1.80,.055)],ivory,24)
# Central iconic white spool / hourglass stool.
lathe('CENTRE_hourglass_stool',0,1.25,[(.01,.43),(.04,.45),(.12,.38),(.30,.26),(.50,.17),(.66,.14),(.85,.17),(1.04,.27),(1.23,.42),(1.27,.46),(1.30,.45)],white,96)
# Foreground low table partly seen: conditional box dimensions, no invented drawers.
cube('TABLE_low_top',(-2.9,-1.0,.42),(2.3,1.25,.09),wood,.045)
for x in [-3.87,-1.93]:
 for y in [-1.48,-.52]:cube('TABLE_leg',(x,y,.2),(.06,.06,.4),wood)
# Distant skyline is a clearly inferred low-detail context, not matching source assets.
for k,(x,w,h,yy) in enumerate([(-7,1.4,8,12),(-5,1.8,7,13),(-2.8,1.4,10,14),(-.8,1.8,7.8,12),(2.0,1.8,10,14),(4.5,1.4,6,12),(6.7,1.8,9,13)]):
 cube(f'CONTEXT_city_mass_{k}',(x,yy,h/2-1),(w,.9,h),black,role='Inferred skyline proxy; not source reconstruction or scale evidence')
 emit=material(f'CONTEXT_windowlights{k}',(.4,.32,.13),emission=1.8)
 for row in range(5,22):
  for col in range(4):
   if (row*13+col*7+k)%4==0:continue
   xx=x-w*.36+col*w*.24;zz=-1+row*h/24;cube(f'CONTEXT_citylight_{k}_{row}_{col}',(xx,yy-.46,zz),(.045,.015,.035),emit,role='Inferred distant texture surrogate, not measured windows')
# Fixed light state shared by all source and inspection cameras.
def light(n,loc,energy,color,size,target):
 l=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();l.energy=energy;l.color=color;l.shape='DISK';l.size=size
light('KEY_fixed',(0,1.0,4.8),500,(.85,.75,1),1.6,(0,1,0))
light('FILL_fixed',(0,-4,3.8),330,(.72,.65,.8),7,(0,2,1.5))
light('LAMP_fixed',(-5.45,2.8,2.7),75,(1,.6,.3),.5,(-3.8,2,1))
def camera(n,loc,target,lens):
 c=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,c);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_start=.02;c.clip_end=200;return o
camera('SOURCE_A',(0,-6.2,2.1),(0,2.1,1.75),24)
camera('SOURCE_B',(.1,-3.7,1.8),(0,2.0,1.65),26)
camera('SOURCE_C',(.1,-3.7,3.8),(0,2.0,1.25),25)
views=[((-5.5,-5.7,2.5),(0,2,1.5)),((5.5,-5.7,2.5),(0,2,1.5)),((-5.7,.0,2.5),(1,2,1.5)),((5.7,.0,2.5),(-1,2,1.5)),((-4,4.3,2.9),(0,0,1.2)),((4,4.3,2.9),(0,0,1.2)),((0,-2,4.9),(0,2,.5)),((0,3.7,4.9),(0,-.5,.5))]
for i,(p,t) in enumerate(views):camera(f'CHECK_{i+1:02}',p,t,18)
s.camera=bpy.data.objects['SOURCE_A']
(D/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R01_material.blend'))
bpy.ops.export_scene.gltf(filepath=str(D/'models/R01_material.glb'),export_format='GLB',export_apply=True)
# White model uses exactly identical mesh vertices/transforms and cameras, glass retained transparent.
for o in s.objects:
 if o.type=='MESH' and not o.name.startswith('WINDOW_glazing'):
  o.data.materials.clear();o.data.materials.append(white_mat)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R01_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(D/'models/R01_white.glb'),export_format='GLB',export_apply=True)
print('DONE R01',len([o for o in s.objects if o.type=='MESH']))
