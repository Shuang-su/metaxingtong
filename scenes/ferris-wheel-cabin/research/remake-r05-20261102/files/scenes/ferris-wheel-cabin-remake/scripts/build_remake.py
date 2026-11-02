"""NEW Nov2 remake implementation. Not recovered R08b source. Model units inferred."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.world.color=(.16,.19,.25);s.view_settings.view_transform='AgX'
def mat(name,color,metal=0,rough=.4):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
red=mat('deep red enamel',(.31,.009,.016),.25,.3);cream=mat('ivory casing',(.72,.61,.39),.12,.33);black=mat('black brown gasket',(.022,.012,.010),.2,.35);brass=mat('brass trim',(.50,.24,.075),.8,.23);seat=mat('red seat upholstery',(.39,.012,.015),0,.5);floor=mat('red textured floor approximate',(.20,.022,.018),.12,.57);white=mat('persisted neutral white',(.63,.63,.63),0,.72)
ledger=[];apertures=[]
P=[(-1.12,-1.85),(1.12,-1.85),(1.62,-1.35),(1.62,1.35),(1.12,1.85),(-1.12,1.85),(-1.62,1.35),(-1.62,-1.35)]
def mesh(name,vs,fs,m,note='inferred dimensions; source existence only',group='structure'):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(m);o['source_status']=note;o['qa_group']=group;ledger.append({'name':name,'group':group,'source_status':note});return o
def box(name,center,size,m,bevel=0,group='structure'):
 x,y,z=center;a,b,c=[v/2 for v in size];vs=[(x+i*a,y+j*b,z+k*c) for k in [-1,1] for j in [-1,1] for i in [-1,1]];fs=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)];o=mesh(name,vs,fs,m,group=group)
 if bevel:
  mod=o.modifiers.new('small physical edge radius','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('weighted corner normals','WEIGHTED_NORMAL')
 return o
# Local basis x=tangent, y=outward normal, z=up. Bounds and wall/frames shared across all views.
def basis(i):
 a=Vector((*P[i],0));b=Vector((*P[(i+1)%8],0));u=(b-a).normalized();return (a+b)/2,u,Vector((u.y,-u.x,0)),(b-a).length

def transform(o,origin,u,n):
 for v in o.data.vertices:
  q=v.co.copy();v.co=origin+u*q.x+n*q.y+Vector((0,0,q.z))
 return o

def localbox(name,c,sz,m,O,U,N,bevel=0,group='structure'):return transform(box(name,c,sz,m,bevel,group),O,U,N)
def rounded(w,h,r):
 out=[]
 for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for j in range(9):
   a=math.radians(start+j*90/8);out.append((cx+r*math.cos(a),cz+r*math.sin(a)))
 return out

def ring(name,center,outer,inner,rout,rin,depths,m,O,U,N,group='structure'):
 out=rounded(*outer,rout);inn=rounded(*inner,rin);v=[]
 for depth in depths:
  for loop in [out,inn]:v.extend([(center[0]+x,depth,center[1]+z) for x,z in loop])
 n=len(out);f=[]
 for j in range(n):
  k=(j+1)%n;f.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
 return transform(mesh(name,v,f,m,group=group),O,U,N)

def slab(name,z0,z1,m):
 v=[(x,y,z) for z in [z0,z1] for x,y in P];n=len(P);f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)];return mesh(name,v,f,m)
slab('floor_slab',-.06,.05,floor);slab('ceiling_slab',2.59,2.69,red)
for i in range(8):
 O,U,N,L=basis(i)
 localbox(f'ceiling_cream_edge_{i}',(0,-.055,2.52),(L+.015,.12,.14),cream,O,U,N)
 # Rectangle openings in continuous shell, rounded apertures filled by cream/black sleeves.
 bays=[(-.84,.43),(.84,.43)] if i in [0,4] else ([(-.675,1.21),(.675,1.21)] if i in [2,6] else [(0,L-.12)])
 holes=[(c-w/2,c+w/2,1.035,2.345) for c,w in bays]
 if i in [0,4]:holes.append((-.51,.51,.05,2.56))
 cuts=sorted(set([-L/2,L/2]+[x for h in holes for x in h[:2]]))
 for k,(a,b) in enumerate(zip(cuts,cuts[1:])):
  intervals=sorted([(h[2],h[3]) for h in holes if h[0]<(a+b)/2<h[1]])
  z=.05
  for low,high in intervals+[(2.59,2.59)]:
   if low>z:localbox(f'wall_{i}_{k}_{z:.3f}',((a+b)/2,.03,(z+low)/2),(b-a,.14,low-z),red,O,U,N)
   z=max(z,high)
 for j,(c,w) in enumerate(bays):
  # Tiny rectangular corner infill + outer casing radius .001 avoids unfilled rounded rectangular corners.
  ring(f'cream_bezel_{i}_{j}',(c,1.69),(w,1.31),(w-.10,1.19),.001,.065,[-.095,.125],cream,O,U,N)
  ring(f'black_gasket_{i}_{j}',(c,1.69),(w-.095,1.195),(w-.145,1.145),.064,.06,[-.115,-.065],black,O,U,N)
  apertures.append({'id':f'window_{i}_{j}','face':i,'center_u':c,'center_z':1.69,'inner_width':w-.145,'inner_height':1.145,'radius':.06,'plane':list(O),'u':list(U),'n':list(N)})
  for z in [1.13,1.98]:localbox(f'window_guard_{i}_{j}_{z}',(c,-.12,z),(w-.12,.028,.028),brass,O,U,N,.008,'window_guard_inferred_repetition')
  for dx in [-1,1]:
   localbox(f'casing_fastener_{i}_{j}_{dx}',(c+dx*(w/2-.035),-.105,1.065),(.027,.022,.027),brass,O,U,N,.004,'fastener')
 # True finite frame connection at each polygon junction
 localbox(f'pillar_{i}',(-L/2,-.005,1.32),(.055,.16,2.54),red,O,U,N)
for i in [0,4]:
 O,U,N,L=basis(i)
 for c in [-.55,.55]:localbox(f'fixed_door_jamb_{i}_{c}',(c,.02,1.32),(.09,.18,2.54),red,O,U,N)
 # opening source front door angle uncertain; rigid leaf and all fittings rotate as one object set.
 ang=math.radians(-52 if i==0 else 0);uu=U*math.cos(ang)+N*math.sin(ang);nn=N*math.cos(ang)-U*math.sin(ang);OO=O-U*.505+uu*.505
 # Door occupies width1.01, height2.51; window outer .92x1.48 with lower and side solids.
 for nm,c,sz in [('bottom',(0,0,.45),(1.01,.12,.80)),('top',(0,0,2.425),(1.01,.12,.27)),('left',(-.4825,0,1.55),(.045,.12,1.48)),('right',(.4825,0,1.55),(.045,.12,1.48))]:localbox(f'door_{i}_{nm}',c,sz,red,OO,uu,nn)
 ring(f'door_window_bezel_{i}',(0,1.55),(.92,1.48),(.83,1.39),.075,.055,[-.11,.125],brass,OO,uu,nn)
 for z in [1.03,1.18]:localbox(f'door_{i}_guard_{z}',(0,-.14,z),(.84,.03,.03),brass,OO,uu,nn,.007,'door_guard')
 ring(f'door_{i}_lower_trim',(0,.44),(.76,.64),(.725,.605),.12,.10,[-.072,-.09],brass,OO,uu,nn,'trim')
 localbox(f'door_{i}_latch',(0,-.12,.79),(.065,.06,.13),brass,OO,uu,nn,.008,'door_latch')
 if i==4:apertures.append({'id':'rear_door_window','face':4,'center_u':0,'center_z':1.55,'inner_width':.83,'inner_height':1.39,'radius':.055,'plane':list(O),'u':list(U),'n':list(N)})
for side in [-1,1]:
 box(f'bench_{side}_seat',(side*1.30,0,.46),(.54,2.64,.14),seat,.055,'bench')
 box(f'bench_{side}_back',(side*1.54,0,.73),(.12,2.64,.49),seat,.055,'bench')
 box(f'bench_{side}_apron',(side*1.30,0,.355),(.50,2.64,.07),red,.01,'bench')
 for y in [-.95,.95]:box(f'bench_{side}_support_{y}',(side*1.32,y,.165),(.14,.12,.23),red,.008,'inferred_support')
for y in [-.8,.8]:box(f'ceiling_cross_beam_{y}',(0,y,2.54),(3.18,.07,.10),cream,.01,'beam')
lightmat=mat('ceiling lamp diffuser',(.9,.82,.62),0,.25);lightmat.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.85,.6,1);lightmat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.115,depth=.045,location=(0,0,2.555));o=bpy.context.object;o.name='ceiling_lamp_diffuser';o.data.materials.append(lightmat);o['qa_group']='lamp';ledger.append({'name':o.name,'group':'lamp','source_status':'visible lamp; shape dimensions inferred'})
def camera(name,pos,target,lens):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.025;return o
for a in [('SRC_front',(.42,-3.55,1.39),(.42,1.38,1.38),27),('SRC_bench',(-.68,-.45,1.28),(1.42,.12,1.05),27),('SRC_corner',(-.45,-.58,1.42),(1.20,-1.25,1.43),31),('SRC_high',(-.90,-.63,1.10),(1.42,.24,1.09),27),('MAIN',(0,-1.0,1.72),(0,.90,1.15),20)]:camera(*a)
for i in range(8):
 a=i*math.pi/4;camera(f'CHECK{i+1:02d}',(.65*math.sin(a),.80*math.cos(a),1.25 if i%2 else 1.7),(1.3*math.sin(a+math.pi),1.5*math.cos(a+math.pi),1.35),18)
camera('CHECK09_ceiling',(0,0,.4),(0,.01,2.6),18);camera('CHECK10_support',(0,-.5,.18),(1.35,.5,.3),20)
for name,pos,power,size in [('interior',(0,0,2.40),180,2),('entry',(0,-3,2),100,3),('outside',(3,1,4),350,4)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects['MAIN'];s['status']='Nov2 remake candidate; NOT byte-restored R08b; source QA FAIL; hand cameras';s['scale']='inferred model units, not validated metres';s['revision']='R01'
(R/'qa/object-ledger.json').write_text(json.dumps(ledger,indent=2));(R/'qa/apertures.json').write_text(json.dumps(apertures,indent=2));(R/'qa/parameters.json').write_text(json.dumps({'footprint':P,'source_camera_status':'retained uncalibrated hand estimates; no R09 fit adopted','limits':['Repeated guard bars not verified for each instance','Support placement/form inferred','No glass/optical reflection model','Exterior omitted, not a full wheel','Cream outer corners now near-square construction, remake difference','No R08b mesh-count equivalence claimed']},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/ferris_remake_R01_material.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'models/ferris_remake_R01_material.glb'),export_format='GLB',export_apply=True)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/ferris_remake_R01_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'models/ferris_remake_R01_white.glb'),export_format='GLB',export_apply=True)
print('REMAKE_SAVED',len([o for o in s.objects if o.type=='MESH']))
