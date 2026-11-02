"""New source-backed conditional remake, not restored historical R10/R11 bytes."""
import bpy,math,json,os,random,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
os.sched_setaffinity(0,{sorted(os.sched_getaffinity(0))[-1]})
D=Path(__file__).resolve().parents[1];random.seed(20261102)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=1
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
S.world=bpy.data.worlds.new('Sky lighting inferred');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.38,.47,.65,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.7
S.view_settings.view_transform='AgX';S.unit_settings.system='NONE';S['scale_status']='Working units, NOT measured meters';S['status']='New remake of lost historical candidate, NOT source accepted';S['source_roles']='All three previously seen angles, not blind'
def mat(n,c,metal=0,rough=.6):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
red=mat('Deep red lacquer',(.5,.035,.02));orange=mat('Orange rear board',(.85,.19,.055));white=mat('Warm architectural white',(.8,.79,.77));snow=mat('Pale snowy ground approximation',(.67,.72,.79));sand=mat('Platform rose beige',(.56,.41,.34));pink=mat('Red umbrella paper',(.63,.035,.09));gold=mat('Cream ribbons',(.9,.76,.48));leaf=mat('Red visible foliage',(.48,.035,.065));sea=mat('Water environmental proxy',(.09,.28,.44),.35,.2);wm=mat('White diagnostic',(.7,.7,.7))
def tag(o,evidence='observed form; dimensions/depth conditional'):
 o['source']='BV1DZ4y1U71V P1 45.013436/15.116586 P2 32.024562';o['evidence']=evidence;return o
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);S.collection.objects.link(o);o.data.materials.append(m);tag(o);return o
def cube(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);tag(o);return o
def cylinder(n,loc,r,depth,m,vertices=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(m);tag(o);return o
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cylinder(n,(a+b)/2,r,(b-a).length,m,12);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def extrude_xz(n,poly,y,t,m):
 k=len(poly);vs=[(x,y+d,z) for d in(-t/2,t/2) for x,z in poly];fs=[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
 pts=[Vector((x,0,z)) for x,z in poly];tris=tessellate_polygon([pts]);lookup={tuple(v):i for i,v in enumerate(pts)}
 for tri in tris:
  ids=[v if isinstance(v,int) else lookup[tuple(v)] for v in tri];fs.append(tuple(reversed(ids)));fs.append(tuple(i+k for i in ids))
 return mesh(n,vs,fs,m)
def extrude_xy(n,poly,z,t,m):
 o=extrude_xz(n,poly,0,t,m)
 for v in o.data.vertices:v.co=(v.co.x,v.co.z,z+v.co.y)
 return o
# Finite open-sea environment; extent and underside are work closure, not recovered coastline.
cylinder('GROUND_finite_work_extent',(0,0,-.13),8,.26,snow,128)['evidence']='visible ground; circular outer boundary INFERRED work closure'
cube('SEA_environment_proxy',(0,18,-.32),(100,100,.08),sea)['evidence']='water backdrop proxy, not reconstructed coastline'
# Smooth lobes and finite foreground tongue; no standard five-point star assumption.
poly=[(-1.6,-7),(1.6,-7),(1.3,-1.3)]
for i in range(41):
 a=-math.pi/2+math.pi*i/40;poly.append((4.3+1.65*math.cos(a),-.7+.8*math.sin(a)))
poly += [(1.1,1.2),(0,1.45),(-1.1,1.2)]
for i in range(41):
 a=math.pi/2+math.pi*i/40;poly.append((-4.3+1.65*math.cos(a),-.7+.8*math.sin(a)))
poly += [(-1.3,-1.3)]
stage=extrude_xy('STAGE_shared_rounded_lobes',poly,.13,.24,sand);stage['evidence']='visible rounded lateral lobes, thickness conditional; front tongue and rear connections inferred, no visible frame-edge cap claim'
# Outer border is actual small tubular geometry, not composited overlay.
for i in range(len(poly)):
 a,b=poly[i],poly[(i+1)%len(poly)];rod('STAGE_edge_%03d'%i,(a[0]*.985,a[1]*.985,.258),(b[0]*.985,b[1]*.985,.258),.012,white)
# Layered screens: open notches, not texture or full-circle hole.
for sign,side in [(-1,'L'),(1,'R')]:
 cube(side+'_rear_ORANGE',(sign*4.75,3.65,1.75),(1.5,.16,3.5),orange)
 # Build left front notch opens x=-4.7 (outer side), then mirror.
 p=[(-4.7,0),(-3.5,0),(-3.5,3.12),(-4.7,3.12),(-4.7,2.65)]
 p += [(-4.7+.9*math.cos(a),1.75+.9*math.sin(a)) for a in [math.pi/2-math.pi*i/48 for i in range(49)]]
 p += [(-4.7,0)]
 p=p[:-1]
 if sign==1:p=[(-x,z) for x,z in reversed(p)]
 extrude_xz(side+'_front_NOTCHED',p,3.28,.15,red)
# Central wall with genuinely open diamond; no cap across sea view.
wall=cube('WALL_red_with_opening',(0,3.92,1.78),(6.25,.22,3.56),red)
cut=cube('temporary_diamond_cutter',(0,3.92,1.32),(3.5,1,3.5),white);cut.rotation_euler[1]=math.radians(35)
bpy.context.view_layer.objects.active=wall;mod=wall.modifiers.new('True open diamond','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for angle,y,name in [(35,3.74,'FRAME_NEAR'),(-24,4.02,'FRAME_SECOND')]:
 a=math.radians(angle);pts=[]
 for x,z in [(-1.75,-1.75),(1.75,-1.75),(1.75,1.75),(-1.75,1.75)]:pts.append((x*math.cos(a)+z*math.sin(a),y,1.32-x*math.sin(a)+z*math.cos(a)))
 for i in range(4):rod(name+'_%d'%i,pts[i],pts[(i+1)%4],.045,white)['evidence']='near white frames observed; exact cross-section/depth/pose conditional'
for x in[-3.24,3.24]:cube('WALL_white_reveal',(x,3.98,1.8),(.42,.3,3.6),white)
# Shared curved upper band and open glazed clerestory, no invented sealed roof.
for n,r0,r1,z0,z1,m in [('BAND',5.9,6.22,3.55,3.9,white),('GLASS',6.03,6.07,3.9,5.4,mat('Upper glass approximate',(.25,.38,.52),.1,.22))]:
 vs=[];fs=[];N=80
 for i in range(N+1):
  a=math.radians(15+150*i/N)
  for r,z in[(r0,z0),(r1,z0),(r1,z1),(r0,z1)]:vs.append((r*math.cos(a),-1+r*math.sin(a),z))
 for i in range(N):
  for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
 fs.extend([(3,2,1,0),(4*N,4*N+1,4*N+2,4*N+3)])
 mesh(n+'_finite_arc',vs,fs,m)['evidence']='curved upper band visible; radius/back extent/upper termination conditional, not roof'
for i in range(13):
 a=math.radians(15+150*i/12);rod('WINDOW_mullion_%02d'%i,(6.04*math.cos(a),-1+6.04*math.sin(a),3.9),(6.04*math.cos(a),-1+6.04*math.sin(a),5.4),.018,white)
for sign,side in[(-1,'L'),(1,'R')]:
 x,y=sign*5.7,1.1
 cylinder(side+'_COLUMN_core',(x,y,1.88),.43,3.76,white)
 for j in range(24):
  a=j*2*math.pi/24;cylinder(side+'_COLUMN_flute_%02d'%j,(x+.415*math.cos(a),y+.415*math.sin(a),1.88),.044,3.66,white,12)
 cylinder(side+'_COLUMN_cap',(x,y,3.78),.48,.12,gold)
 cylinder(side+'_COLUMN_foot',(x,y,.08),.48,.16,white)
# Umbrella is a circular shallow cone rigidly tilted, not squashed ellipse.
bpy.ops.object.empty_add(location=(2.6,2.75,.9));root=bpy.context.object;root.name='UMBRELLA_RIG';normal=Vector((-.55,-.35,.76)).normalized();root.rotation_euler=normal.to_track_quat('Z','Y').to_euler();root['evidence']='circular rim pose conditional from both sources; unseen handle/support unknown'
N=48;vs=[(0,0,.16)]+[(math.cos(2*math.pi*i/N),math.sin(2*math.pi*i/N),0) for i in range(N)];fs=[(0,i+1,(i+1)%N+1) for i in range(N)];o=mesh('UMBRELLA_paper',vs,fs,pink);o.parent=root;sol=o.modifiers.new('Paper thickness inferred','SOLIDIFY');sol.thickness=.008
for j in range(24):
 a=j*2*math.pi/24;o=rod('UMBRELLA_rib_%02d'%j,(0,0,.165),(math.cos(a),math.sin(a),.004),.008,gold);o.parent=root
for j in range(N):
 a,b=j*2*math.pi/N,(j+1)*2*math.pi/N;o=rod('UMBRELLA_rim_%02d'%j,(math.cos(a),math.sin(a),0),(math.cos(b),math.sin(b),0),.012,gold);o.parent=root
# Gifts: each independently editable, ribbons actual geometry. Side small gift observed left.
for name,x,y,w,h in [('L_MAIN',-4,2.65,.62,.36),('L_SMALL',-4.15,2.23,.24,.22),('R_MAIN',3.95,2.65,.5,.54)]:
 cube('GIFT_'+name,(x,y,h/2),(w,w*.65,h),orange)
 cube('GIFT_'+name+'_ribbon_front',(x,y-w*.33-.006,h/2),(.045,.014,h+.02),gold)
 cube('GIFT_'+name+'_ribbon_top',(x,y,h+.012),(.045,w*.68,.024),gold)
 for dx in[-.1,.1]:
  o=rod('GIFT_'+name+'_bow',(x,y,h+.03),(x+dx,y,h+.12),.045,white)
# Red cubic clusters. Counts/depth are conditional where cropped.
for sign in[-1,1]:
 for j,(w,dx,dy) in enumerate([(.58,0,0),(.38,.55,.1),(.25,.85,.08),(.45,-.45,-.05)]):
  c=Vector((sign*(5.6+dx),.5+dy,w*.6));o=cube('RED_CUBE_%s_%s'%(sign,j),c,(w,w,w),red);o.rotation_euler=(.12,.25,sign*.35)
# Visible red planting: explicit stylized leaf meshes, not source photo cards.
for k,(x,y) in enumerate([(-3.5,3),(-3.2,3),(-4.7,2.7),(3.35,3),(3.7,3),(4.3,2.9)]):
 for j in range(7):
  xx=x+random.uniform(-.3,.3);yy=y+random.uniform(-.3,.3);h=random.uniform(.25,.85);rod('PLANT_stem_%d_%d'%(k,j),(xx,yy,0),(xx,yy,h),.012,leaf)
  for q in range(5):
   z=.1+h*q/5;a=random.random()*6.28;r=.11;mesh('PLANT_leaf',[(xx,yy,z),(xx+r*math.cos(a),yy+r*math.sin(a),z+.07),(xx+2*r*math.cos(a),yy+2*r*math.sin(a),z+.03),(xx+r*math.cos(a),yy+r*math.sin(a),z-.03)],[(0,1,2,3)],leaf)
# Fixed conditional cameras; no per-camera visibility changes.
def camera(n,loc,target,lens):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.sensor_width=36;return o
cams=[camera('SOURCE_P1_45',(0,-8.5,3.7),(0,2.5,1.65),24),camera('SOURCE_P2_32',(-1.9,-7.3,3.5),(.6,3,1.8),25),camera('SOURCE_P1_15',(1.7,-7.2,3.6),(-.6,3,1.7),25)]
S.camera=cams[0]
bpy.ops.object.light_add(type='AREA',location=(0,-3,8));o=bpy.context.object;o.name='Inferred broad key';o.data.energy=1700;o.data.shape='DISK';o.data.size=9
bpy.ops.object.light_add(type='SUN',location=(0,0,8));o=bpy.context.object;o.data.energy=1.4;o.rotation_euler=(.4,-.3,-.5)
# Ensure mesh normals, preserve stage actual initial artifact.
for o in list(S.objects):
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R01_material.blend'))
(D/'models/R01_inventory.json').write_text(json.dumps([{'name':o.name,'type':o.type,'evidence':o.get('evidence','conditional lighting/camera'),'vertices':len(o.data.vertices) if o.type=='MESH' else 0} for o in S.objects],ensure_ascii=False,indent=2))
bpy.ops.export_scene.gltf(filepath=str(D/'models/R01_material.glb'),export_format='GLB',export_cameras=True,export_lights=False)
for o in S.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(wm)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R01_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(D/'models/R01_white.glb'),export_format='GLB',export_cameras=True,export_lights=False)
print('R01_MODEL_CHECKPOINT_SAVED',flush=True)
