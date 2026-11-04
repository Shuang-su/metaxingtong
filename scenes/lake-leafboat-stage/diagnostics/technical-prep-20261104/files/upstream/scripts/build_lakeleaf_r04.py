import bpy,bmesh,math,random,json,pathlib,sys,hashlib
from mathutils import Vector
from math import sin,cos,pi,sqrt
R=pathlib.Path(__file__).resolve().parents[1];random.seed(1104)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.35
s.world=bpy.data.worlds.new('Open sky daylight hypothesis');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.34,.54,.70,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s['candidate_status']='RECONSTRUCTION CANDIDATE / NOT SOURCE ACCEPTED';s['source']='BV1JqCeBMEAb; performance 2025-11-07, published 2025-11-17';s['units']='Arbitrary model units; no source metric scale';s['lighting_state']='Shared daylight hypothesis; night transition excluded';s['dynamic_exclusions']='Performer and white birds intentionally not reconstructed as static objects. Water phase unknown.'
collections={}
for name in ['01_LeafBoat','02_Lake','03_VisibleShoreHypothesis','04_ForestHypothesis','05_Cameras','06_Lighting']:
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c

def move(ob,c):
 for x in list(ob.users_collection):x.objects.unlink(ob)
 collections[c].objects.link(ob)
def mat(name,col,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;m.diffuse_color=(*col,1);return m
leaf=mat('LEAF_ObservedGreen_TissueHypothesis',(.2,.5,.04),.4)
for filename,target in [('leaf-tissue-albedo.png','Base Color'),('leaf-tissue-roughness.png','Roughness')]:
 im=bpy.data.images.load(str(R/'textures'/filename));im.filepath='//../textures/'+filename
 if target!='Base Color':im.colorspace_settings.name='Non-Color'
 n=leaf.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;leaf.node_tree.links.new(n.outputs['Color'],leaf.node_tree.nodes['Principled BSDF'].inputs[target])
vein=mat('VEIN_YellowGreen_ObservedBranching',(.32,.48,.055),.43)
water=mat('WATER_ReflectiveTurquoise_Hypothesis',(.012,.20,.26),.16,.32)
im=bpy.data.images.load(str(R/'textures/lake-colour-hypothesis.png'));im.filepath='//../textures/lake-colour-hypothesis.png';n=water.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;water.node_tree.links.new(n.outputs['Color'],water.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
im=bpy.data.images.load(str(R/'textures/water-wave-normal.png'));im.filepath='//../textures/water-wave-normal.png';im.colorspace_settings.name='Non-Color';n=water.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;uv=water.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='WaveUV';water.node_tree.links.new(uv.outputs['UV'],n.inputs['Vector']);normal=water.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.6;water.node_tree.links.new(n.outputs['Color'],normal.inputs['Color']);water.node_tree.links.new(normal.outputs['Normal'],water.node_tree.nodes['Principled BSDF'].inputs['Normal'])
bark=mat('BARK_DarkWarm',(.075,.061,.035),.85);earth=mat('SHORE_MossSoilHypothesis',(.075,.105,.034),.95);rock=mat('ROCK_GreyMossHypothesis',(.13,.16,.10),.9)
greens=[mat('FOLIAGE_'+str(i),c,.62) for i,c in enumerate([(.025,.10,.035),(.04,.17,.05),(.10,.24,.065),(.18,.31,.08),(.06,.20,.13),(.13,.29,.15)])]

def mesh(name,vs,fs,material,collection,uv=None,inference='Topology and extent inferred; not source confirmed'):
 m=bpy.data.meshes.new(name+'_mesh');m.from_pydata(vs,[],fs);m.update();o=bpy.data.objects.new(name,m);collections[collection].objects.link(o);o.data.materials.append(material);o['stable_id']=name;o['inference']=inference
 for p in m.polygons:p.use_smooth=True
 if uv:
  layer=m.uv_layers.new(name='UVMap')
  for p in m.polygons:
   for li in p.loop_indices:layer.data[li].uv=uv[m.loops[li].vertex_index]
 return o

def path(name,points,radii,material,collection,sides=7):
 vs=[];fs=[]
 for i,p in enumerate(points):
  p=Vector(p);a=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)]);a.normalize();b=a.cross(Vector((0,0,1)))
  if b.length<.01:b=a.cross(Vector((0,1,0)))
  b.normalize();c=a.cross(b).normalized()
  for j in range(sides):vs.append(tuple(p+radii[i]*(b*cos(j*2*pi/sides)+c*sin(j*2*pi/sides))))
 for i in range(len(points)-1):
  for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 fs += [tuple(reversed(tuple(range(sides)))),tuple((len(points)-1)*sides+j for j in range(sides))]
 return mesh(name,vs,fs,material,collection)

# Shared thin shell, single open concave upper leaf surface with two tapered poles.
def point(u,v):
 width=1.58*max(0,1-u*u)**.72*(1+.06*sin(3*pi*u))
 x=4.65*u;y=width*v
 end=(2.30 if u<0 else 1.65)*abs(u)**3.0
 z=.20+end+.75*v*v*(1-abs(u)**1.1)+.045*sin(8*pi*u+v*.8)*abs(v)**3*max(0,1-u*u)
 return (x,y,z)
nu=128;nv=40;vs=[];uv=[];fs=[]
for i in range(1,nu):
 u=-1+2*i/nu
 for j in range(nv+1):
  v=-1+2*j/nv;vs.append(point(u,v));uv.append(((u+1)/2,(v+1)/2))
for i in range(nu-2):
 for j in range(nv):
  a=i*(nv+1)+j;fs.append((a,a+nv+1,a+nv+2,a+1))
left=len(vs);vs.append(point(-1,0));uv.append((0,.5));right=len(vs);vs.append(point(1,0));uv.append((1,.5))
for j in range(nv):fs.append((left,j,j+1));a=(nu-2)*(nv+1)+j;fs.append((a,right,a+1))
o=mesh('LEAF_001_ThinConcaveShell',vs,fs,leaf,'01_LeafBoat',uv,'Observed elongated pointed outline and concave leaf. Thickness 0.035 model units, depth and underside inferred. Shared across all cameras.')
sol=o.modifiers.new('PhysicalLeafThickness_0.035_ModelUnits','SOLIDIFY');sol.thickness=.035;sol.offset=-1;sol.use_even_offset=True
sub=o.modifiers.new('GentleTissueSmoothing','SUBSURF');sub.levels=1;sub.render_levels=1
pts=[];rad=[]
for i in range(101):
 u=-.99+1.98*i/100;p=list(point(u,0));p[2]+=.022;pts.append(p);rad.append(.012+.035*(i/100))
path('LEAF_002_CentralMidrib',pts,rad,vein,'01_LeafBoat',9)
for k,u0 in enumerate([-.70,-.52,-.33,-.14,.05,.24,.43,.62,.79]):
 for sign in [-1,1]:
  pts=[];r=[]
  for j in range(31):
   t=j/30;u=u0-.25*t-.07*t*t;v=sign*(.90*sin(t*pi/2));p=list(point(u,v));p[2]+=.018;pts.append(p);r.append(.003+.019*(1-t)**1.2)
  path('LEAF_003_Branch_%02d_%s'%(k,'L' if sign<0 else 'R'),pts,r,vein,'01_LeafBoat',6)
# Lake extends beyond shot. Wave phase/colour are openly a hypothesis, not lakebed geometry.
N=130;vs=[];uv=[];fs=[]
for i in range(N+1):
 for j in range(N+1):
  x=-38+76*i/N;y=-38+76*j/N;z=.018*sin(x*2.7+y*1.1)+.009*sin(y*4.8-x*1.6)
  vs.append((x,y,z));uv.append((i/N,j/N))
for i in range(N):
 for j in range(N):a=i*(N+1)+j;fs.append((a,a+N+1,a+N+2,a+1))
o=mesh('LAKE_001_WaterSurface',vs,fs,water,'02_Lake',uv,'Observed reflective lake; finite boundary, ripple phase and coloured reflections inferred. This is a surface, not a solid closed lake volume.')
l=o.data.uv_layers.new(name='WaveUV')
for p in o.data.polygons:
 for li in p.loop_indices:l.data[li].uv=tuple(x*16 for x in uv[o.data.loops[li].vertex_index])
# One observed bank sector, not a fabricated enclosing lake ring.
vs=[];uv=[];fs=[]
for i in range(81):
 x=-35+70*i/80
 for j in range(16):
  y=9.6+1.1*sin(x*.16)+j*1.1;z=.05+.36*(1-math.exp(-j*.7))+.10*sin(x*.3+j*.2)
  vs.append((x,y,z));uv.append((i/80,j/15))
for i in range(80):
 for j in range(15):a=i*16+j;fs.append((a,a+16,a+17,a+1))
mesh('SHORE_001_ObservedBankSector',vs,fs,earth,'03_VisibleShoreHypothesis',uv,'A shore sector is observed. This contour and its continuation behind foliage are inferred; unobserved shore not closed into a ring.')

def blade(vs,fs,start,direction,length,width,drop=0.35,segments=12,tear=False):
 start=Vector(start);d=Vector((direction[0],direction[1],0)).normalized();side=Vector((-d.y,d.x,0));offset=len(vs)
 for i in range(segments+1):
  t=i/segments;c=start+d*length*t+Vector((0,0,length*(.36*sin(pi*t)-drop*t*t)));w=width*sin(pi*t)**.65
  for q in [-1,0,1]:
   cut=.55 if tear and i%5==3 and q==-1 else 1
   p=c+side*w*q*cut+Vector((0,0,-width*.18*abs(q)*sin(pi*t)));vs.append(tuple(p))
 for i in range(segments):
  a=offset+i*3;fs.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])

def palm(name,x,y,h,span,fronds=8,kind='feather'):
 trunk=[]
 for i in range(12):t=i/11;trunk.append((x+.30*t*t,y+.18*sin(t*pi*.7),.25+h*t))
 path(name+'_Trunk',trunk,[.11*(1-.35*i/11) for i in range(12)],bark,'04_ForestHypothesis',8)
 crown=Vector(trunk[-1]);vs=[];fs=[]
 for k in range(fronds):
  a=2*pi*k/fronds+random.uniform(-.18,.18);d=Vector((cos(a),sin(a),0));L=span*random.uniform(.8,1.2)
  if kind=='banana':blade(vs,fs,crown,d,L,L*.22,.24,14,True)
  else:
   for j in range(1,18):
    t=j/18;c=crown+d*L*t+Vector((0,0,L*(.34*sin(pi*t)-.32*t*t)));side=Vector((-d.y,d.x,0));ll=L*.32*sin(pi*t)**.65
    for q in [-1,1]:
     dr=(side*q+d*.4).normalized();blade(vs,fs,c,dr,ll,ll*.065,.27,4)
   # visible narrow central rachis along entire frond
   pp=[tuple(crown+d*L*t+Vector((0,0,L*(.34*sin(pi*t)-.32*t*t)))) for t in [j/18 for j in range(19)]]
   path(name+'_Rachis_%02d'%k,pp,[.022*(1-j/20) for j in range(19)],greens[2],'04_ForestHypothesis',4)
 o=mesh(name+'_Foliage',vs,fs,random.choice(greens[1:]),'04_ForestHypothesis');o['inference']='Palm/banana class observed; this individual count, branching and position are a candidate hypothesis, not an identified source instance.'
 # Thin leaves are intentional open surfaces; avoid falsely calling manifold.

# Hand-located foreground silhouettes plus deterministic middle/background layer.
for i,(x,y,h,sp,kind) in enumerate([(-11,11,7,3.1,'banana'),(-7,12,4,2.4,'feather'),(-3,14,6,3.0,'banana'),(2.5,12,5.6,2.5,'feather'),(7,11,8,3.2,'feather'),(11,12,6,3,'banana'),(15,13,8,3,'feather'),(-17,14,7.8,3,'feather')]):palm('BANKPALM_%03d'%i,x,y,h,sp,9,kind)
for i in range(34):
 x=random.uniform(-30,30);y=random.uniform(12,23);h=random.uniform(3.5,10.5);palm('FORESTPALM_%03d'%i,x,y,h,random.uniform(1.8,3.6),random.randint(6,10),'banana' if i%3==0 else 'feather')
# Fern undergrowth, each instance has stable ID.
for i in range(48):
 x=-28+56*i/47;y=10.5+random.uniform(0,5);palm('FERN_%03d'%i,x,y,random.uniform(.4,1.4),random.uniform(.8,1.8),7,'feather')
# Fine background broadleaf crowns, built as real quads, no source-image cards.
for i in range(25):
 x=-34+68*i/24;y=random.uniform(19,29);h=random.uniform(8,14)
 path('TREE_%03d_Trunk'%i,[(x,y,.2),(x+.2,y,h*.6),(x+.6,y+.2,h)],[.23,.16,.04],bark,'04_ForestHypothesis',8)
 vs=[];fs=[]
 for j in range(340):
  a=random.uniform(0,2*pi);r=random.random()**.5*3.3;z=h+random.uniform(-2.3,1.3);start=Vector((x+r*cos(a),y+r*sin(a),z));d=Vector((random.uniform(-1,1),random.uniform(-1,1),0));blade(vs,fs,start,d,random.uniform(.23,.52),random.uniform(.10,.23),.18,2)
 mesh('TREE_%03d_Crown'%i,vs,fs,random.choice(greens),'04_ForestHypothesis')
# Small visible rock with foliage seen only in overhead corner: placement uncertain.
for i in range(4):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(-14+i*.65,-8+random.uniform(-.6,.6),-.25));o=bpy.context.object;o.name='ROCK_%03d_OverheadCornerHypothesis'%i;o.scale=(1.4,1.0,.7);o.data.materials.append(rock);o['inference']='Rocky planted outcrop seen at overhead frame corner. This registration is uncertain.';move(o,'03_VisibleShoreHypothesis')
palm('OUTCROP_FERN',-13.6,-8,.15,1.8,9,'feather')

# R04: coherent global registration, never per-camera visibility edits.
# Source overhead has almost no main bank. Shift the single bank sector farther out.
for o in collections['03_VisibleShoreHypothesis'].objects:
 if o.name.startswith('SHORE'):o.location.y+=22
 else:o.location.x+=22;o.location.y-=16
for o in collections['04_ForestHypothesis'].objects:
 if o.name.startswith('OUTCROP'):o.location.x+=22;o.location.y-=16
 else:o.location.y+=22;o.scale.z=2
# Dense source forest has a mid-storey that R01 lacked. Add real leaf meshes, not image backdrops.
for i in range(54):
 x=random.uniform(-38,38);y=random.uniform(37,49);h=random.uniform(4,16)
 vs=[];fs=[]
 for j in range(1100):
  a=random.uniform(0,2*pi);r=random.random()**.5*4.8;z=h+random.uniform(-3.2,2.4);start=Vector((x+r*cos(a),y+r*sin(a),z));d=Vector((random.uniform(-1,1),random.uniform(-1,1),0));blade(vs,fs,start,d,random.uniform(.55,1.1),random.uniform(.24,.44),.18,2)
  # Tilt the whole local blade around its start to populate broadleaf crown volume.
  from mathutils import Quaternion
  q=Quaternion(Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1))).normalized(),random.uniform(-1.3,1.3))
  for ii in range(len(vs)-9,len(vs)):vs[ii]=tuple(start+q@(Vector(vs[ii])-start))
 mesh('MIDSTOREY_%03d_Crown'%i,vs,fs,random.choice(greens[:4]),'04_ForestHypothesis')
for o in collections['01_LeafBoat'].objects:o.location.z-=.16
s['R04_changes']='Global boat lowered 0.16 for tentative water approach; bank moved +22Y, forest Zx2 plus midstorey; source cameras corrected. No camera-conditioned geometry.'

# R04: one shared near-bank low/middle layer, no new shoreline claims.
for i in range(58):
 x=-45+90*i/57;y=32.2+random.uniform(-.2,5.5);h=random.uniform(1.3,4.1)
 palm('LOWBANK_%03d'%i,x,y,h,random.uniform(1.6,3.2),9,'banana' if i%3==0 else 'feather')
for i in range(30):
 x=-43+86*i/29;y=35+random.uniform(0,4);h=random.uniform(1.4,3.0);vs=[];fs=[]
 for j in range(440):
  a=random.uniform(0,2*pi);r=random.random()**.5*2.3;start=Vector((x+r*cos(a),y+r*sin(a),h+random.uniform(-1.2,1.4)));d=Vector((random.uniform(-1,1),random.uniform(-1,1),0));blade(vs,fs,start,d,random.uniform(.4,.9),random.uniform(.18,.35),.18,2)
  from mathutils import Quaternion
  q=Quaternion(Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1))).normalized(),random.uniform(-1.4,1.4))
  for ii in range(len(vs)-9,len(vs)):vs[ii]=tuple(start+q@(Vector(vs[ii])-start))
 mesh('LOWBANKSHRUB_%03d_Crown'%i,vs,fs,random.choice(greens[:4]),'04_ForestHypothesis')

def camera(name,loc,target,lens=50,roll=0,size=(1600,900),orth=None):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);collections['05_Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.rotation_euler.rotate_axis('Z',roll);d.lens=lens;d.sensor_width=36;d.clip_end=300
 if orth:d.type='ORTHO';d.ortho_scale=orth
 o['source_width']=size[0];o['source_height']=size[1];o['calibration']='Initial visual hypothesis, not solved or accepted';return o
camera('SOURCE_092142973_SIDE',(0,-16,2.5),(0,0,2.55),44,.075,(3840,2160))
o=camera('SOURCE_100762992_TOP',(0,0,70),(0,0,0),43,0,(3840,2160));o.rotation_euler=(0,0,1.37);o.data.shift_x=-.008;o.data.shift_y=-.022
camera('SOURCE_108755584_OBLIQUE',(1.5,-6.5,1.7),(-1.2,0,1.7),38,0,(3840,2160))
camera('AUX_006585758_REAR',(4.1,-2.7,2.5),(-2,0,1.1),48,0,(3840,2160))
camera('HERO',(-2.4,-15,3.6),(0,2,2.6),43,0,(1600,900))
for i in range(8):
 a=2*pi*i/8;z=4.2 if i%2==0 else 8.5;camera('CHECK_%02d'%(i+1),(13*cos(a),13*sin(a),z),(0,0,.7),48,0,(1280,720))
ld=bpy.data.lights.new('Sun_DaylightShared','SUN');ld.energy=3.2;ld.angle=.18;o=bpy.data.objects.new('Sun_DaylightShared',ld);collections['06_Lighting'].objects.link(o);o.rotation_euler=(.45,-.55,-.4)
ld=bpy.data.lights.new('SkyFillShared','AREA');ld.energy=350;ld.shape='DISK';ld.size=9;o=bpy.data.objects.new('SkyFillShared',ld);collections['06_Lighting'].objects.link(o);o.location=(-2,-4,10)
s.camera=bpy.data.objects['HERO']
# Encode explicit evidence classifications in all editable objects.
for o in s.objects:
 if 'stable_id' not in o:o['stable_id']=o.name
 if 'inference' not in o:o['inference']='Initial camera/light hypothesis' if o.type in {'CAMERA','LIGHT'} else 'Inferred candidate geometry'
# Remove coincident blade-pole vertices and zero-area geometry while preserving intended open leaf sheets.
for o in s.objects:
 if o.type=='MESH' and ('Foliage' in o.name or 'Crown' in o.name):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
(R/'models').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r04-material.blend'))
# Export all source/check cameras with shared evaluated geometry and original image textures.
bpy.ops.export_scene.gltf(filepath=str(R/'models/lakeleaf-r04.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
white=mat('WHITE_DiagnosticOnly',(.66,.67,.64),.75)
for o in s.objects:
 if o.type=='MESH':
  for k in range(len(o.data.materials)):o.data.materials[k]=white
s['white_model_note']='Same geometry, transforms and visibility as material version; material-only diagnostic replacement.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r04-white.blend'))
print('FINISHED_LAKELEAF_R04')
