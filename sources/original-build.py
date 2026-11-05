import bpy, math, json, os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.use_denoising=True
sc.render.resolution_x=1192; sc.render.resolution_y=671; sc.render.resolution_percentage=50
sc.world.color=(.035,.045,.07)
sc.view_settings.view_transform='AgX'

def mat(n,c,metal=0,rough=.35,emit=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*c,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
 b.inputs['Emission Color'].default_value=(*c,1); b.inputs['Emission Strength'].default_value=emit
 return m
teal=mat('Teal ceramic hypothesis',(.006,.19,.16),.65,.25)
ribmat=mat('Raised jade ribs',(.08,.47,.37),.5,.3)
gold=mat('Warm gold trim',(.85,.49,.08),.65,.25)
dark=mat('Dark purple reflective platform',(.026,.008,.071),.68,.23)
line=mat('Jade luminous edge',(.12,.85,.59),.2,.3,2)
purple=mat('Purple inset',(.26,.04,.49),.4,.3)
white=mat('White diagnostic',(.66,.66,.66),0,.7)
objects=[]
def tag(o,n,m,evidence='inferred dimensions / hidden surfaces'):
 o.name=n; o.data.materials.append(m); o['evidence_status']=evidence; objects.append(o); return o

def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n); d.from_pydata(v,[],f); d.update(); o=bpy.data.objects.new(n,d); sc.collection.objects.link(o); return tag(o,n,m)
def tube(n,coords,r,m):
 c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=2; c.resolution_u=1
 s=c.splines.new('POLY'); s.points.add(len(coords)-1)
 for p,co in zip(s.points,coords):p.co=(*co,1)
 o=bpy.data.objects.new(n,c); sc.collection.objects.link(o); return tag(o,n,m)
def box(n,loc,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.scale=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return tag(o,n,m)
def ring(n,r1,r2,z0,z1,m,N=128):
 v=[]
 for z,r in [(z0,r1),(z0,r2),(z1,r1),(z1,r2)]:v += [(r*math.cos(2*math.pi*i/N),r*math.sin(2*math.pi*i/N),z) for i in range(N)]
 f=[]
 for i in range(N):
  j=(i+1)%N
  f += [(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
 return mesh(n,v,f,m)
# The two concentric platforms are closed annuli, not planes.
ring('STAGE_OUTER finite annulus hidden rear inferred',6.0,10.5,0,.55,dark)
ring('STAGE_OUTER LED front full circumference inferred',10.49,10.55,.16,.33,line)
ring('STAGE_INNER annulus',2.0,6.2,1.25,1.70,dark)
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=2,depth=.45,location=(0,0,1.475));tag(bpy.context.object,'STAGE_INNER central disk',dark)
ring('STAGE_INNER silver band',2.0,2.32,1.701,1.72,ribmat)
ring('STAGE_INNER thin edge',6.18,6.24,1.48,1.54,purple)
# Parametric curved roof: main front pitch visible; reverse pitch hypothesis.
def roof(n,cx,cy,z,w,d,h):
 nx,ny=64,32
 def xyz(u,t):
  # t -1..1 front/back; ridge half width narrow, swept eave broader.
  x=cx+u*w*(.74+.26*abs(t))
  y=cy+t*d
  zz=z+h*(1-abs(t))**2+.8*(abs(u)**7)*(abs(t)**2)
  return (x,y,zz)
 v=[xyz(-1+2*i/nx,-1+2*j/ny) for j in range(ny+1) for i in range(nx+1)]
 f=[]
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;f.append((a,a+1,a+nx+2,a+nx+1))
 o=mesh(n+' closed shell',v,f,teal)
 so=o.modifiers.new('Assumed shell thickness','SOLIDIFY');so.thickness=.12
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=so.name)
 for i in range(45):
  u=-1+2*i/44
  tube(n+' rib %02d'%i,[(x,y,zz+.06) for x,y,zz in [xyz(u,-1+2*j/48) for j in range(49)]],.055,ribmat)
 for t,label in [(0,'ridge'),(-1,'front eave'),(1,'back eave inferred')]:
  tube(n+' gold '+label,[(x,y,zz+.12) for x,y,zz in [xyz(-1+2*i/64,t) for i in range(65)]],.085,gold)
 for u in [-1,1]:tube(n+' swept gable',[(x,y,zz+.1) for x,y,zz in [xyz(u,-1+2*j/48) for j in range(49)]],.085,gold)
roof('ROOF_MAIN',0,5.5,6.0,11.4,3.0,2.5)
roof('ROOF_LEFT',-10.3,1.9,3.7,4.1,1.6,1.1)
roof('ROOF_RIGHT',10.3,1.9,3.7,4.1,1.6,1.1)
roof('ROOF_LEFT_REAR fragment proxy',-6.9,6.7,3.6,2.1,1.1,.85)
roof('ROOF_RIGHT_REAR fragment proxy',6.9,6.7,3.6,2.1,1.1,.85)
box('DJ11 body inferred depth',(0,2.8,2.32),(1.25,.65,1.24),purple)
box('DJ11 top',(0,2.8,2.97),(1.42,.79,.12),dark)
for z in [2.05,2.43,2.8]:box('DJ11 front stripe',(0,2.46,z),(1.27,.035,.055),gold)
# No projected source textures or city geometry.
# Small cloud relief contour is an explicit decorative proxy, not observed topology.
for k,(cx,cy,cz,s) in enumerate([(-11.6,3.7,6.25,1.3),(11.8,3.7,6.25,1.3),(4.1,4.3,4.7,.65)]):
 coords=[]
 for i in range(145):
  a=2*math.pi*i/144; r=1+.17*math.sin(5*a)+.08*math.sin(9*a)
  coords.append((cx+s*1.6*r*math.cos(a),cy,cz+s*.65*r*math.sin(a)))
 tube('CLOUD_%d silhouette decorative proxy'%k,coords,.14*s,gold)
 for q in [-.6,.4]:
  coords=[]
  for i in range(70):
   a=i/69*math.pi*3.4; r=.04+.4*i/69
   coords.append((cx+s*(q+r*math.cos(a)),cy-.03,cz+s*r*math.sin(a)))
  tube('CLOUD_%d spiral proxy'%k,coords,.065*s,gold)

def camera(n,pos,target,lens=40):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
cam=camera('SOURCE11 conditional camera',(0,-29,14.0),(0,2.4,4),38)
cam10=camera('SOURCE10 auxiliary different state',(0,-9,4.7),(0,3.5,3.3),40)
sc.camera=cam
for n,pos,power,col,size in [('Key',(-8,-8,17),3500,(.6,.85,1),10),('Gold',(8,-2,12),2500,(1,.65,.3),8),('Rim',(0,8,11),4000,(.2,1,.65),10)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.color=col;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,3,3))-o.location).to_track_quat('-Z','Y').to_euler()
sc['status']='FINITE CANDIDATE: source gates FAILED; no native video; no acceptance'
sc['source_state']='11 fixed DJ state. 10 auxiliary different state; audience omitted.'
sc.render.filepath=str(P/'renders/preview11.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r01.blend'))
bpy.ops.render.render(write_still=True)
