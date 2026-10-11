import bpy,math,json,random,os
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];random.seed(4122024)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection':bpy.data.collections.remove(c)
COL={}
for n in ['01_Observed_Enclosure','02_Front_Teaching_Wall','03_Bookcase_Books','04_Teacher_Desk_Podium','05_Student_Desks_Chairs','06_Window_Wall','07_Lights_Clock_Speaker','08_Small_Observed_Props','90_INFERRED_Rear_Enclosure','91_INFERRED_Exterior_Context','99_Cameras_Lighting']:
 c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c);COL[n]=c
cur='01_Observed_Enclosure'
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL[cur].objects.link(o);return o

def mat(n,c,r=.65,metal=0,tex=None):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=r;b.inputs['Metallic'].default_value=metal
 if tex:
  for k,s in [('BaseColor','Base Color'),('Roughness','Roughness'),('Normal','Normal')]:
   im=bpy.data.images.load(str(R/'textures'/(tex+'_'+k+'.png')),check_existing=True);im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im
   if k!='BaseColor':im.colorspace_settings.name='Non-Color'
   if k=='Normal':
    nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.23;m.node_tree.links.new(t.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],b.inputs[s])
   else:m.node_tree.links.new(t.outputs['Color'],b.inputs[s])
 return m
M={n:mat(n,(.5,.5,.5),tex=n) for n in ['Plaster','Ceiling','DeskOak','FloorOak','Chalkboard','Cork']}
M.update({'black':mat('Charcoal painted metal',(.025,.035,.039),.34,.3),'metal':mat('Warm grey tubular steel',(.45,.45,.39),.27,.72),'brass':mat('Aged board trim',(.38,.31,.17),.38,.5),'paper':mat('Unprinted pale paper',(.85,.86,.80),.88),'mint':mat('Pale jade notebook',(.40,.67,.58),.64),'darkwood':mat('Dark edge stained wood',(.24,.09,.028),.43),'glass':mat('Clean window glass',(.81,.91,.94),.035),'blue':mat('Desk cup blue ceramic',(.035,.14,.21),.23),'chalk':mat('Faint verified chalk motifs',(.38,.59,.47),.95),'white':mat('Chalk white',(.85,.85,.74),.76),'rubber':mat('Dark rubber feet',(.016,.018,.018),.72)})
b=M['glass'].node_tree.nodes.get('Principled BSDF');b.inputs['Transmission Weight'].default_value=1;b.inputs['IOR'].default_value=1.45
M['emission']=mat('Fluorescent diffusers',(.92,.95,.90),.4);b=M['emission'].node_tree.nodes.get('Principled BSDF');b.inputs['Emission Color'].default_value=(.95,1,.9,1);b.inputs['Emission Strength'].default_value=1.8
M['city']=mat('INFERRED distant city warm concrete',(.62,.65,.60),.9);M['cityglass']=mat('INFERRED distant muted blue glazing',(.35,.51,.54),.4);M['leaf']=mat('INFERRED sunlit foliage',(.30,.44,.12),.9);M['leaf2']=mat('INFERRED dark foliage',(.17,.32,.07),.9)
BOOKS=[mat('Book cloth %02d'%i,c,.77) for i,c in enumerate([(.11,.22,.27),(.15,.28,.31),(.30,.32,.23),(.39,.14,.11),(.14,.15,.20),(.64,.57,.37),(.41,.51,.48),(.49,.28,.32),(.19,.34,.17)])]
def uvbox(o,scale=1):
 me=o.data
 if me.uv_layers:me.uv_layers.remove(me.uv_layers[0])
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]*scale,co[axes[1]]*scale)
def finish(o,n,ma,bev=0,smooth=False):
 o.name=n;link(o);o.data.materials.append(ma)
 if bev:
  m=o.modifiers.new('Rounded real edge','BEVEL');m.width=bev;m.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 if smooth or bev:
  for p in o.data.polygons:p.use_smooth=True
  if bev:
   m=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=m.name)
 uvbox(o);o['evidence']='Observed type and visible form; metric size and unseen surfaces inferred' if not cur.startswith('9') else 'Inferred off-camera continuation or approximate exterior'
 return o
def box(n,p,d,m,bev=.003,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n,m,bev)
 if rot:o.rotation_euler=rot
 return o
def cyl(n,p,r,h,m,rot=None,vertices=16,bev=.001):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=h,location=p);o=finish(bpy.context.object,n,m,bev,True)
 if rot:o.rotation_euler=rot
 return o
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def tube(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for bp,p in zip(s.points,pts):bp.co=(*p,1)
 o=bpy.data.objects.new(n,cu);COL[cur].objects.link(o);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.data.materials.append(m);uvbox(o);return o
def frame(n,x,y,z,w,h,ma,t=.035):
 for xx in [x-w/2,x+w/2]:box(n+' vertical',(xx,y,z),(t,.045,h),ma)
 for zz in [z-h/2,z+h/2]:box(n+' horizontal',(x,y,zz),(w,.045,t),ma)
def cam(n,loc,target,lens):
 bpy.ops.object.camera_add(location=loc);o=link(bpy.context.object);o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=250;return o
def area(n,loc,target,power,size,col=(1,1,1)):
 bpy.ops.object.light_add(type='AREA',location=loc);o=link(bpy.context.object);o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col
# Coordinates: front teaching wall Y=0, room extends +Y. Window side X=-4.0.
W=8;D=8.2;H=3.35
box('Continuous wood plank floor',(0,D/2,-.065),(W,D,.13),M['FloorOak']);uvbox(bpy.context.object,.72)
box('Front pale blue plaster wall',(0,-.10,H/2),(W+.22,.20,H),M['Plaster'])
box('Right pale blue side wall',(W/2+.10,D/2,H/2),(.20,D,H),M['Plaster'])
box('Ceiling plaster slab',(0,D/2,H+.06),(W,.12+D,.12),M['Ceiling'])
for p,d in [((0,.02,.11),(W,.055,.22)),((3.985,D/2,.11),(.055,D,.22))]:box('Blue grey skirting',p,d,M['Plaster'])
box('Front ceiling perimeter beam',(0,.15,H-.29),(W,.31,.30),M['Plaster'])
box('Right ceiling perimeter beam',(3.83,D/2,H-.29),(.34,D,.30),M['Plaster'])
cur='90_INFERRED_Rear_Enclosure'
box('INFERRED rear extent plain wall',(0,D+.10,H/2),(W+.2,.20,H),M['Plaster'])
# No invented back wall posters, doors, or fittings.
cur='06_Window_Wall'
box('Observed left window sill wall',(-4.08,D/2,.45),(.18,D,.9),M['Plaster'])
box('Observed left window upper spandrel',(-4.08,D/2,3.2),(.18,D,.30),M['Plaster'])
# Four window bays / rear extent remain explicit inference pending footage.
for i in range(4):
 y=1.04+i*2.02
 for yy in [y-.975,y+.975]:box('Window bay %d side dark mullion'%i,(-3.984,yy,1.995),(.10,.050,2.19),M['black'])
 for z in [.90,1.44,2.53,3.09]:box('Window bay %d crossbar'%i,(-3.984,y,z),(.10,1.97,.046),M['black'])
 for yy in [y-.325,y+.325]:box('Window bay %d narrow vertical'%i,(-3.984,yy,1.995),(.095,.045,2.19),M['black'])
 for j in range(3):
  for k,(z,h) in enumerate([(1.17,.51),(1.985,1.045),(2.81,.515)]):box('Window glass %d_%d_%d'%(i,j,k),(-4.01,y-.65+j*.65,z),(.009,.60,h),M['glass'],0)
 box('Window sill stone ledge %d'%i,(-3.94,y,.895),(.30,1.97,.045),M['Ceiling'])
 if i<3:box('Window plaster pier %d'%i,(-4.02,y+1.01,1.99),(.23,.15,2.19),M['Plaster'])
cur='02_Front_Teaching_Wall'
box('Green teaching chalkboard',(0,.048,1.62),(4.50,.072,1.52),M['Chalkboard']);frame('Board brass edge',0,.10,1.62,4.50,1.52,M['brass'],.026)
box('Chalk and eraser ledge',(0,.15,.844),(4.56,.19,.037),M['DeskOak'])
for x in [-3.06,3.06]:
 box('Beige side bulletin board',(x,.035,1.62),(1.60,.050,1.52),M['Cork']);frame('Bulletin slim dark edge',x,.07,1.62,1.60,1.52,M['black'],.018)
for n,x,z,w,h in [('Large notice',3.03,1.98,.79,.58),('Small notice',2.59,1.18,.27,.29),('Small notice',3.08,1.19,.29,.26),('Top edge notice',3.68,2.23,.25,.19)]:box(n+' untranscribed', (x,.078,z),(w,.007,h),M['paper'],.001)
box('Front raised wooden podium',(0,.76,.10),(6.95,1.50,.20),M['DeskOak'],.012)
box('Podium front timber nosing',(0,1.50,.135),(6.99,.07,.08),M['darkwood'],.005)
# Only a few clearly identifiable decorative chalk motifs, no invented text.
for cx,cz,rr in [(1.57,2.05,.10),(1.99,1.78,.095)]:
 pts=[]
 for i in range(11):
  a=math.pi/2+i*math.pi/5;r=rr if i%2==0 else rr*.42;pts.append((cx+math.cos(a)*r,.091,cz+math.sin(a)*r))
 tube('Observed chalk star outline',pts,.005,M['chalk'])
# Right-side large face doodle is only a low-confidence outline, separately named.
pts=[(.95+math.cos(a)*.44,.092,1.47+math.sin(a)*.38) for a in [i*math.pi*2/48 for i in range(49)]];tube('Approximate partially occluded chalk doodle perimeter',pts,.005,M['chalk'])
cur='03_Bookcase_Books'
bx=-3.15;by=.31
box('Bookcase timber back',(bx,.20,1.07),(1.07,.043,1.74),M['DeskOak'])
for x in [bx-.54,bx+.54]:box('Bookcase side panel',(x,by,1.07),(.035,.30,1.78),M['DeskOak'])
for z in [.19,.61,1.02,1.43,1.94]:box('Bookcase shelf',(bx,by,z),(1.12,.32,.035),M['DeskOak'])
for shelf,z in enumerate([.215,.635,1.045,1.455]):
 x=bx-.49
 for j in range(14):
  w=random.uniform(.035,.066);h=random.uniform(.24,.36)
  if x+w>bx+.49:break
  box('Book spine shelf%d item%02d'%(shelf,j),(x+w/2,.41,z+h/2),(w,.18,h),BOOKS[(shelf*3+j)%len(BOOKS)],.002,rot=(0,random.choice([0,0,0,-.05,.045]),0));x+=w+.010
cur='04_Teacher_Desk_Podium'
# Teacher table consistent metric furniture scale, no camera-dependent stretch.
tx=.92;ty=.78;tz=.20
box('Teacher desktop',(tx,ty,tz+.77),(1.88,.69,.062),M['DeskOak'],.015)
box('Teacher vertical modesty panel',(tx,ty+.30,tz+.40),(1.75,.038,.66),M['DeskOak'])
for xx in [tx-.83,tx+.83]:box('Teacher desk end panel',(xx,ty,tz+.39),(.055,.60,.71),M['DeskOak'])
for x in [tx-.72,tx-.12,tx+.49]:box('Teacher desk front panel seam',(x,ty+.323,tz+.40),(.008,.004,.57),M['darkwood'],.001)
cur='05_Student_Desks_Chairs'
def student_set(x,y,k):
 box(k+' rounded oak desktop',(x,y,.766),(.66,.45,.041),M['DeskOak'],.012)
 box(k+' open underdesk shelf',(x,y,.642),(.58,.355,.014),M['black'])
 for xx in [x-.279,x+.279]:
  box(k+' underdesk side flange',(xx,y,.685),(.014,.357,.087),M['black'])
  for yy in [y-.145,y+.145]:
   rod(k+' tubular desk leg',(xx,yy,.045),(xx,yy,.741),.014,M['metal']);cyl(k+' desk rubber foot',(xx,yy,.024),.019,.048,M['rubber'])
  rod(k+' desk side low stretcher',(xx,y-.149,.22),(xx,y+.149,.22),.011,M['metal'])
 # chair is behind desktop, facing front (-Y), with narrow bent-tube uprights.
 cy=y+.57
 box(k+' chair oak seat',(x,cy,.443),(.382,.365,.028),M['DeskOak'],.013)
 box(k+' chair curved-back oak panel',(x,cy+.177,.72),(.365,.031,.154),M['DeskOak'],.026)
 for dx in [-.168,.168]:
  for yy in [cy-.137,cy+.146]:
   bot=(x+dx*1.12,yy+(-.035 if yy<cy else .035),.026);top=(x+dx,yy,.428);rod(k+' chair splayed leg',bot,top,.012,M['metal']);cyl(k+' chair rubber foot',(bot[0],bot[1],.020),.016,.04,M['rubber'])
  tube(k+' continuous back upright',[(x+dx,cy+.14,.40),(x+dx,cy+.18,.53),(x+dx,cy+.197,.79),(x+dx*.86,cy+.197,.816)],.012,M['metal'])
  rod(k+' seat side support',(x+dx,cy-.16,.414),(x+dx,cy+.18,.414),.012,M['metal'])
 rod(k+' low chair crossbar',(x-.17,cy+.16,.245),(x+.17,cy+.16,.245),.010,M['metal'])
 # Original footage consistently shows a pale notebook; limited, not an invented text page.
 if k in ['R1C1','R1C2','R1C3','R2C1']:
  box(k+' pale jade closed workbook',(x-.07,y,.796),(.245,.177,.012),M['mint'],.002,rot=(0,0,-.06))
  rod(k+' pencil',(x+.13,y-.07,.801),(x+.21,y+.05,.801),.004,M['black'])
for row,y in enumerate([2.10,3.46,4.82,6.18]):
 for col,x in enumerate([-2.55,-.87,.87,2.55]):student_set(x,y,'R%dC%d'%(row+1,col+1))
cur='07_Lights_Clock_Speaker'
box('Teaching wall monitor',(0,.16,2.77),(1.25,.095,.65),M['black'],.012)
box('Monitor dark screen',(0,.216,2.77),(1.18,.010,.58),mat('Unlit monitor glass',(.024,.032,.036),.24),.007)
rod('Monitor wall bracket',(0,.02,2.63),(0,.13,2.63),.045,M['black'])
# Clock oriented toward room (+Y).
cyl('Clock black rim',(2.04,.08,2.65),.19,.053,M['black'],rot=(math.pi/2,0,0),vertices=64)
cyl('Clock ivory face',(2.04,.112,2.65),.168,.011,M['paper'],rot=(math.pi/2,0,0),vertices=64)
for i in range(12):
 a=i*math.pi/6;rod('Clock hour tick',(2.04+math.sin(a)*.144,.121,2.65+math.cos(a)*.144),(2.04+math.sin(a)*.155,.121,2.65+math.cos(a)*.155),.002,M['black'])
rod('Clock hands approximate',(2.04,.126,2.65),(2.00,.126,2.755),.004,M['black']);rod('Clock hands approximate',(2.04,.127,2.65),(2.13,.127,2.61),.003,M['black'])
box('Wall vent grille left',(-3.47,.044,2.63),(.32,.057,.29),M['black'],.003)
for i in range(9):box('Wall vent horizontal slat',(-3.47,.078,2.51+i*.026),(.29,.008,.006),M['metal'],.001)
box('Small front-right wall loudspeaker',(3.78,.11,2.91),(.14,.11,.18),M['black'],.006)
cyl('Loudspeaker centre',(3.78,.175,2.91),.042,.012,M['white'],rot=(math.pi/2,0,0),vertices=24)
for row,y in enumerate([1.35,4.03,6.7]):
 for x in [-2.02,2.02]:
  for xx in [x-.52,x+.52]:rod('Fluorescent fixture suspension',(xx,y,3.35),(xx,y,3.10),.005,M['black'])
  box('Rectangular suspended fluorescent housing',(x,y,3.06),(1.55,.28,.073),M['black'],.008)
  box('Rectangular fluorescent milk diffuser',(x,y,3.016),(1.43,.225,.018),M['emission'],.003)
cur='08_Small_Observed_Props'
def cup(n,p):
 x,y,z=p;cyl(n+' body',(x,y,z+.066),.042,.126,M['blue'],vertices=32)
 cyl(n+' dark open top',(x,y,z+.131),.034,.003,M['black'],vertices=32)
 pts=[(x+.046+math.cos(a)*.027,y,z+.069+math.sin(a)*.041) for a in [i*2*math.pi/20 for i in range(21)]];tube(n+' handle',pts,.007,M['blue'])
cup('Teacher cup',(tx-.32,ty+.06,.999));cup('Front student cup',(-2.37,2.12,.788))
for i in range(3):box('Teacher stacked books %d'%i,(tx+.56,ty+.02,1.007+i*.032),(.30,.22,.028),BOOKS[[0,2,6][i]],.002)
# Pale globe-like desktop prop is observable, exact sculpture detail unresolved.
cyl('Approximate translucent desk ornament plinth',(tx+.16,ty,1.019),.095,.06,M['glass'],vertices=32)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.135,location=(tx+.16,ty,1.187));finish(bpy.context.object,'Approximate pale globe desk ornament',M['glass'],0,True)
cyl('Desk ornament stem',(tx+.16,ty,1.083),.012,.075,M['white'])
cur='91_INFERRED_Exterior_Context'
# Detached editable geometry, never a whole screenshot pasted on a wall.
for i in range(15):
 y=-6+i*1.50;x=random.uniform(-18,-12);w=random.uniform(.8,1.8);h=random.uniform(1.6,5.8)
 box('INFERRED exterior city block %02d'%i,(x,y,h/2+.4),(random.uniform(1,2.4),w,h),M['city'],.014)
 for z in range(1,int(h*2)):
  for yy in [y-w*.28,y+w*.28]:box('INFERRED facade glazing %d'%i,(x+1.23,yy,z*.45+.7),(.016,w*.28,.22),M['cityglass'],0)
for i in range(14):
 y=-3+i*1.02;x=random.uniform(-7.8,-6.1)
 rod('INFERRED tree trunk',(x,y,-.6),(x,y,1.55),.05,M['darkwood'])
 for j in range(4):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=random.uniform(.43,.75),location=(x+random.uniform(-.35,.35),y+random.uniform(-.33,.33),random.uniform(1.1,1.8)));o=finish(bpy.context.object,'INFERRED foliage canopy',M['leaf'] if j%2==0 else M['leaf2'],0,True);o.scale=(1,1,.90)
cur='99_Cameras_Lighting'
cam('MATCH_A_Front_00h15m19s',(-.05,5.20,1.68),(-.02,0,1.95),29)
cam('MATCH_B_Windows_00h35m23s',(.02,3.22,1.33),(-4,3.38,1.66),28)
cam('PANORAMA_Level_Front',(2.75,7.82,1.65),(-.45,1.42,1.65),22)
cam('PANORAMA_Level_Windows',(2.9,7.32,1.62),(-2.25,3.42,1.62),23)
cam('DETAIL_Desks_Podium',(.44,.80,1.55),(-1.55,2.7,.37),32)
area('Window daylight broad',(-3.7,4.0,2.5),(0,3.0,.6),650,5,(1,.91,.74))
area('Soft room fill',(1,4,3.13),(0,2,0),210,4,(.76,.86,1))
area('Front ambient',(0,1.5,3.15),(0,0,1),90,3,(1,.92,.79))
bpy.ops.object.light_add(type='SUN',location=(-6,1,8));sun=link(bpy.context.object);sun.name='Afternoon warm sunlight';sun.rotation_euler=(Vector((.9,.35,-.46))).to_track_quat('-Z','Y').to_euler();sun.data.energy=2.5;sun.data.angle=.07;sun.data.color=(1,.82,.59)
sc=bpy.context.scene;sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.63,.79,.9,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.50
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=5;sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.3
sc.camera=bpy.data.objects['PANORAMA_Level_Front'];sc['source']='Bilibili BV1LC411V7Nh, 2024-04-12 classroom replay. Structural interpretation only.';sc['scale']='Metric scale estimated from plausible classroom furniture; no measured dimensions.';sc['inferences']='Room depth, rear enclosure, 4x4 desk count, four window bays and light repetition are provisional. Exterior generic. No performers modeled.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Classroom_Blockout_Textured.blend'),compress=True)
for n,ca in [('Preview_Front','MATCH_A_Front_00h15m19s'),('Preview_Window','MATCH_B_Windows_00h35m23s'),('Preview_Panorama','PANORAMA_Level_Front')]:
 sc.camera=bpy.data.objects[ca];sc.render.filepath=str(R/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
clay=mat('White clay preview',(.67,.67,.67),.76)
for o in sc.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
sc.camera=bpy.data.objects['PANORAMA_Level_Front'];sc.render.filepath=str(R/'renders/Preview_White_Panorama.png');bpy.ops.render.render(write_still=True)
print('PREVIEW_COMPLETE')
