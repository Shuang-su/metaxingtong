import bpy,math,json,hashlib,pathlib,random
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials):bpy.data.materials.remove(d)
def mat(n,c,metal=0,rough=.5,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 return m
wood=mat('WOOD_proxy',(.12,.046,.02));black=mat('DARK_metal',(.025,.024,.022),.65);gold=mat('BRASS_proxy',(.23,.12,.035),.75);white=mat('FABRIC_white',(.72,.7,.65));green=mat('CURTAIN_green',(.013,.065,.055));red=mat('GARMENT_red_proxy',(.16,.028,.014));bulb=mat('BULB_warm',(.9,.72,.43),0,.3,2);mirror=mat('MIRROR_actual_reflection_not_duplicate_lights',(.82,.82,.82),1,.035);glass=mat('COSMETIC_dark_green',(.015,.09,.047),.1,.2);pink=mat('COSMETIC_pink',(.39,.1,.12));pearl=mat('PEARL_proxy',(.65,.62,.52),.1,.2);clay=mat('WHITE_clay',(.45,.45,.45))
def finish(o,n,m):o.name=n;o.data.materials.append(m);return o
def box(n,loc,dim,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,m)
def sphere(n,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return finish(o,n,m)
def rod(n,a,b,r,m,verts=16):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,n,m)
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);finish(o,n,m);return o
# No fabricated room enclosure. Only local visible assemblages; all scales and unseen construction inferred.
box('TABLE_top', (0,0,.78),(3.2,.9,.065),wood)
for i,x in enumerate([-1.35,1.35]):
 for j,y in enumerate([-.32,.32]):box(f'TABLE_leg_inferred_{i}_{j}',(x,y,.38),(.07,.07,.76),wood)
box('TABLE_apron_inferred',(0,.25,.66),(2.75,.07,.2),wood)
box('MIRROR_backboard_inferred',(0,.43,1.57),(2.65,.08,1.55),wood)
box('MIRROR_surface',(0,.38,1.57),(2.37,.012,1.29),mirror)
for side in [-1,1]:
 box(f'MIRROR_frame_{side}',(side*1.26,.34,1.57),(.15,.14,1.55),wood)
 # Count is a proxy; reflections excluded from independent count.
 for j in range(5):
  z=1.02+j*.275;rod(f'BULB_socket_{side}_{j}',(side*1.26,.35,z),(side*1.26,.22,z),.045,black)
  sphere(f'BULB_one_physical_instance_{side}_{j}',(side*1.26,.17,z),(.073,.073,.073),bulb)
for z in [.83,2.31]:box(f'MIRROR_frame_horizontal_{z}',(0,.34,z),(2.65,.14,.08),wood)
box('COSMETIC_case_body',(-.45,.08,1.0),(.58,.27,.36),black)
for x in [-.66,-.24]:rod('CASE_handle_leg_'+str(x),(x,.08,1.19),(x,.08,1.25),.012,gold)
rod('CASE_handle_bar',(-.66,.08,1.25),(-.24,.08,1.25),.012,gold)
# Source-supported categories, approximate counts and positions retained as hypotheses.
rr=random.Random(803)
for i in range(17):
 x=(-1.1+i*.075) if i<9 else (.35+(i-9)*.1);y=.05+rr.uniform(-.23,.15);h=rr.uniform(.07,.21);r=rr.uniform(.022,.046)
 rod(f'COSMETIC_bottle_proxy_{i}',(x,y,.815),(x,y,.815+h),r,glass if i%3 else pink)
 rod(f'COSMETIC_cap_proxy_{i}',(x,y,.815+h),(x,y,.84+h),r*.8,black)
for i in range(32):
 t=2*math.pi*i/32;sphere(f'NECKLACE_pearl_proxy_{i}',(-.8+.22*math.cos(t),-.24+.12*math.sin(t),.833),(.013,.013,.013),pearl)
box('CLOCK_red_case_proxy',(.63,.2,.955),(.36,.1,.25),red);box('CLOCK_blank_face_unread_numbers',(.63,.144,.955),(.3,.015,.19),pearl)
box('CHAIR_seat_proxy',(0,-.73,.48),(.55,.53,.10),black);box('CHAIR_back_proxy',(0,-.98,.83),(.55,.1,.65),black)
for x in [-.22,.22]:
 for y in [-.92,-.53]:rod('CHAIR_leg_inferred', (x,y,.03),(x,y,.45),.022,black)
# Separate working arrangement, NOT established room layout or proven same umbrella pose.
uc=Vector((2.0,1.5,2.35));axis=Vector((0,-.85,-.3)).normalized();u=Vector((1,0,0));v=axis.cross(u).normalized();rings=7;N=32;vs=[]
for inner in [False,True]:
 for k in range(rings):
  r=.025+(1.05-.025)*k/(rings-1);dep=.27*(1-(r/1.05)**1.4)
  for j in range(N):
   t=2*math.pi*j/N;vs.append(tuple(uc+u*(r*math.cos(t))+v*(r*math.sin(t))+axis*(dep+(.008 if inner else 0))))
fs=[];L=rings*N
for layer in range(2):
 for k in range(rings-1):
  for j in range(N):
   a=layer*L+k*N+j;b=layer*L+k*N+(j+1)%N;c=b+N;d=a+N;fs.append((a,b,c,d) if layer==0 else(d,c,b,a))
for k in [0,rings-1]:
 for j in range(N):
  a=k*N+j;b=k*N+(j+1)%N;fs.append((a,a+L,b+L,b) if k==0 else(a,b,b+L,a+L))
o=mesh('UMBRELLA_finite_canopy_proxy',vs,fs,white)
# Normalize shell normals rather than rely on construction winding.
bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
for j in range(8):
 t=2*math.pi*j/8;last=uc+axis*.27
 for k in range(1,7):
  r=1.05*k/6;q=uc+u*(r*math.cos(t))+v*(r*math.sin(t))+axis*(.27*(1-(r/1.05)**1.4)+.014);rod(f'UMBRELLA_rib_{j}_{k}',last,q,.006,black,8);last=q
rod('UMBRELLA_hub',tuple(uc-axis*.13),tuple(uc+axis*.35),.023,black)
rod('UMBRELLA_stand_inferred',(2,1.5,.05),tuple(uc-axis*.13),.022,black)
for j in range(3):
 t=j*2*math.pi/3;rod('UMBRELLA_foot_inferred',(2,1.5,.22),(2+.45*math.cos(t),1.5+.45*math.sin(t),.03),.016,black)
for x in [.75,3.25]:rod('RACK_post_proxy',(x,2.8,.03),(x,2.8,2.0),.018,gold)
rod('RACK_horizontal',(.65,2.8,1.9),(3.35,2.8,1.9),.018,gold)
for i,x in enumerate([1,1.45,1.9,2.35,2.8]):
 # Finite simplified silhouette, not original dress pattern or mannequin measurements.
 rod(f'HANGER_{i}',(x-.18,2.8,1.72),(x,2.8,1.87),.009,black,8);rod(f'HANGER_{i}b',(x,2.8,1.87),(x+.18,2.8,1.72),.009,black,8)
 box(f'GARMENT_finite_proxy_{i}',(x,2.8,1.15),(.4,.07,1.12),red)
# Curtain only: not a room wall. Limited width and hidden support inferred.
for i in range(28):
 x=-2+i*.22;sphere(f'CURTAIN_fold_proxy_{i}',(x,3.15,1.55),(.13,.07,1.55),green)
# No room floor, walls, ceiling, unknown neighbors or characters are invented.
world=bpy.data.worlds.new('Study_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;bpy.context.scene.world=world
def look(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light(n,loc,power,size,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;look(o,target)
light('DIAGNOSTIC_key',(-3,-3,4),500,4,(0,0,1));light('DIAGNOSTIC_fill',(4,-1,3),350,3,(1,1,1))
for n,loc,target in [('MAIN_local',(-4,-5,3),(0.7,1,1.3)),('TABLE_high',(-2,-2,3.1),(0,0,1)),('TABLE_front',(2,-3,1.7),(0,0,1.2)),('RACK_local',(4,-2,2.4),(2,2.7,1.4))]:
 d=bpy.data.cameras.new(n);d.lens=40;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;look(o,target)
s=bpy.context.scene;s.camera=bpy.data.objects['MAIN_local'];s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
s['scope']='Local assemblage research, not whole room; source correspondence FAILED; report screenshots not native; positions inferred'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/R01_material.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models/R01_material.glb'),export_format='GLB',export_cameras=True)
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/R01_white.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models/R01_white.glb'),export_format='GLB',export_cameras=True)
print('LOCAL_STUDY_MESHES',sum(o.type=='MESH' for o in bpy.data.objects))
