import bpy,math,random,pathlib,json,hashlib,bmesh
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]; random.seed(1104)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials):bpy.data.materials.remove(d)
def material(name,color,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
white=material('WHITE_clay',(.65,.65,.65)); soil=material('Moss_and_earth',(.07,.13,.022)); bark=material('Bark',(.10,.055,.023));leaf=material('Leaf',(.12,.24,.035));pink=material('Petal_pink',(.8,.19,.3));blue=material('Petal_blue',(.32,.52,.8));lilac=material('Petal_lilac',(.5,.2,.7));pale=material('Petal_pale',(.72,.8,.86));yellow=material('Pollen',(.58,.25,.015));rock=material('Rock',(.16,.18,.12))
for m,scale in [(soil,8),(bark,4),(rock,6)]:
 n=m.node_tree.nodes;l=m.node_tree.links;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=4;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.4;bump.inputs['Distance'].default_value=.07;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
def mesh(name,verts,faces,mat,inference):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);ob['inference']=inference
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 return ob
def tube(name,points,radii,mat,sides=10):
 vs=[];fs=[]
 for k,p in enumerate(points):
  p=Vector(p);t=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)]);t.normalize();q=t.to_track_quat('Z','Y')
  for j in range(sides):a=2*math.pi*j/sides;vs.append(tuple(p+q@Vector((radii[k]*math.cos(a),radii[k]*math.sin(a),0))))
 for k in range(len(points)-1):
  for j in range(sides):a=k*sides+j;b=k*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
 fs.append(tuple(reversed(range(sides))));fs.append(tuple((len(points)-1)*sides+j for j in range(sides)))
 return mesh(name,vs,fs,mat,'Visible branch/trunk family; dimensions, cross sections, unseen backs inferred')
def sphere(name,loc,sc,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=sc;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);o['inference']='Observed approximate form; exact shape and hidden surface inferred';return o
def leaves(name,items,mat):
 vs=[];fs=[]
 for pos,L,W,rot in items:
  q=Vector(rot).to_track_quat('X','Z');base=len(vs);shape=[(-L/2,0,0),(L/2,0,0),(0,-W/2,0),(0,W/2,0),(0,0,.012),(0,0,-.012)]
  vs.extend(tuple(Vector(pos)+q@Vector(x)) for x in shape)
  fs.extend(tuple(base+i for i in f) for f in [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)])
 return mesh(name,vs,fs,mat,'Procedural leaf approximation; placement family observed, individual leaf count and surfaces not recovered')
# Finite uneven earth, no walls or ceiling. Closed underside is a working-domain inference.
N=64;vs=[(0,0,0)];
for r in [5,10,16]:
 for j in range(N):
  a=j*math.tau/N;h=.10*math.sin(j*.7)+(.10 if r==10 else 0);vs.append((r*math.cos(a),r*math.sin(a),h))
fs=[(0,1+j,1+(j+1)%N) for j in range(N)]
for k in range(2):
 for j in range(N):a=1+k*N+j;b=1+k*N+(j+1)%N;fs.append((a,a+N,b+N,b))
bot=len(vs)
for j in range(N):a=j*math.tau/N;vs.append((16*math.cos(a),16*math.sin(a),-.65))
for j in range(N):a=1+2*N+j;b=1+2*N+(j+1)%N;fs.append((a,b,bot+(j+1)%N,bot+j))
fs.append(tuple(reversed([bot+j for j in range(N)])));mesh('TERRAIN_finite_working_domain',vs,fs,soil,'Open natural landscape observed; radial extent16, underside-.65 and terrain interpolation inferred')
# Bounded flower-island state hypothesis, not a solid hedge ring. Height to be tested against temporal evidence.
Z=1.2
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=3.35,depth=.18,location=(0,0,Z-.09));deck=bpy.context.object;deck.name='ISLAND_moss_bedding_inferred';deck.data.materials.append(soil);deck['inference']='Thin unseen bedding inferred under visible turf; not a measured solid platform or support mechanism'
# Knotted root network under visible overhanging foliage, retaining voids.
for i in range(22):
 a=i*math.tau/22;pts=[]
 for k in range(9):
  t=k/8;r=3.5*(1-t)+.25;ang=a+.3*math.sin(t*math.pi);pts.append((r*math.cos(ang),r*math.sin(ang),Z-.2-.8*math.sin(math.pi*t)))
 tube('ISLAND_root_%02d'%i,pts,[.13*(1-k/11) for k in range(9)],bark)
for i in range(40):
 a=i*math.tau/40;r=3.25;pts=[(r*math.cos(a),r*math.sin(a),Z-.35),((r+.25)*math.cos(a+.08),(r+.25)*math.sin(a+.08),Z+.3),((r+.38)*math.cos(a-.05),(r+.38)*math.sin(a-.05),Z+.75)]
 tube('RIM_shrub_branch_%02d'%i,pts,[.05,.035,.009],bark,8)
 items=[]
 for j in range(65):
  th=a+random.uniform(-.10,.10);rr=random.uniform(3.05,3.85);z=Z+random.uniform(-.45,.75);items.append(((rr*math.cos(th),rr*math.sin(th),z),random.uniform(.16,.32),random.uniform(.06,.13),(math.cos(th+random.uniform(-1,1)),math.sin(th+random.uniform(-1,1)),random.uniform(-.6,.6))))
 leaves('RIM_leaves_%02d'%i,items,leaf)
# Major cup flowers, approximate identified color/order around top; no performer placeholders.
flowers=[(-2.8,1.0,.85,pink),(-2.45,1.8,.8,pale),(-1.4,2.6,1.0,pink),(1.1,2.7,.9,blue),(2.7,1.1,.95,pink),(2.95,.1,.65,lilac),(1.1,-2.65,.55,pale),(-.95,-2.7,.5,lilac),(-2.6,-1.2,.7,pink)]
for i,(x,y,h,mat) in enumerate(flowers):
 tube('FLOWER_%02d_stem'%i,[(x,y,Z),(x+.08,y,Z+h*.6),(x,y,Z+h)],[.045,.035,.025],leaf,10)
 for pet in range(5):
  a=pet*math.tau/5;v=[];f=[]
  # closed thick petal, curved cup surface with independent outside/inside shells
  for side in [-1,1]:
   for k in range(6):
    t=k/5;rr=.07+.43*t;zz=Z+h-.08+.23*t*t
    for j in range(5):
     w=(j/4-.5)*1.05*math.sin(math.pi*(.10+.80*t));ang=a+w;v.append((x+rr*math.cos(ang),y+rr*math.sin(ang),zz+.08*math.cos(w*3)*t+side*.009))
  for side in [0,30]:
   for k in range(5):
    for j in range(4):q=side+k*5+j;f.append((q,q+1,q+6,q+5))
  boundary=[0,1,2,3,4,9,14,19,24,29,28,27,26,25,20,15,10,5]
  for j,a0 in enumerate(boundary):b0=boundary[(j+1)%len(boundary)];f.append((a0,b0,b0+30,a0+30))
  mesh('FLOWER_%02d_petal_%d'%(i,pet),v,f,mat,'Visible giant cup flower; five petals and cross-section are provisional simplification')
 sphere('FLOWER_%02d_centre'%i,(x,y,Z+h+.01),(.075,.075,.08),yellow)
# Stable background anchors; unseen branching and exact dimensions inferred.
tube('TREE_main_trunk',[(.5,6,-.15),(.45,6,1),(.2,6.1,3),(.8,6.1,6),(.5,6.4,10),(.8,6.8,15)],[1.45,1.15,.95,.83,.65,.3],bark,24)
for i in range(8):
 a=i*math.tau/8;tube('TREE_main_buttress_%02d'%i,[(.5+2.6*math.cos(a),6+2.6*math.sin(a),0),(.5+1.5*math.cos(a),6+1.5*math.sin(a),.35),(.5+.7*math.cos(a),6+.7*math.sin(a),2.5)],[.18,.4,.22],bark,10)
tube('LOG_left_fallen',[(-7,5,.35),(-5.5,5.6,.5),(-4,6.1,.7),(-2.8,6.7,.8)],[.4,.5,.48,.35],bark,16)
for i,(x,y) in enumerate([(-7,9),(-4,12),(4,10),(8,7),(10,-2),(-10,-3),(-9,4),(8,12)]):
 tube('TREE_background_%02d'%i,[(x,y,0),(x+.4,y,5),(x-.3,y+.2,11),(x,y,17)],[.7,.55,.35,.16],bark,12)
for i,(x,y) in enumerate([(-6,-3),(6,-2),(-6,3),(6,4),(-5,-7),(9,2)]):sphere('ROCK_%02d'%i,(x,y,.15),(random.uniform(.4,.9),random.uniform(.35,.8),random.uniform(.3,.6)),rock)
# Cameras: conditional hypotheses, not calibrated. All share identical scene state.
def cam(name,loc,target,lens=48,w=1920,h=1080):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o['source_width']=w;o['source_height']=h;return o
cam('SOURCE_A_high',(0,-14,17),(0,1,1),48)
cam('SOURCE_B_side',(-10,-12,14),(0,1,1),48)
cam('SOURCE_C_low',(1,13,6.5),(0,0,2),46)
for i in range(8):
 a=i*math.tau/8;cam('CHECK_%02d'%(i+1),(12*math.cos(a),12*math.sin(a),8 if i%2 else 12),(0,0,2),28,1280,720)
bpy.ops.object.light_add(type='SUN',location=(5,-3,12));sun=bpy.context.object;sun.name='SUN_fixed';sun.rotation_euler=(.4,-.5,-.6);sun.data.energy=2;sun.data.angle=.18
bpy.ops.object.light_add(type='AREA',location=(0,-3,10));l=bpy.context.object;l.name='SKY_fill_fixed';l.data.energy=1300;l.data.shape='DISK';l.data.size=12
s=bpy.context.scene;s.world.color=(.13,.16,.2);s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4;s.view_settings.view_transform='AgX';s.camera=bpy.data.objects['SOURCE_A_high'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
# First stage is white only; preserve construction material assignment data in object properties for next stage.
for o in s.objects:
 if o.type=='MESH':
  o['candidate_material']=o.data.materials[0].name if o.data.materials else '';o.data.materials.clear();o.data.materials.append(white)
(ROOT/'models').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R01_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R01_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R01_SAVED',len([o for o in s.objects if o.type=='MESH']))
