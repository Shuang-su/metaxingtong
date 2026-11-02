# NEW Nov2 adaptation of visible historical M03 construction; not original-script byte recovery.
# Saves editable checkpoints before rendering. No missing original PNG/model dependency.
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parents[1];P=json.load(open(D/'parameters.json'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Neutral inspection world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.2,.25,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6;s.view_settings.view_transform='Standard'
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=.48;return m
mats={'stone':mat('conditional_pale_stone',(.48,.51,.58)),'base':mat('conditional_base_blue',(.22,.27,.37)),'gold':mat('conditional_muted_gold',(.39,.24,.08),.65),'lattice':mat('conditional_teal_frame',(.055,.17,.19),.15),'dark':mat('conditional_diagonal_dark',(.09,.1,.13)),'floor':mat('module_cut_floor',(.19,.22,.28)),'white':mat('WHITE_SHARED',(.65,.65,.65))};items=[]
def finish(o,n,key,role):
 o.name=n;o.data.materials.append(mats[key]);o['evidence_role']=role;items.append({'name':n,'material':key,'role':role});return o
def cube(n,loc,dim,key,role):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,key,role)
span=P['span'];rad=P['local_curve_radius'];edge=rad-math.sqrt(rad*rad-(span/2)**2)
def cy(x):return rad-math.sqrt(rad*rad-(x-span/2)**2)-edge
def bar(n,a,b,width,depth,key,role):
 a=Vector((a[0],cy(a[0])+.1,a[1]));b=Vector((b[0],cy(b[0])+.1,b[1]));d=b-a;o=cube(n,(a+b)/2,(width,depth,d.length),key,role);t=d.normalized();normal=Vector((0,1,0));normal=(normal-t*normal.dot(t)).normalized();u=normal.cross(t);o.rotation_euler=Matrix((u,normal,t)).transposed().to_euler()
 if n.startswith('CROSS_'):o.location.y+=.02
 return o

def sweep(n,zlo,zhi,depth,key):
 v=[];faces=[];N=32
 for i in range(N+1):
  x=-.22+(span+.44)*i/N;y=cy(x);v += [(x,y-depth/2,zlo),(x,y+depth/2,zlo),(x,y+depth/2,zhi),(x,y-depth/2,zhi)]
 for i in range(N):
  for j in range(4):a=i*4+j;b=i*4+(j+1)%4;faces.append((a,b,b+4,a+4))
 faces += [(3,2,1,0),tuple(N*4+j for j in range(4))];me=bpy.data.meshes.new(n);me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);return finish(o,n,key,'historical interpreted layered band; thickness/local curve inferred')
cube('FLOOR_finite_module_cut',(1.5,0,-.08),(4.4,1.6,.16),'floor','finite cut support slab, not source site edge')
for j,x in enumerate([0,span]):
 y=cy(x);prefix=f'COL_{j}'
 for k,(z,h,w) in enumerate([(.06,.12,.62),(.15,.06,.54),(.205,.05,.46)]):cube(prefix+f'_base_{k}',(x,y,z),(w,w,h),'base','stepped base hypothesis, dimensions inferred')
 cube(prefix+'_shaft',(x,y,(.23+4.25)/2),(.36,.36,4.25-.23),'stone','pale square shaft; hidden depth inferred')
 for k,z in enumerate([3.2,3.78,4.2]):cube(prefix+f'_band_{k}',(x,y,z),(.39,.39,.035),'gold','narrow band hypothesis')
 cube(prefix+'_capital',(x,y,4.3),(.48,.48,.1),'stone','conditional top bearing cap, hidden joinery unknown')
sweep('BEAM_main_solid',3.78,4.03,.34,'stone');sweep('BEAM_lower_rail',3.17,3.23,.22,'stone');sweep('BEAM_grille_top',3.70,3.78,.24,'gold');sweep('BEAM_cross_band_backing',4.03,4.24,.22,'stone');sweep('BEAM_top_cap',4.24,4.31,.42,'base')
for i in range(12):
 x0=.03+i*(span-.06)/12;x1=.03+(i+1)*(span-.06)/12
 bar(f'CROSS_{i}_A',(x0,4.04),(x1,4.23),.018,.025,'dark','crossed lines interpreted as rods; not proven structural')
 bar(f'CROSS_{i}_B',(x0,4.23),(x1,4.04),.018,.025,'dark','same geometry in every view')
count=P['grille_motif_count'];left=.2;right=span-.2;pitch=(right-left)/count
for i in range(count):
 x0=left+i*pitch+.018;x1=left+(i+1)*pitch-.018;z0=3.25;z1=3.67;name=f'GRILLE_{i}'
 for k,(a,b) in enumerate([((x0,z0),(x1,z0)),((x1,z0),(x1,z1)),((x1,z1),(x0,z1)),((x0,z1),(x0,z0))]):bar(name+f'_frame{k}',a,b,.045,P['grille_back_depth'],'lattice','actual geometric opening; pattern not source accepted')
 # Nov1 M03 minimal inferred end connections retained, not the earlier floating L trial.
 bar(name+'_inner_top',(x0+.07,z1-.09),(x1,z1-.09),.035,.13,'gold','minimum inferred connection to right frame')
 bar(name+'_inner_bottom',(x0,z0+.09),(x1-.07,z0+.09),.035,.13,'gold','minimum inferred connection to left frame')
 bar(name+'_stem_L',(x0+.07,z0+.09),(x0+.07,z0+.24),.035,.13,'gold','inferred pattern continuation')
 bar(name+'_stem_R',(x1-.07,z1-.09),(x1-.07,z1-.24),.035,.13,'gold','inferred pattern continuation')
paths=[[(.18,3.17),(.86,3.17),(.86,3.02),(.68,3.02),(.68,2.86),(.48,2.86),(.48,2.69),(.18,2.69)],[(.18,3.02),(.51,3.02),(.51,2.87),(.32,2.87),(.32,2.74)]]
for side in [0,1]:
 for j,path in enumerate(paths):
  path=[(x if side==0 else span-x,z) for x,z in path]
  for k in range(len(path)-1):bar(f'BRACKET_{side}_{j}_{k}',path[k],path[k+1],.065,P['bracket_back_depth'],'stone','open stepped corner hypothesis; back/internal joins unverified')
for name,loc,power,size in [('KEY',(1,4,7),550,5),('FILL',(-3,-2,5),250,4)]:
 l=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((1.5,0,2))-o.location).to_track_quat('-Z','Y').to_euler();l.energy=power;l.shape='DISK';l.size=size
# Only internal inspection cameras. Failed old source cameras are NOT promoted or relabelled.
for i in range(8):
 a=i*math.pi/4;c=bpy.data.cameras.new('CHECK'+str(i));o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=(1.5+7*math.sin(a),7*math.cos(a),4.3);o.rotation_euler=(Vector((1.5,0,2.1))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=6.5 if i in [2,6] else 5.8
s.camera=bpy.data.objects['CHECK1'];s.render.resolution_x=640;s.render.resolution_y=640
(D/'qa/object-inventory.json').write_text(json.dumps(items,indent=2))
for typ in ['material','white']:
 if typ=='white':
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(mats['white'])
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/NOV2_CP01_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/NOV2_CP01_{typ}.glb'),export_format='GLB')
files=list((D/'models').glob('NOV2_CP01_*'));(D/'qa/checkpoint-files.json').write_text(json.dumps({'status':'new editable checkpoint, not old binary recovery; source images/depth/acceptance pending','files':[{'path':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]},indent=2))
print('NEW EDITABLE CHECKPOINT SAVED BEFORE RENDER')
