"""Deterministic editable candidate. Run: blender -b -t 8 --python scripts/build_scene.py -- --stage r01
All lengths are model units. Source fit is conditional; geometry never depends on camera.
"""
import bpy, math, json, sys, hashlib, argparse
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('--stage',default='r01');p.add_argument('--render',default='preview',choices=['none','preview','all']);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=ROOT/'models'/args.stage; QA=ROOT/'qa'/args.stage
OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.unit_settings.system='NONE';sc['status']='conditional reconstruction candidate; source review pending; no user acceptance';sc['units']='relative model units; no measured scale';sc['source_state']='single approximate sunset material and light state, shared by every camera'
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=False
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
sc.world=bpy.data.worlds.new('Approximate sunset environment');sc.world.use_nodes=True
n=sc.world.node_tree.nodes; l=sc.world.node_tree.links;n.clear()
out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.45
tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');ramp=n.new('ShaderNodeValToRGB')
l.new(tex.outputs['Normal'],sep.inputs[0]);l.new(sep.outputs['Z'],ramp.inputs[0]);l.new(ramp.outputs[0],bg.inputs['Color']);l.new(bg.outputs[0],out.inputs[0])
ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(.42,.22,.24,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.025,.055,.13,1)
def mat(name,color,metal=0,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
 if emission:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emission
 return m
ivory=mat('Piano ivory lacquer - approximate',(.78,.75,.68),.08,.27); ivoryedge=mat('Ivory edge',(.62,.57,.48),.1,.31)
black=mat('Key black',(.012,.009,.008),0,.3);whitekey=mat('Key ivory',(.91,.90,.83),0,.24);gold=mat('Brass hardware',(.48,.31,.10),.72,.3)
inner=mat('Soundboard ochre',(.32,.16,.065),0,.52);dark=mat('Dark structural metal',(.025,.022,.019),.45,.4)
linen=mat('Bench upholstery',(.53,.49,.47),0,.65);paper=mat('Unmarked score paper',(.82,.79,.70),0,.8)
wood=mat('Weathered deck timber',(.20,.105,.052),0,.8);sand=mat('Sand approximation',(.25,.18,.13),0,.9)
boatmat=mat('Near boat dark hull',(.02,.024,.029),.23,.24);boatwood=mat('Boat gunwale wood',(.22,.075,.035),0,.4)
water=mat('Sea approximation',(.075,.10,.16),.42,.22);glow=mat('Lantern warm insert',(.98,.35,.04),0,.5,5)
weave=mat('Chair basket weave',(.09,.052,.025),0,.9);sailmat=mat('Distant sail cloth',(.43,.35,.32),0,.9)
# Image texture is generated locally, not sampled or disguised as source imagery.
if (ROOT/'textures/deck_color.png').exists():
 nt=wood.node_tree;bs=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(ROOT/'textures/deck_color.png'));nt.links.new(tc.outputs['Generated'],im.inputs[0]);nt.links.new(im.outputs[0],bs.inputs['Base Color'])
 im2=nt.nodes.new('ShaderNodeTexImage');im2.image=bpy.data.images.load(str(ROOT/'textures/deck_roughness.png'));im2.image.colorspace_settings.name='Non-Color';nt.links.new(tc.outputs['Generated'],im2.inputs[0]);nt.links.new(im2.outputs[0],bs.inputs['Roughness'])
for m,scale,strength in [(sand,8,.16),(water,1.1,.13)]:
 nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.06;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
# Stable IDs and epistemic status are on every geometry object.
def tag(o,id,material,status='inferred dimensions; observed object class'):
 o['evidence_id']=id;o['evidence_status']=status;o['camera_independent']=True
 if material:o.data.materials.append(material)
 return o
def cube(name,loc,dim,ma,id,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);tag(o,id,ma)
 if bevel:mod=o.modifiers.new('Editable edge bevel','BEVEL');mod.width=bevel;mod.segments=3
 return o
def mesh(name,vs,fs,ma,id):
 me=bpy.data.meshes.new(name+' mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);tag(o,id,ma)
 # Recalculate winding for each closed shell.
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();return o
def rod(name,a,b,r,ma,id,verts=12):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return tag(o,id,ma)
def prism(name,poly,z0,z1,ma,id):
 N=len(poly);vs=[(x,y,z) for z in (z0,z1) for x,y in poly];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(name,vs,fs,ma,id)
def tapered(name,xy,z0,z1,r0,r1,ma,id):
 x,y=xy;poly=[(-1,-1),(1,-1),(1,1),(-1,1)];vs=[(x+a*r,y+b*r,z) for z,r in [(z0,r0),(z1,r1)] for a,b in poly];return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,id)
# Piano origin: keyboard at y=0; tail +Y; width X. No real scale claimed.
# Rounded grand footprint is a cubic sampled perimeter with explicit thickness.
poly=[(-.78,0),(.78,0),(.78,.54),(.74,.85),(.61,1.05),(.39,1.19),(.22,1.39),(.18,1.71),(.12,2.04),(-.03,2.27),(-.26,2.40),(-.48,2.40),(-.66,2.29),(-.77,2.09),(-.78,1.8)]
# Catmull-Rom interpolation retains a flat keyboard rim; smoothed tail only.
def smooth_poly(points):
 out=[]
 for i in range(len(points)):
  a=Vector(points[(i-1)%len(points)]);b=Vector(points[i]);c=Vector(points[(i+1)%len(points)]);d=Vector(points[(i+2)%len(points)])
  for k in range(6):
   t=k/6;v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);out.append(tuple(v))
 return out
# Body is a closed bottom with inner cavity and true rim, not a filled box.
poly=smooth_poly(poly);N=len(poly);inside=[(x*.93,(y-1.2)*.95+1.2) for x,y in poly]
vs=[]
for pxy,z in [(poly,.83),(poly,1.19),(inside,1.19),(inside,.91)]:vs.extend([(x,y,z) for x,y in pxy])
fs=[]
for j in range(N):
 k=(j+1)%N;fs += [(j,k,N+k,N+j),(N+j,N+k,2*N+k,2*N+j),(2*N+j,2*N+k,3*N+k,3*N+j)]
fs += [tuple(range(N-1,-1,-1)),tuple(range(3*N,4*N))]
mesh('P01 grand piano curved rim and bottom',vs,fs,ivory,'P01_body')
prism('P01 soundboard inside rim',[(x*.90,(y-1.2)*.91+1.2) for x,y in poly],.914,.935,inner,'P01_body')
# Lid thickness and raised edge; one transform shared across all cameras.
lid=prism('P02 raised lid',poly,0,.045,ivory,'P02_lid');hinge=Vector((-.78,0,1.21));tilt=math.radians(31)
R=Matrix.Rotation(-tilt,4,'Y');lid.matrix_world=Matrix.Translation(hinge)@R@Matrix.Translation((.78,0,0))
def lid_pt(x,y,z):return lid.matrix_world@Vector((x,y,z))
a=lid_pt(.68,.2,.045);b=lid_pt(-.65,.2,.045);rod('P02 lid front reinforcement',a,b,.024,ivoryedge,'P02_lid',8)
rod('P03 lid support',(.55,.62,1.02),lid_pt(.62,.62,0),.014,gold,'P03_prop')
rod('P02 hinge',(-.78,.1,1.2),(-.78,2,1.2),.012,gold,'P02_lid')
# Keyboard and cheeks.
cube('P04 keybed', (0,-.19,.82),(1.56,.43,.12),ivory,'P04_keys',.025)
cube('P04 fallboard',(0,.015,1.04),(1.44,.055,.26),ivory,'P04_keys',.015)
for sx in [-1,1]:
 # Explicit curved-looking cheek made with profile, extruded in X.
 profile=[(-.40,.80),(.10,.80),(.10,1.19),(.02,1.19),(-.01,1.08),(-.08,.98),(-.20,.92),(-.4,.92)];vs=[(sx*.73+dx,y,z) for dx in [-.045,.045] for y,z in profile];nn=len(profile);fs=[tuple(range(nn-1,-1,-1)),tuple(range(nn,nn*2))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)];mesh('P04 cheek '+str(sx),vs,fs,ivory,'P04_keys')
kw=1.38/52
for i in range(52):
 x=-.69+(i+.5)*kw;cube(f'P04 white key {i+1:02}',(x,-.21,.898),(kw*.95,.32,.028),whitekey,'P04_keys',.002)
 # Conventional 88-key pattern is explicitly inferred.
 if i<51 and i%7 in [0,2,3,5,6]:cube(f'P04 black key {i+1:02}',(x+kw*.5,-.132,.929),(kw*.60,.17,.035),black,'P04_keys',.002)
# Music desk at keyboard rear. No fabricated notation.
desk=cube('P05 music desk',(0,.23,1.39),(.66,.035,.37),ivoryedge,'P05_music',.01);desk.rotation_euler.x=math.radians(-13)
for i in [-1,1]:
 page=cube('P05 blank score page '+str(i),(i*.155,.195,1.405),(.30,.008,.34),paper,'P05_music');page.rotation_euler.x=math.radians(-13);page.rotation_euler.z=i*.045
cube('P05 music desk ledge',(0,.14,1.215),(.72,.12,.025),ivory,'P05_music',.006)
# Three leg load paths. Third leg and lower structure inferred where obscured.
legs=[(-.61,.18,'P07_leg_front'),(.61,.18,'P07_leg_front'),(-.31,2.08,'P06_leg_tail')]
for ix,(x,y,id) in enumerate(legs):
 tapered('leg '+str(ix),(x,y),.11,.82,.055,.095,ivory,id);cube('leg shoulder '+str(ix),(x,y,.80),(.26,.24,.12),ivory,id,.02)
 rod('leg caster axle '+str(ix),(x-.065,y,.075),(x+.065,y,.075),.02,gold,id)
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.075,depth=.045,location=(x,y,.075),rotation=(0,pi/2,0));tag(bpy.context.object,id,gold);bpy.context.object.name='caster '+str(ix)
# Pedal lyre / rods are explicitly approximate.
for x in [-.12,.12]:rod('P08 pedal lyre', (x,-.02,.2),(x,.06,.80),.018,ivory,'P08_pedal')
cube('P08 pedal block',(0,-.10,.17),(.36,.15,.11),ivoryedge,'P08_pedal',.012)
for x in [-.10,0,.10]:cube('P08 brass pedal',(x,-.23,.13),(.065,.21,.025),gold,'P08_pedal',.018)
for x,y,id in legs[:2]:rod('P08 support diagonal',(x,y,.16),(0,.42,.78),.01,dark,'P08_pedal')
# Bench cushion with shallow modeled button depressions (grid surface and closed base).
bx,by=0,-1.02
cube('B01 bench wooden frame',(bx,by,.43),(1.02,.42,.12),ivoryedge,'B01_bench',.02)
for x in [-.42,.42]:
 for y in [-.16,.16]:tapered('B01 bench leg',(bx+x,by+y),0,.4,.035,.045,ivory,'B01_bench')
NX,NY=50,24;verts=[]
buttons=[(-.36+i*.18,-.13+j*.13) for i in range(5) for j in range(3)]
for j in range(NY+1):
 y=-.24+.48*j/NY
 for i in range(NX+1):
  x=-.54+1.08*i/NX;edge=min((.54-abs(x))/.06,(.24-abs(y))/.06,1);dip=sum(.018*math.exp(-((x-u)**2+(y-v)**2)/.0006) for u,v in buttons);verts.append((bx+x,by+y,.51+.055*max(0,edge)-dip))
faces=[]
for j in range(NY):
 for i in range(NX):a=j*(NX+1)+i;faces.append((a,a+1,a+NX+2,a+NX+1))
bound=[i for i in range(NX+1)]+[j*(NX+1)+NX for j in range(1,NY+1)]+[NY*(NX+1)+i for i in range(NX-1,-1,-1)]+[j*(NX+1) for j in range(NY-1,0,-1)]
base_idx=[]
for i in bound:base_idx.append(len(verts));verts.append((verts[i][0],verts[i][1],.49))
for i in range(len(bound)):j=(i+1)%len(bound);faces.append((bound[i],base_idx[i],base_idx[j],bound[j]))
faces.append(tuple(reversed(base_idx)));mesh('B01 tufted cushion',verts,faces,linen,'B01_bench')
# Deck: a finite working patch; boundary is not an observed pier outline.
for i in range(23):cube(f'D01 deck plank {i:02}',(0,-2+i*.255,-.07),(7.4,.244,.14),wood,'D01_deck',.006)
for y in [-1.9,.5,3.45]:cube('D01 inferred joist',(0,y,-.24),(7.1,.14,.20),wood,'D01_deck')
# finite sand patch behind deck. Simplified visible margin; no invented building.
cube('S01 local sand patch',(0,6.2,-.24),(16,5.1,.32),sand,'S01_sand',.04)
cube('E01 water environment',(0,130,-.46),(500,250,.08),water,'E01_sea')
# Lanterns, open frames with solid warm inserts; not source photometric calibration.
def lantern(id,loc,size):
 x,y,z=loc;s=size
 cube(id+' base',(x,y,z+.025),(s*1.12,s*1.12,.05),dark,id,.006)
 cube(id+' light insert',(x,y,z+s*.52),(s*.78,s*.78,s*.94),glow,id,.009)
 for dx in [-.5,.5]:
  for dy in [-.5,.5]:rod(id+' upright',(x+dx*s,y+dy*s,z+.04),(x+dx*s,y+dy*s,z+s),.009,dark,id)
 cube(id+' top',(x,y,z+s),(s,s,.025),dark,id,.005)
 bpy.ops.object.light_add(type='POINT',location=(x,y,z+s*.55));bpy.context.object.data.energy=18*s/.25;bpy.context.object.data.color=(1,.32,.055);bpy.context.object.data.shadow_soft_size=s*.4
lantern('L01_lantern',(.92,1.22,0),.25);lantern('L02_lantern',(-3.6,5.45,-.08),.27)
# Woven chair, true open weave and separate supporting frame.
cx,cy=-2.45,5.55
for sx in [-1,1]:
 for sy in [-1,1]:rod('C01 chair leg',(cx+sx*.30,cy+sy*.26,-.08),(cx+sx*.25,cy+sy*.22,.45),.022,dark,'C01_chair')
 rod('C01 back upright',(cx+sx*.25,cy+.22,.4),(cx+sx*.27,cy+.32,.88),.018,dark,'C01_chair')
 rod('C01 arm',(cx+sx*.27,cy-.26,.65),(cx+sx*.27,cy+.30,.72),.022,dark,'C01_chair')
 rod('C01 arm support',(cx+sx*.27,cy-.23,.42),(cx+sx*.27,cy-.26,.65),.016,dark,'C01_chair')
rod('C01 back top',(cx-.27,cy+.32,.88),(cx+.27,cy+.32,.88),.02,dark,'C01_chair')
for i in range(17):
 x=cx-.25+i*.5/16;rod('C01 seat weave X',(x,cy-.23,.44),(x,cy+.23,.44),.007,weave,'C01_chair',6);rod('C01 back weave X',(x,cy+.22,.46),(x,cy+.32,.86),.007,weave,'C01_chair',6)
for i in range(14):
 y=cy-.23+i*.46/13;rod('C01 seat weave Y',(cx-.25,y,.45),(cx+.25,y,.45),.007,weave,'C01_chair',6)
 z=.46+i*.40/13;y=cy+.22+(z-.46)*.25;rod('C01 back weave Y',(cx-.25,y+.006,z),(cx+.25,y+.006,z),.007,weave,'C01_chair',6)
# Low open basket with visible spaced slats, not a painted black hole.
kx,ky=-1.65,5.1
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.15,depth=.025,location=(kx,ky,-.065));tag(bpy.context.object,'K01_basket',weave)
for i in range(24):
 a=i*2*pi/24;rod('K01 basket upright',(kx+.15*cos(a),ky+.15*sin(a),-.06),(kx+.19*cos(a),ky+.19*sin(a),.20),.009,weave,'K01_basket',6)
for z in [.0,.10,.20]:
 r=.15+(z+.06)/.26*.04
 for i in range(24):a=i*2*pi/24;b=(i+1)*2*pi/24;rod('K01 basket ring',(kx+r*cos(a),ky+r*sin(a),z),(kx+r*cos(b),ky+r*sin(b),z),.008,weave,'K01_basket',6)
# Near boat and distant sailboat remain distinct IDs.
def hull(id,center,length,width):
 x,y,z=center;N=32;outer=[];innerloop=[]
 for i in range(N):
  a=2*pi*i/N;xx=cos(a)*width*.5*(.80+.20*sin(a));yy=sin(a)*length*.5;outer.append((xx,yy));innerloop.append((xx*.87,yy*.92))
 vs=[]
 for loop,zz,scale in [(outer,z+.16,1),(outer,z-.15,.48),(innerloop,z+.16,1),(innerloop,z-.075,.50)]:vs.extend([(x+xx*scale,y+yy*scale,zz) for xx,yy in loop])
 fs=[]
 for i in range(N):j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(i,2*N+i,2*N+j,j),(2*N+i,3*N+i,3*N+j,2*N+j)])
 fs.extend([tuple(range(2*N-1,N-1,-1)),tuple(range(3*N,4*N))]);o=mesh(id+' closed hull shell',vs,fs,boatmat,id)
 for i in range(N):j=(i+1)%N;rod(id+' gunwale',(x+outer[i][0],y+outer[i][1],z+.17),(x+outer[j][0],y+outer[j][1],z+.17),.027,boatwood,id)
 return center
hull('V01_boat',(3.7,6.4,-.34),2.4,1.0)
cube('V01 inferred seat',(3.7,6.4,-.12),(.87,.25,.08),boatwood,'V01_boat')
rod('V01 windshield bar',(3.27,6.63,.07),(4.13,6.63,.07),.015,dark,'V01_boat')
# Far boat distance / scale not identified by a single image.
vx,vy,vz=-8,35,-.34;hull('V02_sailboat',(vx,vy,vz),2.5,.8)
rod('V02 mast',(vx,vy,0),(vx,vy,3.5),.025,dark,'V02_sailboat')
prism('V02 sail',[(vx+.015,vy),(vx+.045,vy),(vx+.045,vy+1.30)],.25,.27,sailmat,'V02_sailboat')
# Replace horizontal placeholder sail with true vertical finite triangular prism.
o=bpy.data.objects.get('V02 sail');bpy.data.objects.remove(o,do_unlink=True)
mesh('V02 triangular sail',[(vx-.01,vy,.35),(vx-.01,vy,3.35),(vx-.01,vy+1.3,.35),(vx+.01,vy,.35),(vx+.01,vy,3.35),(vx+.01,vy+1.3,.35)],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],sailmat,'V02_sailboat')
# Shared lighting; environment state never switches with camera.
bpy.ops.object.light_add(type='AREA',location=(1,-4,7));key=bpy.context.object;key.name='Shared warm sky softbox';key.data.energy=800;key.data.shape='DISK';key.data.size=8;key.data.color=(1,.78,.65)
bpy.ops.object.light_add(type='AREA',location=(-4,5,5));fill=bpy.context.object;fill.name='Shared blue sea fill';fill.data.energy=1000;fill.data.size=7;fill.data.color=(.53,.65,1)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
aim(key,(0,.5,0));aim(fill,(0,.5,0))
def camera(name,loc,target,lens=50):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.data.lens=lens;o.data.clip_end=1000;aim(o,target);o['role']='inspection' if name.startswith('check') else 'conditional source camera fit';return o
cams={}
cams['source_N6318']=camera('source_N6318',(5.9,-3.6,2.15),(.05,.75,1.18),52)
cams['source_N4037']=camera('source_N4037',(4.8,.6,2.40),(-.1,.25,1.20),48)
cams['source_N2518']=camera('source_N2518',(1.12,-1.12,1.27),(-.04,-.05,1.02),44)
cams['main']=camera('main',(5.2,-6.4,4.1),(0,1,.65),45)
for i in range(8):
 a=2*pi*i/8;cams['check_%02d'%i]=camera('check_%02d'%i,(7.5*cos(a),.8+7.5*sin(a),4.1 if i%2 else 3),(0,.8,.6),42)
cams['check_top']=camera('check_top',(0,1,9),(0,1,0),38)
# Store reproducible object inventory and camera definitions before exports.
objects=[o for o in sc.objects if o.type=='MESH'];inventory=[]
for o in objects:
 inventory.append({'name':o.name,'evidence_id':o.get('evidence_id'),'evidence_status':o.get('evidence_status'),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
(QA/'object-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
(QA/'cameras.json').write_text(json.dumps({k:{'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens_mm':o.data.lens,'status':o['role']} for k,o in cams.items()},indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
sc.camera=cams['main'];sc.render.resolution_x=1600;sc.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'piano_seaside_material.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'piano_seaside_material.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True)
# White uses exactly the same objects/mesh/modifiers; materials replaced only.
original={o.name:[m for m in o.data.materials] for o in objects};white=mat('Diagnostic white',(.76,.76,.76),0,.8)
for o in objects:o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'piano_seaside_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'piano_seaside_white.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True)
for o in objects:
 o.data.materials.clear()
 for m in original[o.name]:o.data.materials.append(m)
# Exports above are complete even if an optional render fails.
if args.render!='none':
 keys=['source_N6318','source_N4037'] if args.render=='preview' else list(cams)
 for name in keys:
  sc.camera=cams[name];sc.render.resolution_x=960 if args.render=='preview' or name.startswith('check') else 1920;sc.render.resolution_y=540 if args.render=='preview' or name.startswith('check') else 1080;sc.render.filepath=str(QA/(name+'.png'));bpy.ops.render.render(write_still=True)
(QA/'build-summary.json').write_text(json.dumps({'stage':args.stage,'blender_version':bpy.app.version_string,'mesh_objects':len(objects),'common_geometry_for_all_cameras':True,'units':'model units','material_and_white_share_geometry':True,'native_source_alignment':'conditional manual perspective fit, not calibrated','status':'candidate, source review pending'},indent=2)+'\n')
print('BUILD_COMPLETE',len(objects))
