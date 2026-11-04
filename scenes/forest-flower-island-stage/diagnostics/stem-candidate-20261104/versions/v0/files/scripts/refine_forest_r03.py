import bpy,math,random,pathlib,bmesh
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];random.seed(110403);bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R02_material.blend'))
source=(ROOT/'scripts/build_forest_r01.py').read_text();exec(source[source.index('def mesh('):source.index('# Finite uneven earth')])
soil=bpy.data.materials['Moss_and_earth'];bark=bpy.data.materials['Bark'];leaf=bpy.data.materials['Leaf'];white=bpy.data.materials.get('WHITE_clay')
if white is None:
 white=bpy.data.materials.new('WHITE_clay');white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
# Explicit fixed floating state for all cameras, not animated/per-camera swapping.
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('ISLAND','RIM','FLOWER','SMALL_FLOWERS')):o.location.z+=3.3;o['state']='fixed floating candidate; absolute elevation inferred, not measured animation'
Z=4.5
# Finite dark hanging core contour observed; exact composition and hidden interior inferred.
verts=[];faces=[];N=48
for k,(r,z) in enumerate([(2.9,Z-.08),(2.65,Z-.35),(2.1,Z-.85),(1.2,Z-1.5),(.3,Z-2.0)]):
 for j in range(N):
  a=j*math.tau/N;rr=r*(1+.045*math.sin(j*2.3+k));verts.append((rr*math.cos(a),rr*math.sin(a),z+.06*math.sin(j*1.7+k)))
for k in range(4):
 for j in range(N):a=k*N+j;b=k*N+(j+1)%N;faces.append((a,b,b+N,a+N))
faces.extend([tuple(reversed(range(N))),tuple(4*N+j for j in range(N))]);mesh('ISLAND_dark_hanging_core',verts,faces,bark,'Visible tapered dark underside silhouette; soil/rock/root material identity, internal filling, dimensions inferred. Not a stem or support column.')
for i in range(20):
 a=i*math.tau/20;pts=[]
 for k in range(7):
  t=k/6;r=3.4-1.8*t;pts.append((r*math.cos(a+.2*t),r*math.sin(a+.2*t),Z-.15-1.5*t))
 tube('ISLAND_hanging_root_%02d'%i,pts,[.10*(1-k/9) for k in range(7)],bark,8)
 items=[]
 for j in range(120):
  t=random.random();th=a+random.uniform(-.15,.15);r=3.5-1.4*t;items.append(((r*math.cos(th),r*math.sin(th),Z-.2-1.4*t),.26,.10,(math.cos(th),math.sin(th),-.6)))
 leaves('ISLAND_hanging_leaves_%02d'%i,items,leaf)
# Increase natural silhouette variation of pre-existing roots/trunks without camera-dependent changes.
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and o.name.startswith(('TREE_main','LOG_left')):
  bpy.context.view_layer.objects.active=o;sub=o.modifiers.new('Organic_surface_subdivision','SUBSURF');sub.levels=2;sub.render_levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
  tex=bpy.data.textures.new(o.name+'_bark_shape',type='CLOUDS');tex.noise_scale=.25;d=o.modifiers.new('Small_bark_relief','DISPLACE');d.texture=tex;d.strength=.075;bpy.ops.object.modifier_apply(modifier=d.name)
# Dense shrubs in finite background; procedural approximations, not recovered individual plant identities.
for i in range(32):
 a=i*math.tau/32;r=random.uniform(5,14);x,y=r*math.cos(a),r*math.sin(a)
 if x>6 and -1<y<4:continue
 items=[];height=random.uniform(.7,1.7)
 for j in range(700):
  az=random.random()*math.tau;rr=random.random()**.5*random.uniform(.8,1.3);z=random.uniform(.2,height);items.append(((x+rr*math.cos(az),y+rr*math.sin(az),z),random.uniform(.14,.3),random.uniform(.05,.11),(random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.2,.8))))
 leaves('DENSE_SHRUB_%02d'%i,items,leaf)
# Foreground fern groups at visible edges; broaden inferred scene coverage for wide views.
for i,(x,y) in enumerate([(-7,-10),(7,-11),(-11,-4),(11,-5),(-10,8),(10,10)]):
 items=[]
 for f in range(9):
  a=f*math.tau/9+i*.6;L=random.uniform(2.5,3.8);pts=[]
  for k in range(12):
   t=k/11;pts.append((x+L*t*math.cos(a),y+L*t*math.sin(a),.1+2.2*math.sin(t*math.pi*.75)))
  tube('FOREGROUND_FERN_%02d_frond_%02d'%(i,f),pts,[.045*(1-k/13) for k in range(12)],leaf,6)
  for k in range(1,32):
   t=k/32;base=Vector((x+L*t*math.cos(a),y+L*t*math.sin(a),.1+2.2*math.sin(t*math.pi*.75)));length=.65*math.sin(t*math.pi)**.65
   for sign in [-1,1]:
    v=Vector((math.cos(a+sign*1.05),math.sin(a+sign*1.05),-.15));items.append((tuple(base+v*length*.45),length,.07,tuple(v)))
 leaves('FOREGROUND_FERN_%02d_leaflets'%i,items,leaf)
# Provisional cutout-free full geometry vines and leaves; no hidden view-dependent billboards.
for i in range(8):
 x=-7+i*2;y=random.uniform(5,10);items=[]
 for k in range(55):
  z=12-k*.12;items.append(((x+.15*math.sin(k*.6),y+.12*math.cos(k*.6),z),.22,.08,(.6*(-1 if k%2 else 1),0,-1)))
 leaves('VINE_LEAVES_%02d'%i,items,leaf)
# Vary foliage albedo by deterministic mesh object, retain same shader under all cameras.
n=leaf.node_tree.nodes;l=leaf.node_tree.links;oi=n.new('ShaderNodeObjectInfo');ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.085,.008,1);ramp.color_ramp.elements[1].color=(.20,.36,.055,1);l.new(oi.outputs['Random'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);n.get('Principled BSDF').inputs['Roughness'].default_value=.65
# Camera hypotheses only. Earlier sources remain temporal/layout diagnostics, not same-state acceptance.
def cam(name,loc,target,lens,w=1920,h=1080):
 o=bpy.data.objects.get(name)
 if o is None:bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name
 o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o['source_width']=w;o['source_height']=h;return o
cam('SOURCE_A_high',(0,-18,24.3),(0,.8,4.7),48)
cam('SOURCE_B_side',(-8,-16,18.3),(0,.6,4.8),48)
cam('SOURCE_C_low',(0,-15,9.7),(0,0,5.7),46)
cam('SOURCE_D_floating_wide',(0,-21,10),(0,.5,5.3),20)
for i in range(8):
 a=i*math.tau/8;cam('CHECK_%02d'%(i+1),(12*math.cos(a),12*math.sin(a),9 if i%2 else 13),(0,0,4),28,1280,720)
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=32;s.camera=bpy.data.objects['SOURCE_D_floating_wide'];s.render.resolution_percentage=100
bpy.data.objects['SUN_fixed'].data.energy=3;bpy.data.objects['SKY_fill_fixed'].data.energy=400
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R03_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R03_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R03_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R03_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R03_SAVED',len([o for o in s.objects if o.type=='MESH']))
