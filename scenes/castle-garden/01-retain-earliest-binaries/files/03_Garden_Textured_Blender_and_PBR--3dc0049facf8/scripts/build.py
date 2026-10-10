import bpy,os,math,random,json
from mathutils import Vector
from math import sin,cos,pi
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));random.seed(81)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=6
sc.render.resolution_x=1188;sc.render.resolution_y=668;sc.render.resolution_percentage=70;sc.view_settings.view_transform='AgX'
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.13,.24,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
C={}
for n in ['01_Visible_Facade_Patch','02_Paving_Flowerbed_Edges','03_Balustrades_and_Urns','04_Near_Rose_Uprights','05_Far_Floral_Arch','06_Dense_Flowerbeds','07_Cameras_Lighting']:
 c=bpy.data.collections.new(n);sc.collection.children.link(c);C[n]=c
cur=list(C)[0]
def put(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 C[cur].objects.link(o);return o

def mat(n,col,tex=None,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.7;p.inputs['Metallic'].default_value=metal
 if tex:
  for suffix,socket in [('basecolor','Base Color'),('roughness','Roughness'),('normal','Normal')]:
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(R+'/textures/'+tex+'_'+suffix+'.png');t.image.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color'
   if suffix=='normal':
    nn=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],nn.inputs['Color']);m.node_tree.links.new(nn.outputs['Normal'],p.inputs[socket]);nn.inputs['Strength'].default_value=.45
   else:m.node_tree.links.new(t.outputs['Color'],p.inputs[socket])
 return m
M={k:mat(k,col,k) for k,col in [('violet_masonry',(.24,.21,.34)),('aged_limestone',(.47,.43,.42)),('purple_paving',(.21,.1,.2)),('dark_wood',(.14,.05,.07)),('cyan_glass',(.06,.38,.47)),('leaf',(.13,.22,.055))]}
for k,col in [('dark_stem',(.07,.095,.018)),('soil',(.045,.04,.033)),('gold',(.36,.25,.11)),('rose',(.53,.23,.34)),('pink',(.63,.38,.47)),('cream',(.67,.57,.30)),('purple',(.31,.16,.46)),('blue',(.13,.22,.52)),('white_flower',(.67,.64,.57))]:M[k]=mat(k,col)
M['cyan_glass'].node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(.018,.16,.23,1);M['cyan_glass'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.35

def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);C[cur].objects.link(o);me.materials.append(M[m] if isinstance(m,str) else m);uv=me.uv_layers.new()
 for p in me.polygons:
  ax=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
  for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=(vs[vi][ax[0]],vs[vi][ax[1]])
 return o

def cube(n,loc,dim,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;put(o);o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[m])
 if bevel:
  b=o.modifiers.new('Subtle worn edge','BEVEL');b.width=bevel;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
 return o

def tube(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,cu);C[cur].objects.link(o);cu.materials.append(M[m]);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
 # Generated curve UVs are preserved.
 return o

def lathe(n,x,y,z,profile,m,sides=16):
 vs=[(x+r*cos(2*pi*i/sides),y+r*sin(2*pi*i/sides),z+h) for r,h in profile for i in range(sides)];fs=[]
 for j in range(len(profile)-1):
  for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;fs.append((a,b,b+sides,a+sides))
 return mesh(n,vs,fs,m)

def archpts(x,y,z,w,h):
 # Two gently convex Gothic shoulders meeting in a pointed apex.
 pts=[(x-w,y,z),(x-w,y,z+h*.65)]
 for i in range(1,17):
  t=i/16;pts.append((x-w+w*(1-cos(t*pi/2)),y,z+h*.65+h*.35*sin(t*pi/2)))
 for i in range(1,17):
  t=i/16;pts.append((x+w*sin(t*pi/2),y,z+h*.65+h*.35*cos(t*pi/2)))
 pts.append((x+w,y,z));return pts

def archfill(n,x,y,z,w,h,m):
 pts=archpts(x,y,z,w,h);return mesh(n,pts,[tuple(range(len(pts)-1,-1,-1))],m)
# Façade represented as finite visible patch, not an invented whole castle.
cube('Visible_violet_masonry_facade_patch',(0,5.9,3.4),(13,.28,6.8),'violet_masonry')
for x in [-5.8,-2.05,2.05,5.8]:
 cube('Stone_vertical_pilaster',(x,5.64,3.1),(.34,.35,6.2),'aged_limestone',.02)
 for dx in [-.2,.2]:cube('Pilaster_edge_flute',(x+dx,5.39,3.1),(.065,.10,6.2),'violet_masonry')
for z in [.13,.30,5.9]:cube('Facade_horizontal_cornice',(0,5.57,z),(13,.52,.13),'aged_limestone',.02)
archfill('Pointed_double_door',0,5.55,.25,1.18,4.8,'dark_wood')
for off in [0,.12,.22]:tube('Gothic_door_frame',archpts(0,5.39-off*.3,.23,1.25+off,4.9+off),.048,'aged_limestone')
cube('Door_central_seam',(0,5.48,2.2),(.028,.045,3.85),'gold')
for x in [-.57,.57]:
 for z in [1.0,2.2,3.45]:
  tube('Door_raised_diamond',[(x,5.43,z+.30),(x+.20,5.43,z),(x,5.43,z-.30),(x-.20,5.43,z),(x,5.43,z+.30)],.022,'gold')
 for dx in [-.4,.4]:cube('Door_raised_panel_border',(x+dx,5.47,2.0),(.025,.05,3.35),'gold')
for x in [-3.4,3.4]:
 archfill('Tall_cyan_leaded_window',x,5.51,1.15,.68,4.6,'cyan_glass');tube('Window_pointed_stone_border',archpts(x,5.39,1.1,.75,4.72),.075,'aged_limestone')
 for dx in [-.43,-.14,.14,.43]:cube('Window_dark_mullion',(x+dx,5.42,3.08),(.035,.04,3.65),'dark_stem')
 for zz in [1.5,2.1,2.7,3.3,3.9,4.5]:
  for dx in [-.43,-.14,.14,.43]:tube('Leaded_glass_diamond',[(x+dx,5.405,zz+.27),(x+dx+.14,5.405,zz),(x+dx,5.405,zz-.27),(x+dx-.14,5.405,zz),(x+dx,5.405,zz+.27)],.009,'gold')
 cube('Window_sill',(x,5.3,1.04),(1.75,.6,.16),'aged_limestone',.025)
cur='02_Paving_Flowerbed_Edges'
cube('INFERRED_thin_support_under_visible_patch',(0,.4,-.15),(11.6,11,.18),'violet_masonry')
for j in range(14):
 for i in range(3):cube('Purple_path_paving',(-.86+i*.86,-4.65+j*.70,-.025),(.85,.69,.07),'purple_paving',.013)
for s in [-1,1]:
 cube('Low_flowerbed_stone_edge',(s*1.47,.10,.08),(.28,9.8,.25),'aged_limestone',.045)
 cube('Front_flowerbed_stone_edge',(s*3.32,-4.70,.08),(3.45,.28,.25),'aged_limestone',.045)
 cube('Flowerbed_earth',(s*3.35,.10,.025),(3.45,9.6,.15),'soil')
cur='03_Balustrades_and_Urns'
for s in [-1,1]:
 for z,w,h in [(.3,.40,.18),(1.04,.45,.16),(1.18,.53,.12)]:cube('Stone_balustrade_rail',(s*5,.15,z),(w,10.1,h),'aged_limestone',.03)
 for j in range(27):lathe('Turned_stone_baluster',s*5,-4.65+j*.36,.35,[(.12,0),(.12,.09),(.063,.18),(.055,.40),(.10,.53),(.105,.60)],'aged_limestone',12)
 for yy in [-4.45,1.75,4.65]:
  cube('Urn_square_pedestal',(s*5,yy,.81),(.78,.78,1.62),'aged_limestone',.04)
  cube('Pedestal_cap',(s*5,yy,1.65),(.91,.91,.16),'aged_limestone',.03)
  lathe('Classical_flower_urn',s*5,yy,1.74,[(.28,0),(.3,.07),(.18,.18),(.23,.31),(.45,.40),(.58,.7),(.60,.79),(.53,.82)],'aged_limestone',24)
# Batched explicit leaf and petal surfaces keep the dense planting editable.
B={}
def polyadd(key,vs,fs):
 v,f=B.setdefault(key,([],[]));off=len(v);v.extend(vs);f.extend([tuple(i+off for i in face) for face in fs])
def leaf(p,size=.12):
 a=random.random()*2*pi;u=Vector((cos(a),sin(a),random.uniform(-.2,.6)));v=Vector((-sin(a),cos(a),.2));p=Vector(p)
 
 if cur in ['04_Near_Rose_Uprights','05_Far_Floral_Arch']:
  u=Vector((cos(a),random.uniform(-.15,.15),sin(a)));v=Vector((-sin(a),-.15,cos(a)))
 vs=[p-u*size,p+v*size*.40,p+u*size,p-v*size*.40,p+Vector((0,-size*.22,0))];polyadd('leaf',[tuple(v) for v in vs],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
def flower(p,r,col,layers=3):
 p=Vector(p);a=random.random()*2*pi;normal=Vector((random.uniform(-.6,.6),random.uniform(-.8,.2),1)).normalized();normal=Vector((random.uniform(-.35,.35),-1,random.uniform(-.2,.4))).normalized() if cur in ['04_Near_Rose_Uprights','05_Far_Floral_Arch'] else normal;u=normal.cross(Vector((0,1,0))).normalized();v=normal.cross(u)
 for l in range(layers):
  rr=r*(1-l*.24);count=7-l
  for k in range(count):
   ang=a+k*2*pi/count+l*.6;rad=u*cos(ang)+v*sin(ang);tan=-u*sin(ang)+v*cos(ang)
   center=p+rad*rr*.44+normal*r*l*.17
   vs=[center-rad*rr*.33,center+tan*rr*.46+normal*rr*.1,center+rad*rr*.65+tan*rr*.24+normal*rr*.30,center+rad*rr*.78+normal*rr*.35,center+rad*rr*.65-tan*rr*.24+normal*rr*.30,center-tan*rr*.46+normal*rr*.1]
   polyadd(col,[tuple(x) for x in vs],[(0,1,2,3),(0,3,4,5)])
def flush(prefix):
 global B
 for k,(v,f) in B.items():
  o=mesh(prefix+'_'+k,v,f,k)
  for p in o.data.polygons:p.use_smooth=True
 B={}
cur='06_Dense_Flowerbeds'
for s in [-1,1]:
 for i in range(1900):
  x=s*random.uniform(1.65,4.78);y=random.uniform(-4.4,4.7);z=random.uniform(.12,.46);leaf((x,y,z),random.uniform(.07,.19))
 for i in range(600):
  x=s*random.uniform(1.75,4.70);y=random.uniform(-4.4,4.65);z=random.uniform(.21,.64);col=random.choice(['rose','pink','cream','purple','blue','white_flower']);flower((x,y,z),random.uniform(.045,.125),col,3)
 for yy in [-4.45,1.75,4.65]:
  for i in range(75):
   a=random.random()*2*pi;r=random.random()*.52;p=(s*5+r*cos(a),yy+r*sin(a),2.51+random.random()*.2);leaf(p,.15)
   if i%2==0:flower(p,.065,random.choice(['blue','purple','pink']),2)
flush('Beds_and_urn_planting')
for group,yy,xx,hh in [('04_Near_Rose_Uprights',-3.1,2.9,5.2),('05_Far_Floral_Arch',3.45,1.95,3.95)]:
 cur=group
 path=[]
 if 'Far' in group:
  path=[(-xx,yy,z) for z in [i*.12 for i in range(25)]]+[(xx*cos(pi-i*pi/40),yy,2.85+1.1*sin(pi-i*pi/40)) for i in range(41)]+[(xx,yy,z) for z in [2.88-i*.12 for i in range(25)]]
 else:
  for s in [-1,1]:
   pts=[(s*xx+.06*sin(i),yy+.05*cos(i),i*.13) for i in range(41)];tube('Near_climbing_rose_wood_support',pts,.047,'dark_stem');path+=pts
 if 'Far' in group:tube('Far_floral_arch_support',path,.055,'dark_stem')
 for p in path:
  for j in range(18):
   q=(p[0]+random.uniform(-.22,.22),p[1]+random.uniform(-.19,.19),p[2]+random.uniform(-.10,.10));leaf(q,random.uniform(.08,.16))
  if random.random()<.86:
   q=(p[0]+random.uniform(-.18,.18),p[1]-.18,p[2]+random.uniform(-.10,.10));flower(q,random.uniform(.075,.125),random.choice(['cream','cream','pink']),4)
 flush(group)
cur='07_Cameras_Lighting'
def camera(n,pos,target,lens):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=n;put(o);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
camera('MATCH_A_00h25m11s',(.35,-10.9,2.65),(.0,4,2.65),27)
camera('MATCH_B_00h21m59s',(0,-10.3,2.65),(0,4,2.65),29)
camera('WIDE_Level_Entrance',(0,-14.5,3.9),(0,1.2,2.5),26)
camera('WIDE_Oblique_Visible_Patch',(10,-14,8),(0,1.5,1.7),34)
for n,loc,power,size,col in [('Soft_moon',(1,-4,10),1800,8,(.61,.66,1)),('Front_fill',(-4,-8,6),1500,7,(.94,.85,1)),('Arch_fill',(3,3,6),550,4,(.65,.65,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;put(o);o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(Vector((0,1,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
for o in sc.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  uv=o.data.uv_layers.new()
  for p in o.data.polygons:
   for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=(o.data.vertices[vi].co.x,o.data.vertices[vi].co.z)
sc.camera=bpy.data.objects['MATCH_A_00h25m11s'];bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Garden_Working.blend',compress=True)
sc.render.filepath=R+'/renders/v1_match.png';bpy.ops.render.render(write_still=True)
