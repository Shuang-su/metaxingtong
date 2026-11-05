import bpy, math, json, os
from mathutils import Vector
from math import sin,cos,pi
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=6
s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
materials={}
def mat(n,c,metal=0,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.38
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 materials[n]=m;return m
navy=mat('Arch navy metal',(.025,.018,.065),.65);gold=mat('Warm arch inset',(.95,.34,.06),.6,1.2);blue=mat('Blue facade',(.025,.06,.25),.35);cyan=mat('Cyan coping',(.02,.22,.5),.4);pink=mat('Pink panel luminous insert',(.7,.045,.5),.1,1.8);white=mat('Warm ivory',(.7,.72,.72));wood=mat('Wood structure',(.32,.13,.055));cloth=mat('Canvas pink',(.52,.12,.22));clothwhite=mat('Canvas cream',(.72,.61,.52));dark=mat('Stage deck',(.08,.035,.10),.35);lamp=mat('Round warm diffuser',(1,.82,.25),0,2.5);rail=mat('Magenta rail',(.32,.02,.14),.55);water=mat('Finite ground apron',(.045,.04,.085),.4)
def finish(o,n,m):o.name=n;o.data.materials.append(m);return o
def box(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=finish(bpy.context.object,n,m);o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(n,loc,r,depth,m,vertices=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);return finish(bpy.context.object,n,m)
def beam(n,a,b,w,m):
 d=Vector(b)-Vector(a);o=box(n,(Vector(a)+Vector(b))/2,(w,w,d.length),m);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def arc(n,r,w,y,thick,z,m,start=0,end=pi,N=96):
 verts=[]
 for yy in [y-thick/2,y+thick/2]:
  for rr in [r-w/2,r+w/2]:
   for i in range(N+1):
    a=start+(end-start)*i/N;verts.append((rr*cos(a),yy,z+rr*sin(a)))
 k=N+1;faces=[]
 for i in range(N):
  for off in [0,2*k]:faces.append((off+i,off+i+1,off+k+i+1,off+k+i))
  faces.extend([(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
 faces.extend([(0,k,3*k,2*k),(N,2*k-1,4*k-1,3*k-1)])
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(n,mesh);s.collection.objects.link(o);return finish(o,n,m)
def curved(n,width,y,z,h,thick,m,curve=.035,N=48):
 verts=[]
 for zz in [z-h/2,z+h/2]:
  for dy in [-thick/2,thick/2]:
   for i in range(N+1):
    x=-width/2+width*i/N;verts.append((x,y+curve*x*x+dy,zz))
 k=N+1;faces=[]
 for i in range(N):
  faces.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
 faces.extend([(0,k,3*k,2*k),(N,3*k-1,4*k-1,2*k-1)])
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(n,mesh);s.collection.objects.link(o);return finish(o,n,m)
# Finite stage, no invented enclosing building.
cyl('P01 finite front round podium',(0,-1.8,.02),5.5,.24,dark,128);cyl('P02 podium edge',(0,-1.8,-.09),5.56,.10,rail,128)
box('P03 finite rear apron',(0,1.3,-.15),(15,7,.3),water)
for i,r in enumerate([5.5,3.85,2.85]):
 arc('A%02d vertical arch solid'%i,r,.45,4.1+i*.22,.42,.38,navy)
 for j,dr in enumerate([-.15,.13]):arc('A%02d inset %d'%(i,j),r+dr,.027,3.87+i*.22,.035,.38,gold)
# Curved facade with actual round apertures through upper shell.
upper=curved('W01 upper curved shell',7.7,3.55,2.15,1.55,.3,blue)
for i,x in enumerate([-1.85,0,1.85]):
 yy=3.55+.035*x*x
 disc=cyl('W02 round diffuser %d'%i,(x,yy-.18,2.2),.225,.07,lamp);disc.rotation_euler[0]=pi/2
curved('W03 upper coping',7.95,3.55,2.97,.15,.49,cyan)
curved('W04 lower facade',13.7,2.95,.68,1.3,.4,blue,curve=.013)
curved('W05 lower coping',14,2.95,1.38,.17,.62,cyan,curve=.013)
for i,x in enumerate([-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6]):
 yy=2.95+.013*x*x
 box('W06 panel surround %02d'%i,(x,yy-.245,.68),(.72,.12,.9),navy)
 box('W07 pink inset %02d'%i,(x,yy-.318,.68),(.52,.035,.70),pink)
for i,x in enumerate([-2.65,2.65]):
 d=cyl('W08 lower circle %d'%i,(x,2.72+.013*x*x,.72),.22,.08,lamp);d.rotation_euler[0]=pi/2
beam('R01 top rail',(-6.4,2.61,1.94),(6.4,2.61,1.94),.045,rail)
for i in range(15):
 x=-6.4+i*12.8/14;beam('R02 baluster %02d'%i,(x,2.61,1.4),(x,2.61,1.94),.035,rail)
# Left four-post pavilion: inferred rear depth, open structure.
box('K01 pavilion plinth',(-6.6,1,.1),(3,2.3,.25),white)
for i,x in enumerate([-7.9,-5.3]):
 for j,y in enumerate([.02,1.98]):box('K02 post %d%d'%(i,j),(x,y,1.65),(.12,.12,3.1),white)
box('K03 roof',(-6.6,1,3.25),(3.2,2.6,.18),white)
box('K04 fascia',(-6.6,-.24,3.0),(3.18,.14,.48),white)
box('K05 front counter',(-6.6,-.05,.62),(3.1,.45,1.15),white)
box('K06 counter front insert',(-6.6,-.285,.62),(2.7,.035,.85),cyan)
box('K07 counter worktop',(-6.6,-.05,1.22),(3.25,.6,.10),white)
# Deckchairs constructed from separate slats/cloth stripes and crossed legs.
def chair(idx,x,y,ang):
 objs=[];before=set(bpy.data.objects)
 for side in [-.48,.48]:
  beam('C%s cross leg A'%idx,(side,-.5,0),(side,.6,1.0),.065,wood)
  beam('C%s cross leg B'%idx,(side,.55,0),(side,-.42,.83),.065,wood)
  beam('C%s back rail'%idx,(side,0,.55),(side,.85,1.75),.065,wood)
 beam('C%s front bar'%idx,(-.53,-.4,.65),(.53,-.4,.65),.06,wood)
 for k in range(12):
  a=(-.44+k*.08,-.38,.67);b=(-.44+k*.08,.78,1.64)
  d=Vector(b)-Vector(a);o=box('C%s stripe %02d'%(idx,k),(Vector(a)+Vector(b))/2,(.081,.025,d.length),cloth if k%2 else clothwhite);o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 for o in set(bpy.data.objects)-before:
  q=o.location.copy();o.location=(x+q.x*cos(ang)-q.y*sin(ang),y+q.x*sin(ang)+q.y*cos(ang),q.z+.08);o.rotation_euler.z+=ang
chair('01',4.3,.1,.65);chair('02',7.1,-.2,.65)
# Folding table
box('T01 tabletop',(5.8,-.25,.85),(1.3,.85,.10),wood)
for xx in [5.35,6.25]:
 beam('T02 folding support',(xx,-.65,.08),(xx,.12,.82),.07,wood);beam('T03 folding support',(xx,.12,.08),(xx,-.65,.82),.07,wood)
cyl('T04 cup',(5.9,-.25,1.01),.09,.24,white)
# Eight-piece solid umbrella canopy with scalloped skirt.
ux,uy=6.4,1.15
cyl('U01 umbrella pole',(ux,uy,1.825),.035,3.65,white)
for k in range(8):
 a=k*pi/4;b=(k+1)*pi/4;verts=[(ux,uy,3.65),(ux+2*cos(a),uy+2*sin(a),3.13),(ux+2*cos(b),uy+2*sin(b),3.13),(ux+2*cos(b),uy+2*sin(b),2.91),(ux+2*cos(a),uy+2*sin(a),2.91)]
 mesh=bpy.data.meshes.new('canopy');mesh.from_pydata(verts,[],[(0,1,2),(1,4,3,2)]);mesh.update();o=bpy.data.objects.new('U02 canopy segment %d'%k,mesh);s.collection.objects.link(o);finish(o,o.name,cyan if k%2 else blue);mod=o.modifiers.new('fabric thickness','SOLIDIFY');mod.thickness=.018;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 beam('U03 rib %d'%k,(ux,uy,3.63),(ux+1.97*cos(a),uy+1.97*sin(a),3.12),.018,white)
# Practical floor lights, conservative housings rather than source light rays.
for i,x in enumerate([-3.8,3.3]):
 box('L01 flood housing %d'%i,(x,1.8,.2),(1.45,.35,.28),navy);box('L02 flood diffuser %d'%i,(x,1.60,.22),(1.3,.025,.16),lamp)
def camera(n,loc,target,lens):
 data=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.sensor_width=36;data.sensor_fit='HORIZONTAL';data.clip_end=200;return o
cams=[camera('SOURCE03 conditional',(0,-15.7,4.0),(0,2,2.35),34),camera('SOURCE04 conditional',(2.7,-12.4,3.25),(.9,2.5,2.2),37)]
for i,(loc,t) in enumerate([((12,-12,8),(0,1,1.8)),((-12,-12,8),(0,1,1.8)),((12,10,8),(0,1,1.8)),((-12,10,8),(0,1,1.8)),((0,15,6),(0,1,2)),((0,-13,10),(0,1,1)),((0,1,17),(0,1,0)),((13,1,4),(0,1,2))]):cams.append(camera('CHECK%02d'%i,loc,t,40))
s.world=bpy.data.worlds.new('Purple environment');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.055,.16,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for n,loc,power,color,size,target in [('front soft',(0,-6,9),2100,(.65,.72,1),8,(0,1,1)),('warm side',(-7,1,7),1600,(1,.3,.3),7,(0,1,1)),('rear rim',(4,7,9),2400,(.6,.3,1),6,(0,1,2))]:
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
# Fix face orientation on every mesh after construction.
for o in [o for o in s.objects if o.type=='MESH']:
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
# r01 composition adjustment, fixed geometry across views
for o in s.objects:
 if o.name.startswith('K'):
  if 'post' in o.name:o.dimensions.z+=.8;o.location.z+=.4;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
  elif any(q in o.name for q in ['roof','fascia']):o.location.z+=.8
 if o.name.startswith('U02') or o.name.startswith('U03'):o.location.z+=.6
 if o.name.startswith('U01'):o.dimensions.z+=.6;o.location.z+=.3;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
for o,target in [(cams[0],(0,2,3.15)),(cams[1],(.9,2.5,2.85))]:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
s.camera=cams[0]
bpy.context.view_layer.update()
state={'resolution':[1192,671],'sensor_fit':'HORIZONTAL','world':{'color':[.11,.055,.16,1],'strength':.65},'lights':[],'cameras':[],'unit':'arbitrary model unit, not metres','status':'FAILED source gates; conditional finite candidate'}
for o in s.objects:
 if o.type=='LIGHT':state['lights'].append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size,'shape':o.data.shape,'matrix_world':[list(r) for r in o.matrix_world]})
 if o.type=='CAMERA':state['cameras'].append({'name':o.name,'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'matrix_world':[list(r) for r in o.matrix_world]})
json.dump(state,open(ROOT+'/models/environment.json','w'),indent=2)
for mode in ['material','white']:
 if mode=='white':
  w=mat('DIAGNOSTIC shared white',(.62,.62,.62))
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
 bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/'+mode+'.blend')
 bpy.ops.export_scene.gltf(filepath=ROOT+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
 if mode=='material':
  s.cycles.samples=4;s.render.resolution_percentage=50;s.render.filepath=ROOT+'/renders/low-material03.png';bpy.ops.render.render(write_still=True);s.cycles.samples=32;s.render.resolution_percentage=100
print('BUILD_COMPLETE')
