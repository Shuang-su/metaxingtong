import bpy,math,random,os,json
from mathutils import Vector
from math import sin,cos,pi,sqrt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));random.seed(42)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=6
sc.render.resolution_x=1188;sc.render.resolution_y=668;sc.render.resolution_percentage=65;sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.52,.7,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
sc.view_settings.view_transform='AgX';sc.unit_settings.system='METRIC'
C={}
for n in ['01_Deck_Gravel_Steps','02_Fences_Railing','03_White_Egg_Chair','04_Autumn_Tree','05_Easel','06_Cedar_Feature_Wall','07_Moon_Side_Table','08_Arch_Threshold_Only','09_Background_Approximation','10_Cameras_Lights']:
 c=bpy.data.collections.new(n);sc.collection.children.link(c);C[n]=c
cur=list(C)[0]
def put(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 C[cur].objects.link(o);return o
def mat(n,col,r=.65,met=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=met;return m
M={n:mat(n,c) for n,c in [('white',(.82,.81,.76)),('black',(.023,.025,.028)),('soil',(.15,.13,.105)),('pot',(.32,.34,.3)),('paper',(.86,.87,.80)),('city',(.48,.57,.61)),('window',(.18,.29,.36))]}
for n in ['warm_deck','wall_cedar','tree_bark','white_wicker','linen','gravel','autumn_gold','autumn_yellow','green_leaf','moon']:
 m=mat(n,(.5,.5,.5));M[n]=m;p=m.node_tree.nodes['Principled BSDF']
 for suffix,socket in [('basecolor','Base Color'),('roughness','Roughness'),('normal','Normal')]:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(ROOT+'/textures/'+n+'_'+suffix+'.png');t.image.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color'
  if suffix=='normal':
   nn=m.node_tree.nodes.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.4;m.node_tree.links.new(t.outputs[0],nn.inputs['Color']);m.node_tree.links.new(nn.outputs[0],p.inputs[socket])
  else:m.node_tree.links.new(t.outputs[0],p.inputs[socket])
p=M['moon'].node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(1,.72,.22,1);p.inputs['Emission Strength'].default_value=.25

def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);C[cur].objects.link(o);me.materials.append(m);uv=me.uv_layers.new()
 for p in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
  for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=(v[vi][axes[0]],v[vi][axes[1]])
 return o

def cube(n,l,d,m,b=.0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);put(o);o.data.materials.append(m)
 if b:
  q=o.modifiers.new('Rounded_real_edges','BEVEL');q.width=b;q.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 return o

def cyl(n,a,b,r,m,r2=None,seg=12):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();put(o);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o

def tube(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(n,cu);C[cur].objects.link(o);cu.materials.append(m);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def ball(n,l,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=l);o=bpy.context.object;o.name=n;o.scale=s;put(o);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
# Deck planks individually modelled around the inset bed.
for j in range(29):
 y=-3+j*.18
 spans=[(-4,4.9)] if y<-.88 or y>1.96 else [(-4,-3.75),(1.35,4.9)]
 for a,b in spans:cube('Deck_board',((a+b)/2,y,-.055),(b-a,.171,.11),M['warm_deck'],.008)
cube('Gravel_bed',(-1.2,.52,-.045),(5.06,2.89,.11),M['gravel'])
for a,b in [((-3.8,-.97,.04),(1.41,-.97,.04)),((-3.8,-.97,.04),(-3.8,2,.04)),((1.41,-.97,.04),(1.41,2,.04))]:cyl('Inset_bed_edge',a,b,.028,M['white'],seg=8)
for y in [-.68,-.18,.32]:cube('Rectangular_dark_stepping_strip',(-1.25,y,.035),(2.8,.22,.085),M['tree_bark'],.015)
# Combined small pebble geometry, not a photo plane.
v=[];f=[]
for k in range(1000):
 x=random.uniform(-3.72,1.3);y=random.uniform(-.91,1.9);r=random.uniform(.015,.038);z=.012;i=len(v)
 v.extend([(x-r,y,z),(x,y-r,z),(x+r,y,z),(x,y+r,z),(x,y,z+r)]);f.extend([(i,i+1,i+4),(i+1,i+2,i+4),(i+2,i+3,i+4),(i+3,i,i+4)])
mesh('Individual_gravel_stones',v,f,M['gravel'])
cur='02_Fences_Railing'
cube('Rear_white_parapet',(-1.32,2.08,.2),(5.42,.18,.4),M['white'],.02);cube('Left_white_parapet',(-4.02,.53,.2),(.18,3.25,.4),M['white'],.02)
for j in range(8):
 z=.62+j*.18;cube('Rear_horizontal_cedar_slat',(-1.32,2.08,z),(5.42,.08,.105),M['wall_cedar'],.008);cube('Left_horizontal_cedar_slat',(-4,.62,z),(.08,3.05,.105),M['wall_cedar'],.008)
for x in [-4,-2.25,-.45,1.4]:cube('Rear_fence_upright',(x,2.08,1.07),(.085,.12,1.45),M['wall_cedar'])
for y in [-1.1,.5,2.08]:cube('Left_black_railing_post',(-4.1,y,1.05),(.06,.06,1.5),M['black'])
cube('Left_black_railing_top',(-4.1,.49,1.83),(.07,3.22,.065),M['black'])
cur='03_White_Egg_Chair';cx,cy,cz=-1.3,.48,1.42;rx,ry,rz=.78,.65,.92
# Back cage with an open front. Longitudinal ribs, diagonal woven intersections.
for i in range(23):
 a=pi*.04+i*pi*.92/22
 pts=[(cx+rx*cos(a)*sin(t),cy+ry*sin(a)*sin(t),cz+rz*cos(t)) for t in [j*pi/48 for j in range(49)]];tube('Egg_chair_back_longitudinal_rib',pts,.017,M['white_wicker'])
for j in range(1,15):
 t=j*pi/15;pts=[(cx+rx*cos(a)*sin(t),cy+ry*sin(a)*sin(t),cz+rz*cos(t)) for a in [k*pi/40 for k in range(41)]];tube('Egg_chair_back_cross_weave',pts,.012,M['white_wicker'])
tube('Egg_chair_front_oval_rim',[(cx+rx*sin(t),cy-.07,cz+rz*cos(t)) for t in [j*2*pi/100 for j in range(101)]],.035,M['white_wicker'])
ball('Egg_chair_seat_cushion',(cx,cy-.08,.76),(.62,.52,.16),M['linen'])
for x,a in [(cx-.36,-.3),(cx+.35,.3)]:
 o=ball('Egg_chair_side_pillow',(x,cy+.0,1.04),(.25,.21,.4),M['linen']);o.rotation_euler.y=a
ball('Egg_chair_central_pillow',(cx,cy+.29,1.05),(.36,.18,.30),M['linen'])
for j in range(30):
 z=2.36+j*.061;pts=[]
 for k in range(17):
  t=k*2*pi/16;pts.append((cx+.026*cos(t) if j%2==0 else cx,cy if j%2==0 else cy+.026*cos(t),z+.041*sin(t)))
 tube('Suspension_chain_link',pts,.007,M['white'])
cur='04_Autumn_Tree'
tips=[]
def branch(a,d,length,r,depth):
 b=Vector(a)+Vector(d).normalized()*length;cyl('Tree_branch',a,b,r,M['tree_bark'],r*.55,10)
 if depth<=0:tips.append(tuple(b));return
 for k in range(3 if depth>1 else 2):
  dd=Vector(d)+Vector((random.uniform(-.85,.85),random.uniform(-.7,.7),random.uniform(-.14,.6)));branch(b,dd,length*random.uniform(.62,.79),r*.55,depth-1)
branch((-1.9,1.35,.04),(.06,0,1),1.12,.13,4)
# Additional lateral growth makes the reference's broad irregular crown.
for direction in [(-.9,.05,.65),(.85,.1,.65),(-.2,.5,.8),(.5,-.1,.9)]:branch((-1.84,1.35,1.33),direction,.8,.063,3)
for shade in ['autumn_gold','autumn_yellow']:
 vs=[];fs=[]
 for tip in tips:
  for k in range(8):
   p=Vector(tip)+Vector((random.uniform(-.26,.26),random.uniform(-.26,.26),random.uniform(-.22,.22)));s=random.uniform(.025,.066);a=random.uniform(0,2*pi);u=Vector((cos(a),sin(a),0))*s;vv=Vector((-sin(a)*.5,cos(a)*.5,random.uniform(.25,.95)))*s;i=len(vs)
   # Six-point lobed autumn leaf, bent along its midrib.
   vs.extend([p,p+u*.55+vv,p+u*.4+vv*.36,p+u,p-u*.1-vv*.55,p-u*.65,p-u*.4+vv*.4,p-u*.45+vv]);fs.extend([(i,i+j,i+j+1) for j in range(1,7)])
 mesh('Autumn_individual_lobed_leaves_'+shade,vs,fs,M[shade])
# Fallen leaves scattered on the gravel.
vs=[];fs=[]
for k in range(650):
 x=random.gauss(-1.35,1.0);y=random.uniform(-.86,1.9)
 if not -3.7<x<1.3:continue
 r=random.uniform(.025,.055);i=len(vs);vs.extend([(x-r,y,.045),(x,y+r,.05),(x+r,y,.045),(x,y-r,.052)]);fs.append((i,i+1,i+2,i+3))
mesh('Fallen_autumn_leaf_scatter',vs,fs,M['autumn_gold'])
cur='05_Easel';ex,ey=-3.0,-.24
for dx in [-.34,.34]:cyl('Easel_front_leg',(ex+dx,ey-.06,.04),(ex+dx*.7,ey+.17,1.89),.027,M['warm_deck'])
cyl('Easel_rear_leg',(ex,ey+.62,.04),(ex,ey+.18,1.72),.03,M['warm_deck'])
cube('Easel_canvas_stretcher',(ex,ey,1.27),(.91,.055,1.14),M['white'],.018);cube('Canvas_unreproduced_artwork',(ex,ey-.032,1.27),(.83,.012,1.06),M['paper'])
cube('Easel_painting_shelf',(ex,ey-.05,.66),(1,.13,.055),M['warm_deck']);cube('Easel_leg_crossbar',(ex,ey-.02,.4),(.75,.04,.04),M['warm_deck'])
cur='06_Cedar_Feature_Wall'
cube('Feature_wall_backing',(2.6,2.10,2.14),(2.5,.17,4.28),M['wall_cedar'])
for i in range(24):cube('Vertical_cedar_wall_board',(1.405+i*.104,1.99,2.14),(.094,.065,4.28),M['wall_cedar'],.006)
cube('Small_roof_overhang',(2.6,1.35,4.27),(2.6,1.65,.14),M['wall_cedar'])
# Rectangular roof strip only where visible overhead, not an invented full terrace roof.
cube('Visible_overhead_header',(-1.3,1.78,4.3),(5.4,.16,.17),M['white'])
for x in [-3.8,-2.8,-1.8,-.8,.2,1.2]:cube('Visible_header_short_divider',(x,1.78,4.12),(.045,.08,.27),M['black'])
def plant(x,y,z,s):
 cyl('Planter',(x,y,z),(x,y,z+s*.42),s*.22,M['pot'],s*.3,20)
 for k in range(12):
  a=random.random()*2*pi;end=Vector((x+s*.5*cos(a),y+s*.5*sin(a),z+s*random.uniform(.65,1.3)));cyl('Plant_stem',(x,y,z+s*.4),end,.006,M['green_leaf'],seg=6);ball('Plant_leaf',end,(s*.14,s*.07,s*.23),M['green_leaf'])
for x,z in [(1.96,1.99),(2.45,2.94),(3.34,3.27)]:
 cube('Wall_floating_shelf',(x,1.81,z),(.68,.36,.055),M['warm_deck']);plant(x-.1,1.78,z+.03,.36)
for x,z,r in [(2.63,3.51,.20),(3.01,3.48,.18),(3.32,3.48,.18),(2.6,2.94,.19),(2.88,2.68,.2)]:tube('Wall_circular_hanging_ornament',[(x+r*cos(t),1.86,z+r*sin(t)) for t in [j*2*pi/60 for j in range(61)]],.014,M['warm_deck'])
# Trailing strands at left shelf.
for k in range(15):
 x=2.18+random.random()*.32;z=2.94;y=1.7
 pts=[(x+.015*sin(j),y-.03*j,z-.075*j) for j in range(random.randint(4,10))];tube('Trailing_plant_stem',pts,.006,M['green_leaf'])
 for p in pts:ball('Trailing_plant_leaf',p,(.04,.025,.055),M['green_leaf'])
cur='07_Moon_Side_Table'
ball('Moon_globe_flattened_disk',(2.45,1.7,.89),(.73,.105,.73),M['moon'])
cyl('Side_table_round_top',(3.52,1.05,.77),(3.52,1.05,.82),.35,M['black'],seg=48)
for a in [j*2*pi/8 for j in range(8)]:tube('Side_table_curved_cage_leg',[(3.52+(.17+.17*sin(t*pi/2))*cos(a),1.05+(.17+.17*sin(t*pi/2))*sin(a),.08+.69*t) for t in [j/20 for j in range(21)]],.016,M['black'])
ball('White_sphere_under_table',(3.52,1.05,.29),(.26,.26,.26),M['white']);plant(3.6,1.04,.83,.26)
cyl('Table_small_cup',(3.31,.99,.83),(3.31,.99,.95),.061,M['white'],seg=20)
cur='08_Arch_Threshold_Only'
# Right wall with a true open arch cut-out. Opening beyond remains unmodelled.
ax=4.65;rad=.85;spring=2.55;top=4.3;left=3.8;right=5.5
cube('Arch_left_jamb',(3.73,1.77,1.28),(.18,.64,2.56),M['white'])
vs=[];fs=[]
for i in range(41):
 t=pi-i*pi/40;x=ax+rad*cos(t);z=spring+rad*sin(t);vs.extend([(x,1.45,z),(x,2.12,z),(x,1.45,top),(x,2.12,top)])
for i in range(40):
 a=i*4;b=a+4;fs.extend([(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a,a+1,b+1,b)])
mesh('Arch_curved_opening_solid_spandrel',vs,fs,M['white']);cube('Arch_right_jamb',(5.54,1.77,1.28),(.18,.64,2.56),M['white'])
cube('Arch_short_threshold_only',(4.69,1.79,-.02),(1.7,.66,.06),M['white'])
cur='09_Background_Approximation'
# Distant city silhouettes are separate generic stand-ins, not surveyed architecture.
for i,(x,h,w) in enumerate([(-6.6,3.1,.7),(-5.4,2.5,1.1),(-3.9,3.5,.6),(-.5,2.3,.7),(.9,3.0,.8)]):
 cube('APPROXIMATE_distant_building',(x,7,h/2-1.0),(w,.5,h),M['city'])
 for z in [j*.17 for j in range(int(h/.17)-2)]:cube('Distant_window_strip',(x,6.739,z-.75),(w*.8,.01,.046),M['window'])
cur='10_Cameras_Lights'
def camera(n,loc,target,lens):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=n;put(o);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=200;return o
camera('MATCH_A_29m46s',(.15,-10.1,2.8),(.15,.65,1.94),35)
camera('WIDE_Level_Terrace',(0,-12.7,4.1),(.3,.45,1.85),34)
camera('WIDE_Oblique_Geometry',(-7.8,-10.5,6.4),(.3,.5,1.7),35)
for n,loc,energy,size in [('Large_soft_sky',(-3,-4,8),1700,7),('Front_fill',(4,-6,4),700,5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;put(o);o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,1,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='SUN',location=(-4,-6,7));o=bpy.context.object;put(o);o.rotation_euler=(.5,-.3,-.7);o.data.energy=1.5;o.data.angle=.12
# UVs on all converted tubes, generated in object-local axes.
for o in sc.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  uv=o.data.uv_layers.new()
  for p in o.data.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
   for li,vi in zip(p.loop_indices,p.vertices):v=o.data.vertices[vi].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
sc.camera=bpy.data.objects['MATCH_A_29m46s'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Terrace_Working.blend',compress=True)
sc.render.filepath=ROOT+'/renders/Iteration_01.png';bpy.ops.render.render(write_still=True)
