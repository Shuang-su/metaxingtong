import bpy,math,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;bpy.context.preferences.filepaths.save_version=0
s.world=bpy.data.worlds.new('world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.22,.22,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast'
def mat(n,c):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.use_fake_user=True;m.diffuse_color=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
canvas=mat('canvas_approximate',(.70,.65,.52));sand=mat('sand_approximate',(.42,.28,.14));teal=mat('bag_approximate',(.13,.24,.20));wood=mat('crate_approximate',(.29,.22,.13));dark=mat('frame',(.06,.05,.035));green=mat('lantern',(.08,.19,.09));pink=mat('roll_band',(.35,.19,.18));rock=mat('rock_proxy',(.31,.12,.06));plant=mat('plant_proxy',(.22,.24,.06));white=mat('WHITE_GEOMETRY_PERSISTENT',(.7,.7,.7))
def mesh(n,v,f,m,th=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);me.materials.append(m)
 if th:mod=o.modifiers.new('inferred_cloth_thickness','SOLIDIFY');mod.thickness=th
 return o
def cube(n,c,d,m,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bev:mod=o.modifiers.new('round_edges','BEVEL');mod.width=bev;mod.segments=3
 return o
def rod(n,a,b,r,m,vertices=12):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
def cord(n,pts,r,m,cyclic=False):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;cu.use_fill_caps=not cyclic;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1);sp.use_cyclic_u=cyclic
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);cu.materials.append(m);return o
# Conditional old working solution transcribed, not recovered exact camera JSON.
params=[[1.80367589,-19.6342555,3.75739867,4.62228463,1.29096505,2500],[6.49251467,-22.2671925,5.63611881,2.17180892,.136488499,2500]]
def camera(n,c,t,f):
 bpy.ops.object.camera_add(location=c);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=f*36/1920;o.data.sensor_width=36;o.data.sensor_fit='HORIZONTAL';o.data.clip_end=500;return o
for i,p in enumerate(params,1):camera(f'SOURCE_CONDITIONAL_{i}',p[:3],(p[3],2,p[4]),p[5])
camera('CHECK_MAIN',(-11,-13,10),(0,8,2),2350)
for i in range(8):
 a=math.tau*i/8-math.pi/2;camera(f'CHECK_{i+1:02}',(19*math.cos(a),8+19*math.sin(a),9),(0,8,2),2100)
# Shared roof-ring, old failed eave displacement explicitly NOT applied.
u=[Vector(v) for v in [(-3.3,9.5,3.89),(-.5396,8.1541,3.8916),(1.4614,6.9885,3.8774),(2.7,9.4,3.89),(1.3,12.2,3.89),(-1.99651054,10,5.49581436)]]
l=[Vector(v) for v in [(-5.2,9,1.44),(-1.9397,7.2114,1.4479),(2.6221,7.8415,1.4198),(4.3,10,1.44),(2.4,15.1,1.44),(-4.2,15,1.44)]];ap=Vector((.20156395,10.3,6.14944935))
for i in range(6):
 j=(i+1)%6;v=[];f=[];N=16
 for a in range(N+1):
  t=a/N
  for b in range(N+1):
   q=b/N;p=ap.lerp(u[i].lerp(u[j],q),t);p.z-=.1*math.sin(math.pi*q)*math.sin(math.pi*t)
   if i in [4,5]:p.z-=.1*math.sin(math.pi*t)*(q if i==4 else 1-q)
   v.append(p)
 for a in range(N):
  for b in range(N):k=a*(N+1)+b;f.append((k,k+1,k+N+2,k+N+1))
 mesh(f'T01_roof_{i}',v,f,canvas,.018);rod(f'T01_roof_hem_{i}',u[i],u[j],.027,canvas)
 if i!=1:
  v=[]
  for a in range(N+1):
   t=a/N
   for b in range(N+1):
    q=b/N;p=l[i].lerp(l[j],q).lerp(u[i].lerp(u[j],q),t);p.y-=.018*math.sin(6*math.pi*q)*math.sin(math.pi*t);v.append(p)
  mesh(f'T01_skirt_{i}',v,f,canvas,.018);mesh(f'T01_lowwall_{i}',[(l[i].x,l[i].y,0),(l[j].x,l[j].y,0),l[j],l[i]],[(0,1,2,3)],canvas,.022);rod(f'T01_waist_hem_{i}',l[i],l[j],.025,canvas)
# Closed front drape, not an observed open entrance; no dark painted opening.
bl=Vector((-.55485,7.4298,.03));br=Vector((3.3113,7.9841,.03));v=[];f=[]
for a in range(25):
 t=a/24
 for b in range(41):
  q=b/40;p=bl.lerp(br,q).lerp(u[1].lerp(u[2],q),t);p.y+=.026*math.sin(14*math.pi*q)*(1-.6*t);v.append(p)
for a in range(24):
 for b in range(40):k=a*41+b;f.append((k,k+1,k+42,k+41))
mesh('T02_front_closed_drape',v,f,canvas,.018)
mesh('T02_left_flap',[u[1],l[1],(l[1].x,l[1].y,0),bl],[(0,1,2,3)],canvas,.018);mesh('T02_right_flap',[u[2],l[2],(l[2].x,l[2].y,0),br],[(0,3,2,1)],canvas,.018)
cube('G01_ground_inferred_extent',(0,35,-.12),(160,180,.24),sand)
# Foreground box and upright crate. Crate depth offset follows its own rotation.
cube('B01_body',(0,0,.226),(.90,.50,.452),canvas,.008);cube('B01_lid',(0,0,.468),(.93,.53,.024),canvas,.004)
rl=Vector((-.846658339,5.613841762,1.525090397));rr=Vector((-.19076847,5.916957708,1.538161945));ct=(rl+rr)/2;ax=rr-rl;ax.z=0;w=ax.length;ax.normalize();back=Vector((-ax.y,ax.x,0));c=ct+back*.22;c.z=ct.z/2;crate=cube('P03_crate',c,(w,.44,ct.z),wood,.012);crate.rotation_euler.z=math.atan2(ax.y,ax.x)
for k in range(4):
 p=ct+ax*((k+.5)*w/4-w/2)-back*.015;p.z=ct.z*.49;o=cube('P03_plank_'+str(k),p,(w/4-.014,.025,ct.z*.92),wood,.004);o.rotation_euler.z=crate.rotation_euler.z
# One horizontal bag remains an occlusion hypothesis. Right-only contraction retained.
sp=lambda x:math.copysign(abs(x)**.55,x)
contract=lambda x:x-.45*max(0,min(1,(x+.55)/1.25))**1.2
v=[];f=[];N=48;M=24
for a in range(M+1):
 t=-math.pi/2+math.pi*a/M
 for b in range(N):q=math.tau*b/N;v.append((contract(-.55+1.25*sp(math.cos(t))*sp(math.cos(q))),6.65+.36*sp(math.cos(t))*sp(math.sin(q)),max(.025,.59+.59*sp(math.sin(t)))-.025))
for a in range(M):
 for b in range(N):k=a*N+b;n=a*N+(b+1)%N;f.append((k,n,n+N,k+N))
bag=mesh('P02_horizontal_bag_HYPOTHESIS',v,f,teal);bm=bmesh.new();bm.from_mesh(bag.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(bag.data);bm.free()
for x in [-.78,.78]:
 factor=(1-(abs(x)/1.25)**(2/.55))**(.55/2);pts=[]
 for k in range(64):q=math.tau*k/64;pts.append((contract(-.55+x),6.65+(.36*factor+.006)*sp(math.cos(q)),max(.022,.565+.59*factor*sp(math.sin(q)))))
 cord('P02_loop_band_'+str(x),pts,.022,canvas,True)
# Roll, cooler.
a=Vector((ct.x-1.35,ct.y-.2,.32));b=Vector((ct.x-1.05,ct.y+.02,1.62));rod('P01_roll',a,b,.32,canvas,24)
for t in [.25,.77]:p=a.lerp(b,t);d=(b-a).normalized();rod('P01_roll_band',p-d*.033,p+d*.033,.328,pink,24)
cube('P04_cooler',(3.85,8.15,.33),(1.3,.7,.66),canvas,.08);cube('P04_lid',(3.85,8.15,.69),(1.32,.72,.08),canvas,.03)
for x in [3.45,4.25]:cube('P04_band',(x,7.786,.37),(.12,.03,.64),pink,.005)
# Continuous chair surface, unchanged source-guided working frame; contact/occlusion still needs review.
cl=Vector((-1.74588376,1.18927759,1.16707911));cr=Vector((-.93583593,1.73200318,1.05366088));cx=(cl+cr)/2;axis=cr-cl;axis.z=0;axis.normalize();front=Vector((axis.y,-axis.x,0))
for side in [-1,1]:
 p=cx+axis*side*.45;rear=Vector((p.x,p.y,.025));ff=rear+front*.72;top=Vector((p.x,p.y,1.12));sf=ff.copy();sf.z=.48;rod('C01_cross_A',rear,sf,.025,dark);rod('C01_cross_B',ff,top,.025,dark)
knots=[(0,0,1.12),(.48,.18,.57),(.78,.53,.405),(1,.69,.48)];v=[];f=[]
for a in range(19):
 t=a/18
 for k in range(3):
  if knots[k][0]<=t<=knots[k+1][0]:break
 A,B=knots[k:k+2];q=(t-A[0])/(B[0]-A[0]);q=q*q*(3-2*q);off=A[1]*(1-q)+B[1]*q;z=A[2]*(1-q)+B[2]*q
 for b in range(19):u0=b/18;p=cx+axis*(u0-.5)*.9+front*off;p.z=z-math.sin(math.pi*u0)*(.045*math.sin(math.pi*t)+.075*(1-t)**3+.09*t**3);v.append(p)
for a in range(18):
 for b in range(18):k=a*19+b;f.append((k,k+1,k+20,k+19))
mesh('C01_sling',v,f,canvas,.014)
for b in [0,18]:cord('C01_side_hem',[v[a*19+b] for a in range(19)],.012,canvas)
# Lantern and genuine open cup with inner wall and floor.
rod('L01_base',(-.22,.20,.48),(-.22,.20,.54),.115,green,24);rod('L01_glass_proxy',(-.22,.20,.54),(-.22,.20,.82),.075,canvas,24);rod('L01_cap',(-.22,.20,.82),(-.22,.20,.88),.10,green,24)
for x in [-.305,-.135]:rod('L01_support',(x,.2,.53),(x,.2,.86),.011,green)
cord('L01_handle',[(-.32,.2,.84),(-.32,.2,.96),(-.22,.2,1),(-.12,.2,.96),(-.12,.2,.84)],.011,dark)
v=[];f=[]
for z,rad in [(.48,.065),(.65,.065),(.65,.052),(.495,.052)]:
 for k in range(32):q=math.tau*k/32;v.append((.14+rad*math.cos(q),.23+rad*math.sin(q),z))
for j in range(3):
 for k in range(32):n=(k+1)%32;f.append((j*32+k,j*32+n,(j+1)*32+n,(j+1)*32+k))
f.extend([tuple(reversed(range(32))),tuple(range(96,128))]);mesh('M01_open_cup',v,f,canvas)
cord('T01_guy_rope',[(4.3,10,1.44),(5.5,9.2,.06)],.018,dark);rod('T01_peg',(5.5,9.2,0),(5.5,9.2,.14),.035,wood)
# Limited nearby proxies only, not whole canyon. No massive grass scatter.
for i,(x,y,h,rad) in enumerate([(-5.8,4.5,5.9,.16),(-6.3,10.3,7,.24),(-3.9,2.9,2.5,.14),(4.9,11,7,.24),(7.4,14,2.3,.18)]):
 rod('V01_cactus_'+str(i),(x,y,0),(x,y,h),rad,plant,16)
 if i in [0,3]:rod('V01_branch',(x,y,h*.55),(x+.6,y,h*.55),rad*.65,plant);rod('V01_branch_tip',(x+.6,y,h*.55),(x+.6,y,h*.78),rad*.65,plant)
for i,(x,y,z,scale) in enumerate([(-6,7,.5,(2.2,1.1,.7)),(6.5,12,.7,(2.3,1.4,.9)),(-3.8,1,.12,(1,.65,.18))]):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,z));o=bpy.context.object;o.name='R01_rock_proxy_'+str(i);o.scale=scale;o.data.materials.append(rock)
bpy.ops.object.light_add(type='SUN',location=(0,0,12));o=bpy.context.object;o.name='shared_sun';o.rotation_euler=(.55,-.4,-.6);o.data.energy=2.2;o.data.angle=.18
s.camera=bpy.data.objects['CHECK_MAIN'];s['candidate_status']='REMADE NOT RESTORED; NOT ACCEPTED';s['working_units']='arbitrary, not metres';s['third_status']='historical source FAIL, later replay missing'
(R/'qa/C01_parameters.json').write_text(json.dumps({'camera_params_historical_working_transcription':params,'original_precise_json_missing':True,'roof_control':'conditional R08b/f control; rejected R08e eave not applied','source_status':'FAIL/PENDING','stage':'2026-11-02 remake C01 not old bytes'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C01_remade_materials.blend'))
for o in s.objects:
 if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C01_remade_white.blend'));print('C01_CHECKPOINT_SAVED',flush=True)
for name in ['SOURCE_CONDITIONAL_1','SOURCE_CONDITIONAL_2']+[f'CHECK_{i:02}' for i in range(1,9)]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/f'renders/C01_{name}_white.png');bpy.ops.render.render(write_still=True)
print('C01_LOW_VIEWS_DONE',flush=True)
