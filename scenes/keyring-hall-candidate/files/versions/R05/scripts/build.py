import bpy, math, json, os, bmesh
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=6
s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100
s.world.use_nodes=True;s.world.color=(.035,.035,.07);s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.035,.035,.07,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;s.view_settings.view_transform='AgX'
objects=[]
def mat(n,c,metal=0,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.32
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
navy=mat('navy-stage',(.024,.018,.075),.35);silver=mat('blue-silver',(.1,.23,.4),.6);white=mat('key-white-cyan',(.56,.94,1),.1,1.4);black=mat('key-black-purple',(.06,.027,.1),.2);pink=mat('pink-luminous',(.8,.018,.3),.15,3);piano=mat('piano-ivory',(.82,.86,.93),.2);star=mat('four-concave-star',(.29,.08,.55),.25);screen=mat('media-unresolved-blue',(.012,.024,.12),0,.35)
def register(o,m,ev='inferred dimensions/back/connection; visible class in 17/20/21'):
 o.data.materials.append(m);o['evidence']=ev;objects.append({'id':o.name,'evidence':ev});return o
def cube(n,loc,dim,m,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;o.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return register(o,m)
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);return register(o,m)
def arc(n,ri,ro,z,h,a,b,m,N=96):
 vs=[]
 for zz in [z,z+h]:
  for rr in [ri,ro]:
   for i in range(N+1):
    t=a+(b-a)*i/N;vs.append((rr*math.sin(t),rr*math.cos(t),zz))
 k=N+1;fs=[]
 for i in range(N):
  fs += [(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)]
 if abs((b-a)-2*math.pi)>1e-6:fs += [(0,k,3*k,2*k),(N,2*k+N,3*k+N,k+N)]
 return mesh(n,vs,fs,m)
arc('stage-central-solid',0,5.0,-.3,.3,-math.pi,math.pi,navy)
arc('stage-step-ring',5.02,6.0,-.42,.22,-math.pi,math.pi,navy)
arc('stage-outer-floor',6.02,10,-.5,.25,-math.pi*.66,math.pi*.66,navy)
arc('inner-luminous-rim',4.96,5.01,.002,.035,-math.pi,math.pi,silver)
arc('key-pink-ring',8.3,8.38,-.18,.08,-1.9,1.9,pink)
# Four concave points; curve sampled, center filled, small finite thickness.
pts=[]
for i in range(128):
 t=2*math.pi*i/128;pts.append((4.8*math.cos(t)**3,4.8*math.sin(t)**3,.012))
v=pts+[(x,y,0) for x,y,z in pts];f=[tuple(range(128)),tuple(range(255,127,-1))]+[(i,(i+1)%128,(i+1)%128+128,i+128) for i in range(128)]
mesh('four-point-concave-floor-inlay',v,f,star)
for i in range(37):
 a=-1.85+i*3.7/36;x,y=9.05*math.sin(a),9.05*math.cos(a)
 o=cube(f'white-key-{i:02}',(x,y,.901906),(.69,.26,2.3),white,-a);o.rotation_euler.x=math.radians(-12)
 if i%7 not in (2,6):
  a+=.038;o=cube(f'black-key-{i:02}',(8.72*math.sin(a),8.72*math.cos(a),.502823),(.38,.42,1.45),black,-a);o.rotation_euler.x=math.radians(-12)
for side in [-1,1]:
 for j in range(3):
  a,b=(1.05,1.97) if side==1 else (-1.97,-1.05)
  arc(f'upper-terrace-{side}-{j}',10+j*.7,10.7+j*.7,1.8+j*.65,.22,a,b,navy,32)
  arc(f'upper-edge-{side}-{j}',10+j*.7,10.05+j*.7,2.02+j*.65,.045,a,b,pink,32)
# finite rear curved media surface, deliberately untextured and nontransparent, not external trees/actors
vs=[];fs=[];na=64;nh=24
for j in range(nh+1):
 phi=(math.pi/2)*j/nh
 for i in range(na+1):
  a=-1.98+3.96*i/na;vs.append((13*math.cos(phi)*math.sin(a),13*math.cos(phi)*math.cos(a),1+13*math.sin(phi)))
for j in range(nh):
 for i in range(na):
  k=j*(na+1)+i;fs.append((k,k+1,k+na+2,k+na+1))
o=mesh('finite-media-surface-unresolved',vs,fs,screen);mod=o.modifiers.new('inferred-shell-thickness','SOLIDIFY');mod.thickness=.05
# fine dome grid curves
for j in [2,5,8,11,14,17,20]:
 ph=math.pi/2*j/nh;arc('media-grid-lat-%02d'%j,13*math.cos(ph)-.025,13*math.cos(ph),1+13*math.sin(ph),.025,-1.98,1.98,silver,64)
# piano body polygon with rounded tail, front keyboard faces -Y
cx,cy=3.0,-1.8
poly=[(-1.05,-.65),(1.05,-.65),(1.05,.4),(.75,1.65),(.3,2.05),(-.25,1.95),(-.75,1.15),(-1.05,.3)]
def prism(n,poly,z,h,m):
 v=[(cx+x,cy+y,z) for x,y in poly]+[(cx+x,cy+y,z+h) for x,y in poly];k=len(poly);return mesh(n,v,[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],m)
prism('piano-body-rim',poly,1.05,.3,piano);prism('piano-soundboard',[(x*.88,y*.9) for x,y in poly],1.35,.025,black)
# opened lid shares shape and hinge, plausible not exact
lid=prism('piano-open-lid',poly,1.35,.065,piano)
for v in lid.data.vertices:
 v.co.z += (v.co.x-(cx-1.05))*.68
for i,(x,y) in enumerate([(-.86,-.4),(.86,-.4),(.35,1.5)]):cube(f'piano-leg-{i}',(cx+x,cy+y,.525),(.14,.14,1.05),piano)
cube('piano-keyboard-bed',(cx,cy-.79,1.12),(2.2,.45,.13),piano)
for i in range(35):
 x=cx-1+i*2/35;cube(f'piano-white-{i}',(x,cy-.83,1.1975),(.053,.36,.025),piano)
 if i%7 not in (2,6):cube(f'piano-black-{i}',(x+.026,cy-.72,1.24),(.029,.19,.05),black)
cube('bench-seat',(cx,cy-1.62,.65),(1.3,.66,.19),piano)
for i,(x,y) in enumerate([(-.53,-.23),(.53,-.23),(-.53,.23),(.53,.23)]):cube(f'bench-leg-{i}',(cx+x,cy-1.62+y,.28),(.09,.09,.56),piano)
def cam(n,loc,targ,lens):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(targ)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.sensor_width=36;o.data['aspect']=1192/671;return o
cams=[cam('source17-conditional',(0,-3.5,1.9),(0,5,1.3),30),cam('source20-conditional',(-.8,-7.8,.95),(0,3,4.0),26),cam('source21-conditional',(0,-11.0,10),(0,2.4,4),25)]
for i in range(8):
 a=2*math.pi*i/8;cams.append(cam(f'inspection-{i+1:02}',(9*math.sin(a),9*math.cos(a),9 if i%2==0 else 7),(0,0,.8),18))
for n,loc,power,col,size in [('key',(0,-5,10),2200,(.55,.7,1),9),('fill',(-6,0,6),1700,(.3,.45,1),7),('rim',(5,5,8),2400,(1,.2,.65),6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.color=col;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
s.camera=cams[2]
# Weld actual shared endpoints and top-pole singularities, remove zero-area faces.
for obj in s.objects:
 if obj.type=='MESH':
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bad=[f for f in bm.faces if f.calc_area()<1e-10]
  if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()

(R/'docs/objects.json').write_text(json.dumps(objects,indent=2))
(R/'docs/render-sidecar.json').write_text(json.dumps({'engine':'CYCLES','samples':64,'denoising':False,'threads':6,'resolution':[1192,671],'world_background_rgba':list(s.world.node_tree.nodes['Background'].inputs['Color'].default_value),'world_background_strength':s.world.node_tree.nodes['Background'].inputs['Strength'].default_value,'world_use_nodes':s.world.use_nodes,'world_color':list(s.world.color),'view_transform':'AgX','lights':[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size,'matrix_world':[list(r) for r in o.matrix_world]} for o in s.objects if o.type=='LIGHT'],'restore':'Use scripts/build.py or exact BLEND; GLB Area lights and World are not equivalent. All materials are Principled nodes.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/keyring-material.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'models/keyring-material.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=True)
wm=mat('diagnostic-white',(.7,.7,.7))
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(wm)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/keyring-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'models/keyring-white.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=True)
