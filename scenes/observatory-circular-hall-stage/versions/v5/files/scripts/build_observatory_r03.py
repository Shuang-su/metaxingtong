"""First explicit structural hypothesis from article stills; no native-frame calibration."""
import bpy,bmesh,math,json,pathlib,hashlib,random
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];random.seed(531)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,rough=.45,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*c,1);q.inputs['Roughness'].default_value=rough;q.inputs['Metallic'].default_value=metal;return m
clay=mat('WHITE_clay',(.7,.7,.7),.8);blue=mat('Blue_structural',(.12,.18,.32),.4,.35);dark=mat('Dark_floor',(.06,.08,.16),.23,.5);gold=mat('Gold_inlay',(.42,.32,.14),.3,.7);pale=mat('Pale_window_rim',(.44,.52,.68),.4,.3);veg=mat('Pink_growth_proxy',(.38,.16,.36),.85);rock=mat('Small_rock_proxy',(.16,.14,.2),.9)
def mesh(n,v,f,m,note='Dimensions and hidden cross-section inferred from uncalibrated article images'):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m);o['evidence_limit']=note
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();return o
def box(n,loc,scale,m,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;o.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);o['evidence_limit']='Observed family; position/size/cross-section provisional';return o
def ring(n,ri,ro,z,h,m,N=128):
 v=[(r*math.cos(a*math.tau/N),r*math.sin(a*math.tau/N),zz) for zz in (z,z+h) for r in (ri,ro) for a in range(N)];f=[]
 for i in range(N):j=(i+1)%N;f += [(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
 return mesh(n,v,f,m)
def disk(n,r,z,h,m,N=128):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=h,location=(0,0,z+h/2));o=bpy.context.object;o.name=n;o.data.materials.append(m);o['evidence_limit']='Finite solid thickness inferred';return o
def tube(n,points,r,m,sides=8):
 v=[];f=[]
 for k,p in enumerate(points):
  t=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)]);q=t.to_track_quat('Z','Y')
  v += [tuple(Vector(p)+q@Vector((r*math.cos(i*math.tau/sides),r*math.sin(i*math.tau/sides),0))) for i in range(sides)]
 for k in range(len(points)-1):
  for i in range(sides):a=k*sides+i;b=k*sides+(i+1)%sides;f.append((a,b,b+sides,a+sides))
 f += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))];return mesh(n,v,f,m)
def plane_pos(x,z,a,r):return (r*math.cos(a)-x*math.sin(a),r*math.sin(a)+x*math.cos(a),z)
def frame(n,outer,inner,a,r,d,m):
 # Same radial ordering, four boundary loops: truly open centre, solid jamb thickness.
 N=len(inner);v=[plane_pos(x,z,a,rr) for rr in (r-d/2,r+d/2) for loop in (outer,inner) for x,z in loop];f=[]
 for i in range(N):j=(i+1)%N;f.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 return mesh(n,v,f,m,'True opening; shape approximate, no opaque fake window decal')
def arch(n,a,r,w,bottom,spring,d,m):
 # U outline, open down to floor; inner/outer semicircles connected through jamb bases.
 inner=[(-w,bottom),(-w,spring)]+[(w*math.cos(math.pi-i*math.pi/24),spring+w*math.sin(math.pi-i*math.pi/24)) for i in range(1,25)]+[(w,bottom)]
 outer=[(-w-.18,bottom),(-w-.18,spring)]+[((w+.18)*math.cos(math.pi-i*math.pi/24),spring+(w+.18)*math.sin(math.pi-i*math.pi/24)) for i in range(1,25)]+[(w+.18,bottom)]
 outline=outer+list(reversed(inner));N=len(outline)
 v=[plane_pos(x,z,a,rr) for rr in (r-d/2,r+d/2) for x,z in outline];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]
 for j in range(N):k=(j+1)%N;f.append((j,k,N+k,N+j))
 o=mesh(n,v,f,m,'U-shaped open portal with finite cross-section, dimensions inferred')
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
# Finite open terrace and enclosed circular hall. Units arbitrary, not metres.
disk('TERRACE_finite_base',11,-.4,.4,blue);disk('HALL_floor_solid',6.3,0,.4,blue);disk('DANCE_floor',4.75,.4,.08,dark)
for i,(r,z) in enumerate([(6.7,0),(6.5,.14),(6.3,.28)]):ring('HALL_step_%02d'%i,6.12,r,z,.14,blue)
for i,r in enumerate([2.8,4.2,4.65]):ring('FLOOR_gold_ring_%02d'%i,r,r+.025,.481,.012,gold)
# Five-point hollow inlay (not floating star solid).
outer=[];inner=[]
for i in range(10):
 a=math.pi/2+i*math.pi/5;r=3 if i%2==0 else 1.25;outer.append((r*math.cos(a),r*math.sin(a)));r-=.13;inner.append((r*math.cos(a),r*math.sin(a)))
v=[(x,y,z) for z in (.481,.495) for loop in (outer,inner) for x,y in loop];f=[]
for i in range(10):j=(i+1)%10;f += [(i,j,10+j,10+i),(20+i,30+i,30+j,20+j),(i,20+i,20+j,j),(10+i,10+j,30+j,30+i)]
mesh('FLOOR_five_star_inlay',v,f,gold)
# Twelve-bay hypothesis: opposite door axes, ten tall real keyhole/capsule openings.
for k in range(12):
 a=-math.pi/2+k*math.tau/12;r=6;half=6*math.tan(math.pi/12);zc=3.22
 if k in (0,6):
  w=1.05; spring=3.0
  for side in (-1,1):
   x=side*(half+w)/2;o=box('DOOR_%02d_jamb_%d'%(k,side),plane_pos(x,2.95,a,r),(half-w,.32,5.1),blue,a+math.pi/2)
  # Above arch segments follow actual curved opening boundary, no across-opening slab.
  vv=[];ff=[];N=40
  for j in range(N+1):
   x=-w+2*w*j/N;low=spring+math.sqrt(max(0,w*w-x*x));vv += [plane_pos(x,z,a,rr) for rr,z in [(r-.16,low),(r+.16,low),(r-.16,5.5),(r+.16,5.5)]]
  for j in range(N):b=4*j;c=b+4;ff += [(b,c,c+1,b+1),(b+2,b+3,c+3,c+2),(b,b+2,c+2,c),(b+1,c+1,c+3,b+3)]
  ff += [(0,1,3,2),(4*N,4*N+2,4*N+3,4*N+1)];mesh('DOOR_%02d_upper'%k,vv,ff,blue);arch('DOOR_%02d_gold_arch'%k,a,r-.18,w,.4,spring,.05,gold)
 else:
  # Ray parameterization keeps outer rectangular edge aligned with inner profile.
  # Genuine keyhole aperture: broad circular head merges into narrow rounded stem.
  stem=.25; crown=.55; cz=4.36; bz=1.35;theta=math.acos(stem/crown)
  inn=[(stem,bz),(stem,cz-crown*math.sin(theta))]
  for j in range(1,49):
   t=-theta+(math.pi+2*theta)*j/48;inn.append((crown*math.cos(t),cz+crown*math.sin(t)))
  inn.append((-stem,bz))
  for j in range(1,25):
   t=math.pi+math.pi*j/24;inn.append((stem*math.cos(t),bz+stem*math.sin(t)))
  inn=inn[:-1] # Closing vertex is represented once, avoiding a zero-length edge.
  out=[]
  for x,z in inn:
   dz=z-2.95;scale=min(half/max(abs(x),1e-9),2.55/max(abs(dz),1e-9));out.append((x*scale,2.95+dz*scale))
  frame('WALL_%02d_perforated'%k,out,inn,a,r,.32,blue)
  rim=[(x*1.13,2.95+(z-2.95)*1.025) for x,z in inn];frame('WINDOW_%02d_gold_lip'%k,rim,inn,a,r-.19,.055,gold)
  # No glass: source transparency vs open aperture unverified, explicitly pending.
 # ribs at bay boundaries span floor to roof; finite width.
 aa=a+math.pi/12;o=box('COLUMN_%02d'%k,(6.15*math.cos(aa),6.15*math.sin(aa),2.95),(.23,.32,5.1),blue,aa)
# Continuous upper and bottom rings, dome thickness explicit, internal rear unseen inferred.
ring('WALL_lower_sill',5.84,6.18,.4,.16,blue)
ring('ROOF_drum',5.8,6.35,5.5,.3,blue);ring('ROOF_gold_cornice',6.23,6.4,5.58,.08,gold)
# Dome uses closed surface of revolution with hollow underside, apex cap.
N=96;profile=[(6.3,5.8),(5.8,6.0),(4.8,6.35),(3.2,6.75),(.25,7.1),(.25,6.95),(3.2,6.6),(4.8,6.2),(5.8,5.85),(6.3,5.65)];v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for r,z in profile for i in range(N)];f=[]
for j in range(len(profile)):
 for i in range(N):ii=(i+1)%N;jj=(j+1)%len(profile);f.append((j*N+i,j*N+ii,jj*N+ii,jj*N+i))
mesh('ROOF_hollow_dome',v,f,blue);disk('ROOF_apex_cap',.25,6.95,.15,blue)
for k in range(24):
 a=k*math.tau/24;tube('ROOF_radial_rib_%02d'%k,[(r*math.cos(a),r*math.sin(a),z+.03) for r,z in profile[:5]],.035,pale)
# Observed pointed roof centre ornament, uncertain exact twist/height; finite solid proxy.
bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=.34,radius2=.035,depth=.85,location=(0,0,7.525));o=bpy.context.object;o.name='ROOF_centre_spire';o.data.materials.append(pale);o['evidence_limit']='Roof tip visible in report15; simple untwisted proxy, exact shape unknown'
# Separate exterior rings and portal structures visibly supported on terrace.
for k in range(4):
 a=-math.pi/2+k*math.pi/2;arch('TERRACE_portal_%02d'%k,a,9.3,1.15,0,1.8,.3,pale)
 for rr in (8.8,10.1):
  # Whole rings visible in wide image; portal connection details inferred.
  pass
for i,r in enumerate([7.6,9.9,10.65]):ring('TERRACE_inlay_%02d'%i,r,r+.035,.002,.015,gold)
# Four buttress gantries; number/backside arrangement hypothesis from front two in exterior still.
for k in range(4):
 a=math.pi/4+k*math.pi/2
 tube('EXTERIOR_brace_%02d'%k,[(8.0*math.cos(a),8.0*math.sin(a),.08),(7.6*math.cos(a),7.6*math.sin(a),4.75),(6.25*math.cos(a),6.25*math.sin(a),5.25)],.18,blue,8)
# Small observed ring vegetation and rocks are provisional placeholders, not source-count matched.
for k in range(100):
 a=k*math.tau/100;r=5.1+random.uniform(-.08,.2)
 tube('RING_growth_%03d'%k,[(r*math.cos(a),r*math.sin(a),.4),(r*math.cos(a)+random.uniform(-.1,.1),r*math.sin(a)+random.uniform(-.1,.1),.4+random.uniform(.1,.3))],.018,veg,5)
for k in range(12):
 a=k*math.tau/12;box('UPLIGHT_%02d'%k,(4.9*math.cos(a),4.9*math.sin(a),.52),(.35,.17,.16),pale,a)
# Cameras are first uncalibrated hypotheses, identical geometry/state across all.
def cam(n,loc,target,lens=45):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=500;o['calibration']='NOT FIT / FAILED';return o
cam('SOURCE_13_high',(1,-5.4,4.4),(0,.5,.6),22);cam('SOURCE_14_front',(0,-4.9,2.1),(0,3.5,2.4),21);cam('SOURCE_15_exterior',(0,-24,11),(0,0,2.6),38);cam('SOURCE_21_high',(-2.2,-5,4.8),(0,.2,.6),22)
for i in range(8):
 a=i*math.tau/8
 if i<4:cam('CHECK_%02d'%(i+1),(18*math.cos(a),18*math.sin(a),9 if i%2 else 13),(0,0,2),35)
 else:cam('CHECK_%02d'%(i+1),(4.3*math.cos(a),4.3*math.sin(a),3.8),(0,0,2.2),20)
cam('MAIN_exterior',(17,-20,12),(0,0,2.5),40)
for n,loc,power,size in [('SKY_fixed',(0,0,10),2300,10),('INTERIOR_fixed',(0,0,5.1),450,4),('FRONT_fixed',(0,-12,9),1800,8)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.12,.22,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.view_settings.view_transform='AgX';s.camera=bpy.data.objects['MAIN_exterior'];s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100
s['status']='UNACCEPTED structural candidate; article stills only; unknown timestamps and highest native quality';s['unit_note']='arbitrary working units, no metric scale'
for mode in ['material','white']:
 if mode=='white':
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/('R03_'+mode+'.blend')))
 bpy.ops.export_scene.gltf(filepath=str(P/'models'/('R03_'+mode+'.glb')),export_format='GLB',export_cameras=True,export_extras=True)
print('BUILD_FINISHED')
