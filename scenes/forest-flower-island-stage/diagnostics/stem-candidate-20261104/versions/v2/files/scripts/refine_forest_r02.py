import bpy,math,random,pathlib,bmesh
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];random.seed(110402)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R01_white.blend'))
# Import helper definitions only, without reinitializing or rebuilding prior objects.
source=(ROOT/'scripts/build_forest_r01.py').read_text();start=source.index('def material(');end=source.index('# Finite uneven earth')
exec(source[start:end]); soil=bpy.data.materials['Moss_and_earth'];bark=bpy.data.materials['Bark'];leaf=bpy.data.materials['Leaf'];pink=bpy.data.materials['Petal_pink'];blue=bpy.data.materials['Petal_blue'];pale=bpy.data.materials['Petal_pale'];yellow=bpy.data.materials['Pollen'];lilac=bpy.data.materials['Petal_lilac'];white=bpy.data.materials['WHITE_clay']
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  name=o.get('candidate_material');o.data.materials.clear();o.data.materials.append(bpy.data.materials.get(name) or soil)
# Improve deterministic bark surface silhouette, not texture as displaced source truth.
for o in bpy.context.scene.objects:
 if o.type=='MESH' and (o.name.startswith('TREE') or o.name.startswith('LOG')):
  for v in o.data.vertices:
   x,y,z=v.co;d=.035*math.sin(x*13+y*9+z*4)+.025*math.sin(x*4-y*5+z*1.1);v.co.x+=d;v.co.y+=.6*d
  o.data.update()
# Flower island groundcover: clear distinction between observed color fields and inferred individual flowers.
Z=1.2
items=[]
for i in range(4500):
 a=random.random()*math.tau;r=3.35*math.sqrt(random.random());x=r*math.cos(a);y=r*math.sin(a);items.append(((x,y,Z+random.uniform(.03,.14)),random.uniform(.07,.15),random.uniform(.018,.035),(random.uniform(-.5,.5),random.uniform(-.5,.5),1)))
leaves('ISLAND_turf_blades_procedural',items,leaf)
# Small flowers are grouped by observed approximate sectors, not individually claimed recovered instances.
for idx,(cx,cy,color) in enumerate([(-2.1,-1.7,pink),(-.8,-2.5,pink),(1,-2.3,blue),(2.3,-1.4,pink),(2.3,1,pink),(.4,2.4,blue),(-1.6,2.0,yellow),(-2.5,.4,blue),(0,0,yellow)]):
 items=[]
 for k in range(70):
  x=cx+random.uniform(-.5,.5);y=cy+random.uniform(-.5,.5)
  if x*x+y*y>10.5:continue
  zz=Z+random.uniform(.12,.25)
  for j in range(5):
   a=j*math.tau/5;items.append(((x+.04*math.cos(a),y+.04*math.sin(a),zz),.09,.05,(math.cos(a),math.sin(a),.12)))
 leaves('SMALL_FLOWERS_patch_%02d'%idx,items,color)
# Surrounding understory on open terrain; screen-space lights/shadows are not generated as solid structures.
for group in range(16):
 items=[]
 for j in range(400):
  a=random.uniform(group*math.tau/16,(group+1)*math.tau/16);r=random.uniform(4.2,13);x,y=r*math.cos(a),r*math.sin(a)
  # Provisional bare-path sector to visible right; no claimed actual map boundary.
  if x>5 and -3<y<6:continue
  items.append(((x,y,random.uniform(.08,.65)),random.uniform(.12,.4),random.uniform(.04,.13),(random.uniform(-1,1),random.uniform(-1,1),random.uniform(.3,1))))
 leaves('UNDERSTORY_patch_%02d'%group,items,leaf)
# Articulated fern fronds/leaflets, as visible foliage family, exact counts inferred.
fernpos=[(-5,3),(5,3),(-6,-1),(5,-4),(-4,6),(7,7),(-8,7),(1,8),(-7,-6),(8,-6),(-10,0),(10,3)]
for i,(x,y) in enumerate(fernpos):
 items=[]
 for f in range(7):
  a=f*math.tau/7+i*.7;L=random.uniform(1.4,2.5);pts=[]
  for k in range(10):
   t=k/9;pts.append((x+L*t*math.cos(a),y+L*t*math.sin(a),.1+1.5*math.sin(t*math.pi*.72)))
  tube('FERN_%02d_frond_%02d'%(i,f),pts,[.025*(1-k/11) for k in range(10)],leaf,6)
  for k in range(1,24):
   t=k/24;base=Vector((x+L*t*math.cos(a),y+L*t*math.sin(a),.1+1.5*math.sin(t*math.pi*.72)));length=.42*math.sin(t*math.pi)**.65
   for sign in [-1,1]:
    v=Vector((math.cos(a+sign*1.05),math.sin(a+sign*1.05),-.15));items.append((tuple(base+v*length*.45),length,.06,tuple(v)))
 leaves('FERN_%02d_leaflets'%i,items,leaf)
# Broad-leaf plants and red foliage families at observed approximate margins.
red=bpy.data.materials.new('Red_leaf');red.use_nodes=True;red.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.025,.035,1)
for i,(x,y) in enumerate([(-5,5),(5,6),(-6,0),(7,-1),(-8,9),(3,10)]):
 items=[]
 for j in range(24):
  a=j*2.4;r=.25+.35*(j/24);z=.4+j*.04;items.append(((x+r*math.cos(a),y+r*math.sin(a),z),.8,.19,(math.cos(a),math.sin(a),.5)))
 leaves('RED_FOLIAGE_%02d'%i,items,red)
for i,(x,y) in enumerate([(-6,-5),(7,-4),(-8,4),(8,4)]):
 items=[]
 for j in range(12):
  a=j*math.tau/12;items.append(((x+.7*math.cos(a),y+.7*math.sin(a),.7),1.9,.5,(math.cos(a),math.sin(a),.65)))
 leaves('BROAD_LEAF_%02d'%i,items,leaf)
# Finite upper branches, inferred canopy coverage. Never camera-specific visibility.
for i,(x,y) in enumerate([(-7,9),(-4,12),(4,10),(8,7),(-9,4),(8,12),(.5,6)]):
 for j in range(3):
  a=j*math.tau/3+i;tip=(x+3.5*math.cos(a),y+3.5*math.sin(a),13+j)
  tube('CANOPY_branch_%02d_%d'%(i,j),[(x,y,7),(x+1.3*math.cos(a),y+1.3*math.sin(a),10),tip],[.3,.18,.055],bark,10)
 items=[]
 for k in range(700):
  a=random.random()*math.tau;r=3.8*math.sqrt(random.random());items.append(((x+r*math.cos(a),y+r*math.sin(a),random.uniform(12,15)),.45,.18,(random.uniform(-1,1),random.uniform(-1,1),.15)))
 leaves('CANOPY_foliage_%02d'%i,items,leaf)
# Sparse visible vines, their hidden attachment and species inferred.
for i in range(12):
 x=random.uniform(-9,9);y=random.uniform(6,12);tube('VINE_%02d'%i,[(x,y,12),(x+.15,y+.2,9),(x-.2,y,6)],[.022,.02,.008],bark,6)
def setcam(name,loc,target,lens):
 o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
setcam('SOURCE_A_high',(0,-18,21),(0,.8,1.4),48)
setcam('SOURCE_B_side',(-8,-16,15),(0,.6,1.5),48)
setcam('SOURCE_C_low',(0,-15,6.4),(0,0,2.4),46)
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=32;s.world.color=(.07,.10,.15)
# Sky fill reduced to preserve canopy shadows; sources still not photometrically calibrated.
bpy.data.objects['SKY_fill_fixed'].data.energy=650
s.camera=bpy.data.objects['SOURCE_A_high'];s.render.resolution_percentage=100
for o in s.objects:
 if o.type=='MESH':o['candidate_material']=o.data.materials[0].name if o.data.materials else ''
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R02_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R02_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R02_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R02_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R02_SAVED',len([o for o in s.objects if o.type=='MESH']))
