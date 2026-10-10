import bpy, math, random, os, json
from mathutils import Vector
from math import sin,cos,pi,sqrt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));random.seed(513)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials:bpy.data.materials.remove(m)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False
sc.render.threads_mode='FIXED';sc.render.threads=6;sc.render.resolution_x=1188;sc.render.resolution_y=668;sc.render.resolution_percentage=70
sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.world.color=(.05,.05,.05)
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.014,.005,.036,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
C={}
for n in ['01_Visible_Stage_Patch','02_Inflated_Armchairs','03_Floor_Lamp','04_Telescope','05_Hanging_Silver_Stars','06_Stage_Lighting_Audio','07_Procedural_City_Approximation','08_Optional_Star_Companion','09_Optional_Moving_Balloon_Dog','10_Cameras_Studio_Lights']:
 c=bpy.data.collections.new(n);sc.collection.children.link(c);C[n]=c
cur='01_Visible_Stage_Patch'
def put(o,c=None):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 C[c or cur].objects.link(o);return o

def mat(n,col,rough=.5,metal=0,emission=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emission
 return m
M={
'white':mat('Glazed_ivory_checker',(.69,.7,.78),.23,.12),'black':mat('Glazed_midnight_checker',(.010,.014,.035),.26,.12),'blue':mat('Cobalt_stage_edge',(.08,.22,.52),.32,.15),
'chrome':mat('Cool_brushed_aluminium',(.51,.63,.8),.21,.85),'silver':mat('Inflated_silver_foil',(.61,.69,.83),.17,.94),'dark':mat('Satin_black_hardware',(.012,.015,.024),.35,.32),
'lamp':mat('Warm_frosted_lampshade',(.86,.71,.48),.38,0,2),'tube':mat('Telescope_warm_grey',(.58,.6,.69),.32,.35),'lens':mat('Optical_glass_blue',(.018,.04,.1),.12,.7),
'pink':mat('Magenta_neon',(.7,.035,.34),.28,.05,3),'cyan':mat('Cyan_neon',(.02,.65,.86),.24,.1,3),'violet':mat('Violet_neon',(.25,.06,.75),.27,.1,3),
'yellow':mat('Plush_star_yellow',(.98,.72,.23),.7,0,.3),'face':mat('Plush_embroidered_face',(.055,.025,.012),.86),'blush':mat('Plush_pink_cheeks',(.9,.26,.37),.86),
'dog':mat('Glossy_red_balloon',(.54,.012,.065),.17,.25),'building':mat('Midnight_city_concrete',(.006,.007,.023),.61,.12),'building2':mat('Deep_violet_city_concrete',(.011,.006,.029),.55,.15),
'window':mat('Cool_city_windows',(.072,.095,.23),.4,.05,.32),'windowdim':mat('Dim_city_windows',(.016,.023,.064),.5,.1,.10),'warmwindow':mat('Warm_city_windows',(.19,.14,.12),.5,.05,.24)}
M['fabric']=mat('PBR_Silver_Blue_Woven_Upholstery',(.53,.62,.76),.42,.34)
p=M['fabric'].node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.18;p.inputs['Sheen Weight'].default_value=.2
for file,socket,space in [('silver_fabric_basecolor.png','Base Color','sRGB'),('silver_fabric_roughness.png','Roughness','Non-Color'),('silver_fabric_normal.png','Normal','Non-Color')]:
 n=M['fabric'].node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(ROOT+'/textures/'+file);n.image.colorspace_settings.name=space
 if socket=='Normal':
  nn=M['fabric'].node_tree.nodes.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.45;M['fabric'].node_tree.links.new(n.outputs['Color'],nn.inputs['Color']);M['fabric'].node_tree.links.new(nn.outputs['Normal'],p.inputs[socket])
 else:M['fabric'].node_tree.links.new(n.outputs['Color'],p.inputs[socket])
M['grille']=mat('PBR_Perforated_speaker_grille',(.025,.03,.04),.6,.4);n=M['grille'].node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(ROOT+'/textures/speaker_grille.png');M['grille'].node_tree.links.new(n.outputs['Color'],M['grille'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

def mesh(n,vs,fs,m,c=None,uv=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);C[c or cur].objects.link(o)
 if m:me.materials.append(m)
 layer=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li,vi in zip(poly.loop_indices,poly.vertices):layer.data[li].uv=uv[vi] if uv else (vs[vi][axes[0]],vs[vi][axes[1]])
 return o

def cube(n,loc,dims,m,bevel=0,c=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);put(o,c);o.data.materials.append(m)
 if bevel:
  b=o.modifiers.new('Soft_edge','BEVEL');b.width=bevel;b.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return o

def cyl(n,a,b,r,m,rad2=None,sides=20,c=None):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cone_add(vertices=sides,radius1=r,radius2=r if rad2 is None else rad2,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();put(o,c);o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o

def tube(n,pts,r,m,c=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.resolution_u=2;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,cu);C[c or cur].objects.link(o);o.data.materials.append(m);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def uvball(n,loc,scale,m,c=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;put(o,c);o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o

def spow(x,e):return (1 if x>=0 else -1)*abs(x)**e

def cushion(n,loc,dims,back=False):
 vs=[];fs=[];uv=[];N=112;J=56;a,b,c=[v/2 for v in dims]
 for j in range(J+1):
  lat=-pi/2+pi*j/J
  for i in range(N):
   lon=2*pi*i/N;x=a*spow(cos(lat),.64)*spow(sin(lon),.62);y=b*spow(cos(lat),.64)*spow(cos(lon),.62);z=c*spow(sin(lat),.70)
   front=max(0,-y/b)**5
   if back:
    # Vertical drawn-up folds at the lower front of each back bolster.
    env=math.exp(-((z/c+.55)/.78)**2);fold=.024*sin(43*x+2*sin(7*x))+ .009*sin(69*x)
    y+=front*env*fold;z+=.006*front*env*sin(36*x)
   else:
    # Two recessed fastenings and radial soft creases on the front skirt.
    for bx in [-.29,.29]:
     d2=((x-bx)/.064)**2+((z-.035)/.058)**2;y+=front*.034*math.exp(-d2*.8)
     y+=front*.007*math.exp(-d2*.12)*sin(18*math.atan2(z-.035,x-bx))
    z-=.025*math.exp(-(x/.48)**2)*max(0,z/c)**5
   vs.append((x+loc[0],y+loc[1],z+loc[2]));uv.append((i/N*3,j/J*2))
 for j in range(J):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 o=mesh(n,vs,fs,M['fabric'],uv=uv)
 for f in o.data.polygons:f.use_smooth=True
 return o

# Stage surface is only a visible patch. Its off-camera extent is inferred.
# Each floor checker is genuine planar mesh clipped against the same perimeter.
poly=[(-6,-4.5),(6,-4.5),(6,-.2),(.82,1.90),(-6,-.2)]
def clip(subject,bound):
 out=subject
 for k,p in enumerate(bound):
  q=bound[(k+1)%len(bound)];inp=out;out=[]
  if not inp:break
  def side(v):return (q[0]-p[0])*(v[1]-p[1])-(q[1]-p[1])*(v[0]-p[0])
  for i,s in enumerate(inp):
   e=inp[(i+1)%len(inp)];a=side(s);b=side(e)
   if a>=0:out.append(s)
   if (a>=0)!=(b>=0):t=a/(a-b);out.append((s[0]+t*(e[0]-s[0]),s[1]+t*(e[1]-s[1])))
 return out
ang=pi/4;tile=1.12
for i in range(-10,11):
 for j in range(-10,11):
  q=[]
  for u,v in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]:
   x=(u*tile)*cos(ang)-(v*tile)*sin(ang);y=(u*tile)*sin(ang)+(v*tile)*cos(ang);q.append((x+.2,y+.12))
  pts=clip(q,poly)
  if len(pts)>=3:mesh('Checker_%+03d_%+03d'%(i,j),[(x,y,0) for x,y in pts],[tuple(range(len(pts)))],M['white'] if (i+j)%2==0 else M['black'])
# A thin support is included for editing. Unknown front/end geometry is not treated as evidence.
verts=[(x,y,z) for z in [-.13,-.015] for x,y in poly];N=len(poly);faces=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
mesh('INFERRED_support_under_visible_patch',verts,faces,M['blue'])
for a,b,oa,ob in [((-6,-.2),(.82,1.9),(-6,.9),(.82,3.65)),((.82,1.9),(6,-.2),(.82,3.65),(6,.95))]:
 mesh('Visible_blue_rear_band',[(a[0],a[1],-.01),(b[0],b[1],-.01),(ob[0],ob[1],-.01),(oa[0],oa[1],-.01)],[(0,1,2,3)],M['blue'])
 tube('Narrow_silver_boundary',[(a[0],a[1],.007),(b[0],b[1],.007)],.018,M['chrome'])
cur='02_Inflated_Armchairs'
for k,x in [('Left',-.81),('Right',.93)]:
 cushion(k+'_single_seat_inflated_base',(x,-.075,.365),(1.59,1.36,.60))
 cushion(k+'_gathered_back_bolster',(x+(.13 if k=='Right' else -.11),.39,.875),(1.49,.61,.60),True)
 for dx in [-.59,.59]:
  for yy in [-.47,.43]:cyl(k+'_short_dark_foot',(x+dx,yy,.018),(x+dx,yy,.11),.055,M['dark'])
 for dx in [-.29,.29]:
  # Small round covered fabric fastenings; do not remove the dimple geometry underneath.
  uvball(k+'_covered_front_button',(x+dx,-.744,.4),(.017,.01,.017),M['fabric'])
 # Narrow lower fabric seam, visible at the base.
 pts=[]
 for i in range(120):
  t=2*pi*i/119;pts.append((x+.772*spow(sin(t),.62),-.075+.64*spow(cos(t),.62),.117))
 tube(k+'_lower_upholstery_seam',pts,.0038,M['fabric'])
cur='03_Floor_Lamp';lx,ly=-2.55,2.05
cyl('Lamp_round_low_foot',(lx,ly,.0),(lx,ly,.038),.19,M['chrome'],sides=48)
cyl('Lamp_slim_stem',(lx,ly,.035),(lx,ly,2.09),.017,M['chrome'],sides=24)
cyl('Lamp_lower_stem_sleeve',(lx,ly,.055),(lx,ly,.45),.024,M['chrome'])
profile=[(0,2.26),(.15,2.265),(.28,2.25),(.39,2.22),(.435,2.18),(.448,2.14),(.435,2.105),(.32,2.098),(.31,2.065),(.13,2.065),(0,2.075)]
vs=[];fs=[]
for r,z in profile:
 for i in range(64):t=i*2*pi/64;vs.append((lx+r*cos(t),ly+r*sin(t),z))
for j in range(len(profile)-1):
 for i in range(64):fs.append((j*64+i,j*64+(i+1)%64,(j+1)*64+(i+1)%64,(j+1)*64+i))
o=mesh('Lamp_warm_saucer_shade',vs,fs,M['lamp'])
for f in o.data.polygons:f.use_smooth=True
cur='04_Telescope';tx,ty=-1.18,2.4
for angle in [-pi/2,pi/6,5*pi/6]:
 a=(tx+.08*cos(angle),ty+.08*sin(angle),1.23);b=(tx+.39*cos(angle),ty+.39*sin(angle),.025);cyl('Tripod_black_leg',a,b,.025,M['dark']);cyl('Tripod_silver_foot',(b[0],b[1],.02),(b[0],b[1],.10),.028,M['chrome'])
pts=[(tx+.30*cos(a),ty+.30*sin(a),.38) for a in [-pi/2,pi/6,5*pi/6,-pi/2]];tube('Tripod_spreader_triangle',pts,.015,M['dark'])
cyl('Telescope_white_mount_post',(tx,ty,1.12),(tx,ty,1.51),.073,M['tube'])
cyl('Telescope_black_mount_head',(tx,ty,1.45),(tx,ty,1.61),.105,M['dark'])
cyl('Optical_tube_body',(tx-.55,ty,1.72),(tx+.12,ty,1.72),.117,M['tube'],sides=48)
cyl('Objective_black_rim',(tx-.59,ty,1.72),(tx-.55,ty,1.72),.124,M['dark'],sides=48)
cyl('Recessed_objective_glass',(tx-.588,ty,1.72),(tx-.587,ty,1.72),.106,M['lens'],sides=48)
for xx in [tx-.12,tx-.02]:cyl('White_tube_ring',(xx-.018,ty,1.72),(xx+.018,ty,1.72),.124,M['tube'],sides=40)
cyl('Rear_focuser',(tx+.12,ty,1.72),(tx+.28,ty,1.72),.07,M['dark'])
cube('Eyepiece_diagonal_housing',(tx+.26,ty,1.745),(.16,.13,.14),M['tube'],.015)
cyl('Eyepiece_top',(tx+.3,ty,1.77),(tx+.3,ty,1.9),.033,M['dark'])
cyl('Finder_scope',(tx-.2,ty,1.9),(tx+.04,ty,1.9),.027,M['dark'])
cyl('Finder_bracket',(tx-.02,ty,1.8),(tx-.02,ty,1.88),.018,M['dark'])

def star(n,center,radius,thick,m,phase=pi/2):
 # Closed, rounded inflated star with explicit front/back surfaces and spherical UVs.
 N=100;R=20;vs=[];uv=[];fs=[]
 outline=[]
 corners=[Vector(((1 if i%2==0 else .50)*cos(phase+2*pi*i/10),(1 if i%2==0 else .50)*sin(phase+2*pi*i/10))) for i in range(10)]
 for k,p in enumerate(corners):
  prev=corners[(k-1)%10];nxt=corners[(k+1)%10];rounding=.75 if k%2==0 else .10
  start=p+(prev-p)*rounding;end=p+(nxt-p)*rounding
  for j in range(10):
   t=j/10;point=(1-t)**2*start+2*(1-t)*t*p+t*t*end;outline.append(point)

 for side in [-1,1]:
  for j in range(R+1):
   rr=j/R
   for i in range(N):
    a=2*pi*i/N+phase;x=rr*radius*outline[i].x;z=rr*radius*outline[i].y;y=side*thick*sqrt(max(0,1-rr**2))
    # Slight foil seam crumpling at the edge only.
    if m==M['silver']:y+=side*.008*sin(i*.71)*rr**7
    vs.append((center[0]+x,center[1]+y,center[2]+z));uv.append((i/N,j/R))
 K=(R+1)*N
 for s in range(2):
  for j in range(R):
   for i in range(N):
    f=(s*K+j*N+i,s*K+j*N+(i+1)%N,s*K+(j+1)*N+(i+1)%N,s*K+(j+1)*N+i);fs.append(f if s==0 else f[::-1])
 for i in range(N):fs.append((R*N+i,R*N+(i+1)%N,K+R*N+(i+1)%N,K+R*N+i))
 o=mesh(n,vs,fs,m,uv=uv)
 for f in o.data.polygons:f.use_smooth=True
 return o
cur='05_Hanging_Silver_Stars'
for i,(x,y,z,r) in enumerate([(-1.36,.10,2.43,.34),(1.20,.60,2.86,.355),(2.88,.50,2.73,.39)]):
 star('Silver_star_%02d'%i,(x,y,z),r*1.27,.18,M['silver']);cyl('Suspension_line_%02d_UNSEEN_ANCHOR'%i,(x,y,z+r),(x,y,5.7),.0035,M['chrome'],sides=6)
# A ringed purple sphere is partially visible at the far left of the reference.
planet=uvball('Partly_seen_ringed_planet_APPROX',(-3.42,1.0,3.12),(.26,.26,.26),M['violet'])
bpy.ops.mesh.primitive_torus_add(major_radius=.38,minor_radius=.016,major_segments=64,minor_segments=10,location=(-3.42,1.0,3.12),rotation=(.25,.18,0));planet_ring=bpy.context.object;planet_ring.name='Partial_planet_ring_APPROX';put(planet_ring);planet_ring.data.materials.append(M['yellow'])
cur='06_Stage_Lighting_Audio'
# Moving-head lamps sit on the confirmed rear strip, aimed and colored as the wide reference.
for i,(x,y) in enumerate([(-3.85,1.48),(-2.13,2.58),(-.56,3.08),(1.80,3.08),(3.38,2.11)]):
 cube('Moving_head_%02d_base'%i,(x,y,.10),(.31,.27,.18),M['dark'],.035)
 for dx in [-.115,.115]:cube('Moving_head_%02d_yoke'%i,(x+dx,y,.25),(.035,.13,.27),M['dark'],.014)
 cyl('Moving_head_%02d_rotating_body'%i,(x,y,.20),(x,y,.44),.12,M['dark'],sides=24)
 cyl('Moving_head_%02d_lens_rim'%i,(x,y,.44),(x,y,.467),.10,M['dark'],sides=24)
 cyl('Moving_head_%02d_lens'%i,(x,y,.468),(x,y,.47),.083,M['violet'] if i%2 else M['cyan'],sides=24)
for i,(x,y) in enumerate([(-2.98,1.94),(2.35,2.58)]):
 # Sloped wedge monitors: textured grille and separate cabinet, genuine solid mesh.
 vs=[(x+dx,y+dy,z) for dx in [-.31,.31] for dy,z in [(-.19,.02),(.19,.02),(.19,.25),(-.19,.14)]]
 mesh('Wedge_monitor_%02d_cabinet'%i,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],M['dark'])
 mesh('Wedge_monitor_%02d_perforated_grille'%i,[(x-.28,y-.192,.044),(x+.28,y-.192,.044),(x+.28,y-.192,.123),(x-.28,y-.192,.123)],[(0,1,2,3)],M['grille'])
 tube('Wedge_monitor_%02d_trim'%i,[(x-.29,y-.201,.039),(x+.29,y-.201,.039),(x+.29,y-.201,.13),(x-.29,y-.201,.13),(x-.29,y-.201,.039)],.012,M['chrome'])

# Optional character-like prop, separated from all architectural anchors.
cur='08_Optional_Star_Companion';sx,sy,sz=.92,.28,1.46
star('Optional_yellow_plush_star',(sx,sy,sz),.505,.18,M['yellow'])
for xx,sgn in [(-.12,-1),(.12,1)]:
 o=cube('Star_embroidered_eye',(sx+xx,sy-.187,sz+.055),(.027,.014,.125),M['face'],.005);o.rotation_euler[1]=sgn*.18
 uvball('Star_pink_cheek',(sx+xx*1.37,sy-.180,sz-.042),(.057,.008,.022),M['blush'])
pts=[]
for i in range(33):
 x=-.067+.134*i/32;z=-.071+.035*(1-abs(sin(pi*(x+.067)/.067)))
 pts.append((sx+x,sy-.19,sz+z))
tube('Star_double_curve_smile',pts,.008,M['face'])
pts=[(sx+.014*sin(i*pi/20),sy,sz+.42+i*.0035) for i in range(26)];tube('Star_top_wisp',pts,.008,M['yellow'])
# Present but hidden: this prop moves independently during the stream.
cur='09_Optional_Moving_Balloon_Dog';dx,dy,dz=3.1,4.7,.65
for n,a,b,r in [('body',(-.7,0,.9),(.45,0,.9),.24),('neck',(-.68,0,.88),(-.94,0,1.48),.2),('head',(-.99,0,1.54),(-1.43,0,1.63),.24),('ear_a',(-1.02,-.12,1.65),(-.88,-.12,2.13),.15),('ear_b',(-1.01,.13,1.65),(-.84,.13,2.12),.15),('front_leg_a',(-.68,-.14,.72),(-.62,-.14,.10),.18),('front_leg_b',(-.68,.16,.72),(-.62,.16,.10),.18),('rear_leg_a',(.4,-.14,.75),(.47,-.14,.09),.18),('rear_leg_b',(.4,.16,.75),(.47,.16,.09),.18),('tail',(.55,0,1.02),(.84,0,1.42),.1)]:
 a=Vector(a)+Vector((dx,dy,dz));b=Vector(b)+Vector((dx,dy,dz));o=uvball('Moving_balloon_dog_'+n,(a+b)/2,(r,r,(b-a).length/2+r),M['dog']);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
C[cur].hide_render=True;C[cur].hide_viewport=True

# All city silhouettes, windows, and neon strips are editable meshes. No screenshot billboards.
cur='07_Procedural_City_Approximation'
city=[]
# Screen-space silhouette targets derived from the wide reference, then realized as volume.
for px,py,pw,y,d in [(40,392,110,13,2),(208,316,85,14,2),(274,127,96,25,2),(407,-34,159,26,2.8),(347,180,260,20,2.8),(684,337,460,15,3),(620,180,80,29,2.3),(776,99,120,28,3),(894,242,120,23,2.6),(992,305,130,18,2.6),(1130,-50,160,24,3.0),(-40,220,130,26,3),(-160,130,180,30,3),(1270,210,150,26,3)]:
 depth=y+9;u=-(py-334)/1650;dz=depth*(u*cos(math.radians(8))-sin(math.radians(8)))/(cos(math.radians(8))+u*sin(math.radians(8)));top=2.6+dz;camdepth=depth*cos(math.radians(8))-dz*sin(math.radians(8));x=(px-594)*camdepth/1650;w=pw*camdepth/1650
 city.append((x,y+d/2,w,d,top))

for k,(x,y,w,d,top) in enumerate(city):
 bot=-13;cube('City_%02d_mass_APPROX'%k,(x,y,(top+bot)/2),(w,d,top-bot),M['building'] if k%2 else M['building2'],.025)
 # Dense but non-textual window grids on front and side surfaces.
 vs=[];fs=[];ids=[]
 for side in ['front','left','right']:
  cols=max(3,int((w if side=='front' else d)/.24));rows=max(4,int((top-bot)/.40))
  for row in range(rows):
   for col in range(cols):
    if random.random()<.22:continue
    z=bot+.2+row*.40;xx=-w/2+.10+(w-.2)*(col+.5)/cols
    yy=-d/2+.10+(d-.2)*(col+.5)/cols
    if side=='front':pts=[(x+xx+qx,y-d/2-.006,z+qz) for qx,qz in [(-.067,0),(.067,0),(.067,.16),(-.067,.16)]]
    else:
     xx=x+(-w/2-.006 if side=='left' else w/2+.006);pts=[(xx,y+yy+qy,z+qz) for qy,qz in [(-.065,0),(.065,0),(.065,.16),(-.065,.16)]]
    start=len(vs);vs.extend(pts);fs.append(tuple(range(start,start+4)));ids.append(random.choices([0,1,2],[.24,.73,.03])[0])
 o=mesh('City_%02d_window_meshes'%k,vs,fs,M['window']);o.data.materials.append(M['windowdim']);o.data.materials.append(M['warmwindow'])
 for p,mi in zip(o.data.polygons,ids):p.material_index=mi
 if k in [1,3,4,5,6,7,9,10]:
  color=M['pink'] if k%2 else M['cyan'];y0=y-d/2-.018
  tube('City_%02d_roof_neon'%k,[(x-w/2,y0,top+.015),(x+w/2,y0,top+.015),(x+w/2,y+d/2,top+.015)],.015,color)
  if k in [3,7,10]:tube('City_%02d_vertical_neon'%k,[(x-w/2,y0,top-6.8),(x-w/2,y0,top)],.014,M['violet'])
# Two visible graphic chevrons, not invented text or labels.
for k,(x,y,z) in enumerate([(-1.4,20.8,-.12),(2.16,22,-.4)]):
 for j in range(2):tube('City_graphic_double_chevron',[(x+j*.18,y,z+.28),(x+j*.18+.16,y,z),(x+j*.18,y,z-.28)],.018,M['pink'])
# Stars are small remote emissive tetrahedra, an open backdrop rather than a physical room.
for i in range(105):
 x=random.uniform(-33,33);y=48;z=random.uniform(-1,24);s=random.uniform(.008,.02)
 mesh('Distant_sky_star_%03d'%i,[(x-s,y,z),(x+s,y,z),(x,y,z+s),(x,y+.01,z-s)],[(0,1,2),(0,3,1)],M['window'])

cur='10_Cameras_Studio_Lights'
def light(n,loc,power,col,size,target,kind='AREA'):
 d=bpy.data.lights.new(n,kind);d.energy=power;d.color=col
 if kind=='AREA':d.shape='DISK';d.size=size
 if kind=='SPOT':d.spot_size=size;d.spot_blend=.5;d.shadow_soft_size=.16
 o=bpy.data.objects.new(n,d);C[cur].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
light('Soft_neutral_front',(0,-4.5,5.3),560,(.65,.75,1),5,(0,0,.6))
light('Magenta_left_rim',(-3,1.1,4.5),620,(1,.12,.55),3,(0,0,.5))
light('Cyan_right_rim',(3.5,.7,4),780,(.12,.55,1),3,(0,0,.6))
light('Pale_ceilingless_soft_reflection',(0,2,6),390,(.55,.65,1),3,(0,0,1))
light('Lamp_practical',(lx,ly,2.065),22,(1,.62,.3),1,(lx,ly,0),'POINT')
for x,y,col in [(-2.1,2.6,(1,.04,.42)),(-.5,3.1,(.04,.65,1)),(1.8,3.1,(.08,.55,1)),(3.4,2.1,(.65,.06,1))]:light('Stage_light_pool',(x,y,.48),90,col,.85,(x*.72,-1.1,0),'SPOT')
def camera(n,loc,target,lens=50):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);C[cur].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.sensor_width=36;d.clip_end=250;return o
camera('MATCH_A_01h15m29s',(0,-9,2.6),(0,0,2.6-9*math.tan(math.radians(8))),50)
camera('MATCH_B_00h35m17s',(0,-4.9,2.08),(0,0,2.08-4.9*math.tan(math.radians(10.3))),50)
camera('MATCH_C_01h55m59s_no_sofas',(0,-9,2.6),(0,0,2.6-9*math.tan(math.radians(8))),50)
camera('PANORAMA_Level_Full_Component_Set',(1,-12,2.6),(0,1,1.5),40)
camera('MATCH_D_01h58m39s_empty',(0,-6.6,2.6),(0,0,2.6-6.6*math.tan(math.radians(8))),50)
camera('DETAIL_Telescope_Lamp',(-4.8,-3.1,2.6),(-1.9,2.15,1.25),50)
sc.camera=bpy.data.objects['MATCH_A_01h15m29s']
# Tag known limitations inside the native scene.
sc['source_video']='https://www.bilibili.com/video/BV1ru41147sn/'
sc['scope']='Visible city-backed stage components only. No claimed room, glazing, walls, or ceiling.'
sc['inference']='Off-camera patch depth, support/back faces, unseen attachment points and city masses are approximate.'
sc['movable_props']='Balloon dog and yellow companion are separated; default dog hidden to match 01:15:29.'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_KTV_Textured.blend')
if os.environ.get('MODEL_ONLY')=='1':
 import sys;sys.exit(0)
sc.render.filepath=ROOT+'/renders/draft5_match_A.png';bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['PANORAMA_Level_Full_Component_Set'];sc.render.filepath=ROOT+'/renders/draft5_panorama.png';bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['MATCH_B_00h35m17s'];sc.render.filepath=ROOT+'/renders/draft5_match_B.png';bpy.ops.render.render(write_still=True)
C['02_Inflated_Armchairs'].hide_render=True;C['08_Optional_Star_Companion'].hide_render=True
sc.camera=bpy.data.objects['MATCH_D_01h58m39s_empty'];sc.render.filepath=ROOT+'/renders/draft5_match_D.png';bpy.ops.render.render(write_still=True)
print('BUILD_AND_DRAFT_COMPLETE',flush=True)
