import bpy,math,json,hashlib
from mathutils import Vector,Matrix
from pathlib import Path
D=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.world.color=(.25,.25,.25);s.view_settings.view_transform='Standard'
m=bpy.data.materials.new('WHITE_SHARED');m.diffuse_color=(.65,.65,.65,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
def finish(o,name):
 o.name=name;o.data.materials.clear();o.data.materials.append(m);return o
def cube(n,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n)
def cyl(n,loc,r,depth,verts=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);return finish(bpy.context.object,n)
def lathe(n,xy,profile,N=48):
 v=[];f=[]
 for z,r in profile:
  for k in range(N):a=2*math.pi*k/N;v.append((xy[0]+r*math.cos(a),xy[1]+r*math.sin(a),z))
 for j in range(len(profile)-1):
  for k in range(N): a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
 f.append(tuple(reversed(range(N))));f.append(tuple((len(profile)-1)*N+k for k in range(N)))
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(v,[],f);mesh.update();o=bpy.data.objects.new(n,mesh);s.collection.objects.link(o);finish(o,n);return o
def ring(n,r0,r1,z0,z1,N=96):
 v=[(r*math.cos(k*2*math.pi/N),r*math.sin(k*2*math.pi/N),z) for r,z in [(r0,z0),(r1,z0),(r1,z1),(r0,z1)] for k in range(N)];f=[]
 for j in range(4):
  for k in range(N):f.append((j*N+k,j*N+(k+1)%N,((j+1)%4)*N+(k+1)%N,((j+1)%4)*N+k))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);return finish(o,n)
def rod(n,a,b,r):
 d=Vector(b)-Vector(a);o=cyl(n,(Vector(a)+Vector(b))/2,r,d.length,12);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
cube('GROUND_inferred_bounded_support',(0,5,-.25),(24,30,.3))
cyl('POOL_bottom',(0,0,-.05),6.1,.2,128)
ring('POOL_outer_retaining_wall',6,6.2,-.05,.18,128)
ring('POOL_water_placeholder',5.15,6.0,.06,.075,128)
cyl('STAGE_solid_drum',(0,0,.17),5,.44,128)
for i,(r,z,w) in enumerate([(5,.39,.04),(5.08,.29,.035),(5.12,.18,.04)]):ring('STAGE_lip_'+str(i),r-w,r+w,z-.025,z+.025,128)
# Two colonnades remain open; repeated depth hypothesis, no photo planes.
for side,sign in [('L',-1),('R',1)]:
 cube('AISLE_'+side,(sign*5.5,10,.05),(3.1,14,.28))
 for j,y in enumerate([6,9,12,15]):
  for row,x in [('',4.4),('OUT_',6.6)]:
   n=f'COL_{row}{side}{j}';cube(n+'_base',(sign*x,y,.27),(.72,.72,.3));cube(n+'_shaft',(sign*x,y,1.72),(.43,.43,2.6));cube(n+'_capital',(sign*x,y,3.03),(.7,.7,.18))
  cube(f'BEAM_{side}{j}',(sign*5.5,y,3.25),(3.1,.24,.32))
 cube('TOP_long_beam_'+side,(sign*4.4,10.5,3.25),(.25,12.7,.32));cube('TOP_outer_beam_'+side,(sign*6.6,10.5,3.25),(.25,12.7,.32))
 cube('ROOF_slab_'+side,(sign*5.5,10.5,3.55),(3.35,12.8,.25))
 for j in range(32):
  y=4.2+j*.4
  # Individual eave tile round ends, conditional roof construction.
  a=(sign*3.8,y,3.57);b=(sign*7.1,y,3.8);rod(f'TILE_{side}{j}',a,b,.09)
 # Foreground bronze urns: profile only; filigree intentionally not invented.
 lathe('URN_'+side,(sign*2.7,6),[(.1,.25),(.16,.28),(.25,.18),(.38,.12),(.65,.20),(.8,.32),(1.12,.32),(1.23,.22),(1.27,.38),(1.32,.35),(1.5,.24),(1.64,.13),(1.7,.07),(1.8,.12),(1.9,.03)])
 for j,y in enumerate([6,9,12,15]):
  x=sign*4.4
  # Fixed round lantern under near eave.
  lathe(f'LANTERN_round_{side}{j}',(x,y),[(2.45,.13),(2.5,.28),(2.65,.38),(2.85,.4),(3.03,.3),(3.08,.12)],32)
  rod(f'LANTERN_hanger_{side}{j}',(x,y,3.08),(x,y,3.4),.018)
# Cross strings. Count/depth conditional rather than claimed measured.
for j,y in enumerate([6.4,9.4,12.4,15.4]):
 points=[]
 for k in range(21):
  x=-4.4+k*.44;z=3.65-.4*(1-(x/4.4)**2);points.append((x,y,z))
  lathe(f'LANTERN_string{j}_{k}',(x,y),[(z-.45,.085),(z-.42,.12),(z-.12,.12),(z-.09,.085)],16)
  if k:rod(f'CABLE_{j}_{k}',points[k-1],points[k],.009)
# Source cameras from fixed shared proxy, not validated calibration.
for item in json.load(open(D/'qa/camera_seed.json')):
 cam=bpy.data.cameras.new(item['name']);o=bpy.data.objects.new(item['name'],cam);s.collection.objects.link(o);o.location=item['camera_center'];R=Matrix(item['world_to_camera']);o.rotation_euler=(R.transposed() @ Matrix.Diagonal((1,-1,-1))).to_euler();cam.lens=item['f_px']*36/1920;cam.sensor_width=36;cam.clip_end=300
for name,loc,power,size in [('KEY',(0,-3,10),2300,9),('FILL',(0,12,8),1500,7)]:
 l=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=loc;l.energy=power;l.shape='DISK';l.size=size
# eight inspection cameras, not source evidence.
for i in range(8):
 a=2*math.pi*i/8;cam=bpy.data.cameras.new('CHECK'+str(i));o=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(o);o.location=(18*math.sin(a),5+18*math.cos(a),10);o.rotation_euler=(Vector((0,5,1.5))-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=28
s.camera=bpy.data.objects['SOURCE1'];bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R01_white.blend'))
meshes=[o for o in s.objects if o.type=='MESH'];(D/'qa/R01_inventory.json').write_text(json.dumps({'mesh_count':len(meshes),'objects':[{'name':o.name,'verts':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in meshes],'status':'white preliminary; no geometry acceptance; all source camera poses conditional'},indent=2))
for name in ['SOURCE1','SOURCE2']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/f'renders/R01_{name}_white960.png');bpy.ops.render.render(write_still=True)
