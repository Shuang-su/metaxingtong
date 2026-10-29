"""Deterministic editable candidate. Run: blender -b -t 8 --python scripts/build_scene.py -- --stage r01
All lengths are model units. Source fit is conditional; geometry never depends on camera.
"""
import bpy, math, json, sys, hashlib, argparse
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
from math import sin, cos, pi
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('--stage',default='r07');p.add_argument('--render',default='preview',choices=['none','preview','all']);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=ROOT/'models'/args.stage; QA=ROOT/'qa'/args.stage
OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
fit_path=QA/'camera-anchor-fit.json';source_fit=json.loads(fit_path.read_text()) if fit_path.exists() else None
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.unit_settings.system='NONE';sc['status']='conditional reconstruction candidate; source review pending; no user acceptance';sc['units']='relative model units; no measured scale';sc['source_state']='single approximate sunset material and light state, shared by every camera'
sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=32;sc.cycles.samples=48;sc.cycles.use_denoising=False
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
sc.world=bpy.data.worlds.new('Approximate sunset environment');sc.world.use_nodes=True
n=sc.world.node_tree.nodes; l=sc.world.node_tree.links;n.clear()
out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.45
tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');ramp=n.new('ShaderNodeValToRGB')
l.new(tex.outputs['Normal'],sep.inputs[0]);zneg=n.new('ShaderNodeMath');zneg.operation='MULTIPLY';zneg.inputs[1].default_value=-1;l.new(sep.outputs['Z'],zneg.inputs[0]);l.new(zneg.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],bg.inputs['Color']);l.new(bg.outputs[0],out.inputs[0])
ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(.42,.22,.24,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.025,.055,.13,1)
def mat(name,color,metal=0,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
 if emission:s.inputs['Emission Color'].default_value=(*color,1);s.inputs['Emission Strength'].default_value=emission
 return m
ivory=mat('Piano ivory lacquer - approximate',(.78,.75,.68),.08,.27); ivoryedge=mat('Ivory edge',(.62,.57,.48),.1,.31)
black=mat('Key black',(.012,.009,.008),0,.3);whitekey=mat('Key ivory',(.91,.90,.83),0,.24);gold=mat('Brass hardware',(.48,.31,.10),.72,.3)
inner=mat('Soundboard ochre',(.32,.16,.065),0,.52);dark=mat('Dark structural metal',(.025,.022,.019),.45,.4)
linen=mat('Bench upholstery',(.68,.63,.59),0,.73);paper=mat('Unmarked score paper',(.82,.79,.70),0,.8)
wood=mat('Weathered deck timber',(.20,.105,.052),0,.8);sand=mat('Sand approximation',(.25,.18,.13),0,.9)
boatmat=mat('Near boat dark hull',(.02,.024,.029),.23,.24);boatwood=mat('Boat gunwale wood',(.22,.075,.035),0,.4)
water=mat('Sea approximation',(.075,.10,.16),.42,.22);glow=mat('Lantern warm insert',(.98,.35,.04),0,.5,5)
weave=mat('Chair basket weave',(.09,.052,.025),0,.9);sailmat=mat('Distant sail cloth',(.43,.35,.32),0,.9)
# Image texture is generated locally, not sampled or disguised as source imagery.
if (ROOT/'textures/deck_color.png').exists():
 nt=wood.node_tree;bs=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(ROOT/'textures/deck_color.png'));nt.links.new(tc.outputs['UV'],im.inputs[0]);nt.links.new(im.outputs[0],bs.inputs['Base Color'])
 im2=nt.nodes.new('ShaderNodeTexImage');im2.image=bpy.data.images.load(str(ROOT/'textures/deck_roughness.png'));im2.image.colorspace_settings.name='Non-Color';nt.links.new(tc.outputs['UV'],im2.inputs[0]);nt.links.new(im2.outputs[0],bs.inputs['Roughness'])
# Sand and water use portable uniform PBR; procedural bumps removed for GLB parity.
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
poly=[(-.78,0),(.78,0),(.78,.54),(.765,.85),(.70,1.10),(.58,1.35),(.45,1.62),(.36,1.90),(.24,2.16),(.02,2.34),(-.26,2.40),(-.48,2.40),(-.66,2.29),(-.77,2.09),(-.78,1.8)]
# Catmull-Rom perimeter is subsequently clipped at the real keyboard opening.
def smooth_poly(points):
 out=[]
 for i in range(len(points)):
  a=Vector(points[(i-1)%len(points)]);b=Vector(points[i]);c=Vector(points[(i+1)%len(points)]);d=Vector(points[(i+2)%len(points)])
  for k in range(6):
   t=k/6;v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);out.append(tuple(v))
 return out
# Body is a closed bottom with inner cavity and true rim, not a filled box.
poly=smooth_poly(poly)
# Preserve straight front sidewalls; the old closed spline overshot these edges.
poly=[(max(-.78,min(.78,x)),max(0,y)) for x,y in poly]
changed=True
while changed:
 changed=False;keep=[]
 for i,b in enumerate(poly):
  a=poly[i-1];c=poly[(i+1)%len(poly)];cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
  if abs(cross)<1e-9:changed=True
  else:keep.append(b)
 poly=keep
N=len(poly);inside=[(x*.93,(y-1.2)*.95+1.2) for x,y in poly]
vs=[]
for pxy,z in [(poly,.70),(poly,1.19),(inside,1.19),(inside,.91)]:vs.extend([(x,y,z) for x,y in pxy])
fs=[]
for j in range(N):
 k=(j+1)%N;fs += [(j,k,N+k,N+j),(N+j,N+k,2*N+k,2*N+j),(2*N+j,2*N+k,3*N+k,3*N+j)]
fs += [tuple(range(N-1,-1,-1)),tuple(range(3*N,4*N))]
body=mesh('P01 grand piano curved rim and bottom',vs,fs,ivory,'P01_body')
for f in body.data.polygons:
 if abs(f.normal.z)<.5:f.use_smooth=True
# R07 removes the false tall crosswall at the keyboard opening. This is a
# permanent mesh boolean, never a render/camera visibility switch.
cutter=cube('temporary front opening',(0,-.60,1.23),(2.4,1.64,.80),None,'construction')
bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('Permanent keyboard opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
def clip_y(points,ymin):
 result=[]
 for i,a in enumerate(points):
  b=points[(i+1)%len(points)]
  if a[1]>=ymin:result.append(a)
  if (a[1]>=ymin)!=(b[1]>=ymin):
   t=(ymin-a[1])/(b[1]-a[1]);result.append((a[0]+t*(b[0]-a[0]),ymin))
 return result
prism('P01 soundboard inside rim',clip_y([(x*.90,(y-1.2)*.91+1.2) for x,y in poly],.27),.914,.935,inner,'P01_body')
# P09/P10: native N2453 reveals harp and strings; counts/lengths remain inferred.
for a,b in [((-.65,.30,1.00),(.61,.30,1.00)),((-.60,.65,1.00),(.52,.65,1.00)),((-.58,1.03,1.00),(.20,1.03,1.00)),((-.58,.31,1.01),(-.41,2.19,1.01)),((.02,.31,1.01),(-.18,2.17,1.01)),((.52,.31,1.01),(-.07,1.86,1.01))]:
 rod('P09 copper harp brace',a,b,.028,gold,'P09_harp',8)
for i in range(62):
 x=-.58+i*1.15/61;end_y=2.20-max(0,x+.20)*1.95
 rod('P10 string %02d'%i,(x,.24,.98),(x*.53-.15,end_y,.98),.0018,gold,'P10_strings',6)
 for yy in [.24,end_y]:rod('P09 tuning pin',(x if yy==.24 else x*.53-.15,yy,.967),(x if yy==.24 else x*.53-.15,yy,.995),.006,dark,'P09_harp',8)
for yy in [1.12,1.45]:
 bpy.ops.mesh.primitive_torus_add(major_radius=.068,minor_radius=.009,major_segments=24,minor_segments=8,location=(-.42,yy,.951));tag(bpy.context.object,'P09_harp',gold);bpy.context.object.name='P09 open soundboard ring'
# Lid thickness and raised edge; one transform shared across all cameras.
lid_poly=[]
for i,a in enumerate(poly):
 b=poly[(i+1)%len(poly)]
 if a[1]>=.38:lid_poly.append(a)
 if (a[1]>=.38)!=(b[1]>=.38):
  t=(.38-a[1])/(b[1]-a[1]);lid_poly.append((a[0]+t*(b[0]-a[0]),.38))
lid=prism('P02 raised lid',lid_poly,0,.045,ivory,'P02_lid');hinge=Vector((-.78,0,1.21));tilt=math.radians(source_fit['common_lid_angle_degrees'] if source_fit else 31)
R=Matrix.Rotation(-tilt,4,'Y');lid.matrix_world=Matrix.Translation(hinge)@R@Matrix.Translation((.78,0,0))
def lid_pt(x,y,z):return lid.matrix_world@Vector((x,y,z))
a=lid_pt(.73,.42,.045);b=lid_pt(-.75,.42,.045);rod('P02 lid front reinforcement',a,b,.024,ivoryedge,'P02_lid',8)
rod('P03 lid support',(.760,.55,1.185),lid_pt(.62,.55,0),.014,gold,'P03_prop')
# Small inferred seat connects the prop to the observed rim; contact is explicit.
cube('P03 prop foot seat',(.760,.55,1.18),(.055,.065,.028),gold,'P03_prop',.004)
rod('P02 hinge',(-.78,.1,1.2),(-.78,2,1.2),.012,gold,'P02_lid')
# R07 continuous cheek and fallboard profiles; all dimensions remain inferred.
def bezier2(a,b,c,d,steps=32):
 return [tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in range(2)) for t in [i/steps for i in range(steps+1)]]
def profile_x(name,profile,x0,x1,material,evidence,bevel=0):
 nn=len(profile);vs=[(x,y,z) for x in (x0,x1) for y,z in profile]
 fs=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
 o=mesh(name,vs,fs,material,evidence)
 for f in list(o.data.polygons)[2:]:f.use_smooth=True
 if bevel:
  m=o.modifiers.new('Profile edge radius','BEVEL');m.width=bevel;m.segments=3
 return o
cube('P04 keybed lower step',(0,-.16,.714),(1.60,.67,.108),ivory,'P04_keys',.009)
cube('P04 keybed front molding',(0,-.485,.748),(1.58,.045,.035),ivoryedge,'P04_keys',.006)
cube('P04 keybed front upper ledge',(0,-.444,.773),(1.53,.055,.021),ivory,'P04_keys',.004)
# Concave open fallboard transitions from the keys to the vertical rear face.
fallcurve=bezier2((-.077,.824),(.105,.824),(.158,.925),(.158,1.165),40)
fallprofile=fallcurve+[(.200,1.165),(.200,.805),(-.077,.805)]
profile_x('P04 curved inner fallboard',fallprofile,-.702,.702,ivory,'P04_keys',.003)
cube('P04 projecting upper trim',(0,.088,1.167),(1.52,.205,.029),ivory,'P04_keys',.005)
cube('P04 trim lower bead',(0,.127,1.142),(1.46,.102,.018),ivoryedge,'P04_keys',.004)
for sx in [-1,1]:
 # Broad concave curve seen in N2518 and N6766, with an extruded cheek cap.
 arc=bezier2((.184,1.225),(.184,.970),(.025,.852),(-.270,.852),48)
 nose=bezier2((-.400,.852),(-.455,.852),(-.480,.830),(-.480,.773),12)
 profile=[(-.480,.660),(.300,.660),(.300,1.225)]+arc+nose+[(-.480,.700)]
 o=profile_x('P04 continuous cheek '+str(sx),profile,sx*.741-.039,sx*.741+.039,ivory,'P04_keys',.004)
 o['shape_evidence']='N2518 / N6766 / N6318: broad concave cheek; hidden join and dimensions inferred'
 # Real mesh union removes coincident internal faces at the cheek/rim junction.
 bpy.context.view_layer.objects.active=body
 join=body.modifiers.new('Permanent cheek to rim joint','BOOLEAN');join.operation='UNION';join.solver='EXACT';join.object=o
 bpy.ops.object.modifier_apply(modifier=join.name);bpy.data.objects.remove(o,do_unlink=True)
body['evidence_id']='P01_body P04_keys';body['shape_evidence']='N2518 / N6766: continuous concave cheeks fused to shared rim; inferred dimensions'
kw=1.38/52
for i in range(52):
 x=-.69+(i+.5)*kw;cube(f'P04 white key {i+1:02}',(x,-.243,.798),(kw*.95,.36,.028),whitekey,'P04_keys',.002)
 if i<51 and i%7 in [0,2,3,5,6]:cube(f'P04 black key {i+1:02}',(x+kw*.5,-.164,.831),(kw*.60,.19,.039),black,'P04_keys',.002)
# Music desk at keyboard rear. No fabricated notation.
desk=cube('P05 music desk',(0,.23,1.39),(.66,.035,.37),ivoryedge,'P05_music',.01);desk.rotation_euler.x=math.radians(-13)
for i in [-1,1]:
 page=cube('P05 blank score page '+str(i),(i*.155,.195,1.405),(.30,.008,.34),paper,'P05_music');page.rotation_euler.x=math.radians(-13);page.rotation_euler.z=i*.045
cube('P05 music desk ledge',(0,.14,1.215),(.72,.12,.025),ivory,'P05_music',.006)
# Three leg load paths. Third leg and lower structure inferred where obscured.
legs=[(-.61,.18,'P07_leg_front'),(.61,.18,'P07_leg_front'),(-.31,2.08,'P06_leg_tail')]
for ix,(x,y,id) in enumerate(legs):
 tapered('leg '+str(ix),(x,y),.11,.69,.055,.095,ivory,id);cube('leg shoulder '+str(ix),(x,y,.68),(.26,.24,.12),ivory,id,.02)
 rod('leg caster axle '+str(ix),(x-.065,y,.075),(x+.065,y,.075),.02,gold,id)
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.075,depth=.045,location=(x,y,.075),rotation=(0,pi/2,0));tag(bpy.context.object,id,gold);bpy.context.object.name='caster '+str(ix)
# Pedal lyre / rods are explicitly approximate.
for x in [-.12,.12]:rod('P08 pedal lyre', (x,-.02,.2),(x,.06,.80),.018,ivory,'P08_pedal')
cube('P08 pedal block',(0,-.10,.17),(.36,.15,.11),ivoryedge,'P08_pedal',.012)
for x in [-.10,0,.10]:cube('P08 brass pedal',(x,-.23,.13),(.065,.21,.025),gold,'P08_pedal',.018)
for x,y,id in legs[:2]:rod('P08 support diagonal',(x,y,.16),(0,.42,.78),.01,dark,'P08_pedal')
# R07 thick cushion with rounded plan and closed curved sidewall, no normal-map fake.
bx,by=0,-1.02
cube('B01 bench wooden frame',(bx,by,.43),(1.02,.42,.12),ivoryedge,'B01_bench',.02)
for x in [-.42,.42]:
 for y in [-.16,.16]:tapered('B01 bench leg',(bx+x,by+y),0,.4,.035,.045,ivory,'B01_bench')
NX,NY=100,56;verts=[]
buttons=[(-.36+i*.18,-.13+j*.13) for i in range(5) for j in range(3)]
def cushion_xy(u,v):return (.55*u*(1-.065*abs(v)**8),.267*v*(1-.12*abs(u)**8))
def cushion_z(x,y,u,v):
 dip=sum(.038*math.exp(-((x-a)**2+(y-b)**2)/.00075) for a,b in buttons)
 return .565+.067*(1-abs(u)**8)*(1-abs(v)**8)-dip
for j in range(NY+1):
 v=-1+2*j/NY
 for i in range(NX+1):
  u=-1+2*i/NX;x,y=cushion_xy(u,v);verts.append((bx+x,by+y,cushion_z(x,y,u,v)))
faces=[]
for j in range(NY):
 for i in range(NX):a=j*(NX+1)+i;faces.append((a,a+1,a+NX+2,a+NX+1))
bound=list(range(NX+1))+[j*(NX+1)+NX for j in range(1,NY+1)]+[NY*(NX+1)+i for i in range(NX-1,-1,-1)]+[j*(NX+1) for j in range(NY-1,0,-1)]
last=bound
for z,scale in [(.545,1.010),(.515,1.003),(.490,.976),(.480,.940)]:
 ring=[]
 for q in bound:
  x,y,_=verts[q];ring.append(len(verts));verts.append((bx+(x-bx)*scale,by+(y-by)*scale,z))
 for i in range(len(ring)):j=(i+1)%len(ring);faces.append((last[i],ring[i],ring[j],last[j]))
 last=ring
bottom_center=len(verts);verts.append((bx,by,.480))
for i in range(len(last)):faces.append((last[i],bottom_center,last[(i+1)%len(last)]))
cushion=mesh('B01 rounded tufted cushion',verts,faces,linen,'B01_bench')
for f in cushion.data.polygons:f.use_smooth=True
cushion['shape_evidence']='N4037 / N6318: thick soft rounded cushion with dimples; exact count / underside inferred'
for i,(x,y) in enumerate(buttons):
 z=cushion_z(x,y,x/.55,y/.267)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(bx+x,by+y,z+.003));o=bpy.context.object;o.name='B01 recessed fabric button %02d'%i;o.scale=(.012,.012,.004);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);tag(o,'B01_bench',linen)
 for f in o.data.polygons:f.use_smooth=True
# Deck: a finite working patch; boundary is not an observed pier outline.
for i in range(23):cube(f'D01 deck plank {i:02}',(0,-2+i*.255,-.07),(7.4,.244,.14),wood,'D01_deck',.006)
for y in [-1.9,.5,3.45]:cube('D01 inferred joist',(0,y,-.24),(7.1,.14,.20),wood,'D01_deck')
# finite sand patch behind deck. Simplified visible margin; no invented building.
cube('S01 local sand patch',(6.2,0,-.24),(5.1,16,.32),sand,'S01_sand',.04)
cube('E01 water environment',(0,0,-.46),(1000,1000,.08),water,'E01_sea')
# Lanterns, open frames with solid warm inserts; not source photometric calibration.
def lantern(id,loc,size):
 x,y,z=loc;s=size
 cube(id+' base',(x,y,z+.025),(s*1.12,s*1.12,.05),dark,id,.006)
 cube(id+' light insert',(x,y,z+s*.52),(s*.78,s*.78,s*.94),glow,id,.009)
 for dx in [-.5,.5]:
  for dy in [-.5,.5]:rod(id+' upright',(x+dx*s,y+dy*s,z+.04),(x+dx*s,y+dy*s,z+s),.009,dark,id)
 cube(id+' top',(x,y,z+s),(s,s,.025),dark,id,.005)
 bpy.ops.object.light_add(type='POINT',location=(x,y,z+s*.55));bpy.context.object.data.energy=18*s/.25;bpy.context.object.data.color=(1,.32,.055);bpy.context.object.data.shadow_soft_size=s*.4
lantern('L01_lantern',(-.92,1.22,0),.25);lantern('L02_lantern',(7.2,-5.5,-.08),.27)
# Woven chair, true open weave and separate supporting frame.
cx,cy=7.2,-4.1
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
kx,ky=7,-3.1
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
hull('V01_boat',(10.4,3.7,-.34),2.4,1.0)
cube('V01 inferred seat',(10.4,3.7,-.12),(.87,.25,.08),boatwood,'V01_boat')
rod('V01 windshield bar',(9.97,3.93,.07),(10.83,3.93,.07),.015,dark,'V01_boat')
# Far boat distance / scale not identified by a single image.
vx,vy,vz=40,-4,-.34;hull('V02_sailboat',(vx,vy,vz),2.5,.8)
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
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.data.lens=lens;o.data.clip_end=1000;aim(o,target);o['role']='inspection' if name.startswith(('check','detail')) else 'conditional source camera fit';return o
cams={}
cams['source_N6318']=camera('source_N6318',(-5.9,-2.1,1.2),(.05,.75,1.55),48)
cams['source_N4037']=camera('source_N4037',(-4.5,1.6,2.1),(-.1,0,1.22),50)
cams['source_N2518']=camera('source_N2518',(1.12,-1.12,1.21),(-.04,-.05,.87),44)
cams['source_N2453']=camera('source_N2453',(3.8,4.0,3.3),(-.4,.95,1.0),58)
cams['source_N6766']=camera('source_N6766',(1.2,-1.1,.65),(.1,-.05,1.0),35)
cams['detail_cheek_right']=camera('detail_cheek_right',(2.2,-2.8,1.6),(0,-.05,.96),58)
cams['detail_cheek_left']=camera('detail_cheek_left',(-2.2,-2.8,1.6),(0,-.05,.96),58)
cams['detail_bench']=camera('detail_bench',(1.6,-2.8,1.45),(0,-1.02,.48),62)
cams['main']=camera('main',(-5.2,-6.4,4.1),(0,1,.65),45)
for i in range(8):
 a=2*pi*i/8;cams['check_%02d'%i]=camera('check_%02d'%i,(7.5*cos(a),.8+7.5*sin(a),4.1 if i%2 else 3),(0,.8,.6),42)
cams['check_top']=camera('check_top',(0,1,9),(0,1,0),38)
# Camera parameters never change mesh/material/light state.
if source_fit:
 for name,p in source_fit['cameras'].items():
  o=cams['source_'+name];o.location=p['location'];q=(Vector(p['target'])-o.location).to_track_quat('-Z','Y');o.rotation_euler=(q@Quaternion((0,0,1),p['roll_rad'])).to_euler();o.data.lens=p['lens_mm']
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
 keys=['source_N6318','source_N4037','source_N2518','source_N2453','source_N6766'] if args.render=='preview' else list(cams)
 for name in keys:
  sc.camera=cams[name];sc.render.resolution_x=960 if args.render=='preview' or name.startswith('check') else 1920;sc.render.resolution_y=540 if args.render=='preview' or name.startswith('check') else 1080;sc.render.filepath=str(QA/(name+'.png'));bpy.ops.render.render(write_still=True)
(QA/'build-summary.json').write_text(json.dumps({'stage':args.stage,'blender_version':bpy.app.version_string,'mesh_objects':len(objects),'common_geometry_for_all_cameras':True,'units':'model units','material_and_white_share_geometry':True,'native_source_alignment':'conditional manual perspective fit, not calibrated','status':'candidate, source review pending'},indent=2)+'\n')
print('BUILD_COMPLETE',len(objects))
