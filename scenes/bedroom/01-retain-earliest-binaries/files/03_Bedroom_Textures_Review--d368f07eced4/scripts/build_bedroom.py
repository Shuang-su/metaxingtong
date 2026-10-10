import bpy, math, os, json, random, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];random.seed(14)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
 if col.name!='Collection':bpy.data.collections.remove(col)
COL={}
for name in ['01_Room_envelope_inferred','02_Wall_mouldings','03_Parquet_floor','04_Upholstered_bed','05_Bedding','06_Bedside_cabinet','07_Lamp_clock_frames','08_Plant_inferred_hidden','09_Cameras_lighting']:
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);COL[name]=c
cur='01_Room_envelope_inferred'
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL[cur].objects.link(o);return o

def mat(name,color,rough=.65,metal=0,tex=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if tex:
  for kind,socket in [('BaseColor','Base Color'),('Roughness','Roughness'),('Normal','Normal')]:
   t=n.new('ShaderNodeTexImage');t.name=tex+' '+kind;t.image=bpy.data.images.load(str(R/'textures'/f'{tex}_{kind}.png'));t.image.pack()
   if kind!='BaseColor':t.image.colorspace_settings.name='Non-Color'
   if kind=='Normal':
    nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.3;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs[0],b.inputs['Normal'])
   else:l.new(t.outputs['Color'],b.inputs[socket])
 return m
M={k:mat(k,(.5,.5,.5),tex=k) for k in ['Wall','Linen','Rug','Oak','Checker','Cabinet','Orange','Leaf']}
M['dark']=mat('Dark metal',(.032,.024,.020),.35,.75);M['black']=mat('Frame black lacquer',(.016,.012,.012),.28);M['blue']=mat('Blue enamel alarm clock',(.032,.23,.29),.22,.3);M['cream']=mat('Clock face ivory',(.75,.69,.55),.8);M['soil']=mat('Pot dark soil',(.07,.042,.021),1);M['pot']=mat('Earthen plant pot',(.18,.085,.04),.85);M['vein']=mat('Leaf fine veins',(.063,.13,.032),.65);M['skirt']=mat('Wall skirting deep shadow',(.12,.09,.069),.8)

def uvbox(o,scale=1):
 me=o.data
 if me.uv_layers:me.uv_layers.remove(me.uv_layers[0])
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]*scale,co[axes[1]]*scale)

def finish(o,name,ma=None,bevel=0):
 o.name=name;link(o)
 if ma:o.data.materials.append(ma)
 if bevel:
  m=o.modifiers.new('Soft real edge bevel','BEVEL');m.width=bevel;m.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
  for p in o.data.polygons:p.use_smooth=True
  m=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');m.keep_sharp=True
  bpy.ops.object.modifier_apply(modifier=m.name)
 uvbox(o)
 return o

def cube(name,loc,size,ma,bevel=0,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,ma,bevel)
 if rot:o.rotation_euler=rot
 return o

def cyl(name,loc,r,depth,ma,rot=None,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;finish(o,name,ma,.004)
 if rot:o.rotation_euler=rot
 return o

def sphere(name,loc,size,ma,segments=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=12,radius=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,ma)
 for p in o.data.polygons:p.use_smooth=True
 return o

def rod(name,a,b,r,ma):
 v=Vector(b)-Vector(a);o=cyl(name,(Vector(a)+Vector(b))*.5,r,v.length,ma,vertices=12);o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o

def mesh(name,vs,fs,ma,uvs=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);COL[cur].objects.link(o);me.materials.append(ma)
 for p in me.polygons:p.use_smooth=True
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  for li in p.loop_indices:
   idx=me.loops[li].vertex_index;uv.data[li].uv=uvs[idx] if uvs is not None else (vs[idx][0],vs[idx][1])
 return o

# Metric convention: rear wall y=0, bed extends toward -Y. Full envelope is inference.
cube('Rear wall verified visible face',(0,.12,1.65),(7.2,.18,3.3),M['Wall'],.01)
cube('Left room return inferred',(-3.61,-2.75,1.65),(.18,5.65,3.3),M['Wall'],.01)
cube('Right room return inferred',(3.61,-2.75,1.65),(.18,5.65,3.3),M['Wall'],.01)
cube('Floor substrate',(0,-2.75,-.045),(7.2,5.7,.09),M['skirt'])
cur='02_Wall_mouldings'
cube('Rear skirting',(0,-.019,.062),(7.15,.045,.124),M['Wall'],.006)
cube('Skirting bottom shadow',(0,-.043,.014),(7.15,.012,.018),M['skirt'],.002)
# Full-height panel layouts read from front image. Hidden continuation marked inferred.
def panel(name,x1,x2,z1=.255,z2=3.26,y=-.022):
 for n,x in [('L',x1),('R',x2)]:cube(name+' '+n,(x,y,(z1+z2)/2),(.021,.022,z2-z1),M['Wall'],.005)
 for n,z in [('B',z1),('T',z2)]:cube(name+' '+n,((x1+x2)/2,y,z),(x2-x1,.022,.021),M['Wall'],.005)
for i,(a,b) in enumerate([(-3.36,-2.82),(-2.46,-1.41),(-1.05,1.48),(1.79,2.83),(3.14,3.46)]):panel('Rear wall panel '+str(i),a,b)
for x in [-2.68,-1.24,1.64,3.0]:
 cube('Double panel outer vertical',(x,-.014,1.65),(.014,.018,3.27),M['Wall'],.003)
 cube('Double panel inner vertical',(x+.046,-.014,1.65),(.011,.018,3.27),M['Wall'],.003)
# Subtle two narrow vertical accents around the poster, visible above and beneath it.
for x in [.13,.29]:cube('Behind-poster vertical bead',(x,-.018,1.78),(.016,.025,3.03),M['Wall'],.004)
cur='03_Parquet_floor'
# Individual herringbone slats with physically assigned plank UV. 90-degree alternating strips.
L=.55;W=.11
for i in range(-30,31):
 for j in range(-80,81):
  bx=i*L+j*W;by=i*L-j*W
  for typ in [0,1]:
   cx=bx+L*.5 if typ==0 else bx+W*.5;cy=by+W*.5 if typ==0 else by+1.5*L
   if -3.55<cx<3.55 and -5.52<cy<.025:
    o=cube('Herringbone oak plank',(cx,cy,.002),(L-.003,W-.003,.012) if typ==0 else (W-.003,L-.003,.012),M['Oak'],.0015)
    uv=o.data.uv_layers.active
    off=random.random()
    for p in o.data.polygons:
     for li in p.loop_indices:
      co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x/L if typ==0 else co.y/L)+off,(co.y/W if typ==0 else co.x/W))
# Supplement visible sub-floor: slats above produce a chevron-like repeated pattern with real seam relief.
cur='04_Upholstered_bed'
BX=0;back=-.38;front=-2.60;cy=(back+front)/2
cube('Bed recessed dark plinth',(0,cy,.068),(2.16,2.18,.116),M['skirt'],.025)
cube('Bed upholstered base inner',(0,cy,.202),(2.29,2.30,.235),M['Linen'],.045)
for i in range(25):
 x=-1.10+i*2.20/24
 cube('Footboard vertical padded channel %02d'%i,(x,-2.642,.211),(.090,.107,.259),M['Linen'],.038)
for s in [-1,1]:
 for i in range(24):
  y=-.41-i*2.19/23;cube('Side rail padded channel',(s*1.137,y,.211),(.106,.089,.259),M['Linen'],.035)
for i in range(23):
 x=-1.066+i*2.132/22
 cube('Headboard tall padded channel %02d'%i,(x,-.278,.494),(.101,.153,.90),M['Linen'],.043)
cube('Mattress ivory side band',(0,-1.455,.410),(2.19,2.27,.180),M['Linen'],.065)
# Piped mattress perimeter in genuine rounded strip objects.
for s in [-1,1]:rod('Mattress piping side',(s*1.086,-.41,.481),(s*1.086,-2.52,.481),.006,M['Linen'])
rod('Mattress piping foot',(-1.02,-2.572,.479),(1.02,-2.572,.479),.006,M['Linen'])
cur='05_Bedding'
cube('Large low pile bedside rug',(0,-1.55,.020),(3.24,3.11,.020),M['Rug'],.008)
# Light sheet overhang visible under the checker duvet, with draped foot lip.
def cloth(name,kind):
 nu=65;nv=73;vs=[];uv=[]
 for j in range(nv):
  t=j/(nv-1);yy=-.59-t*2.03
  for i in range(nu):
   u=i/(nu-1);xx=(u-.5)*2.50
   side=max(0,(abs(xx)-1.025)/.225);tail=max(0,(t-.86)/.14)
   zz=.516-.20*(side**.72)-.08*(tail**.8)
   zz+=.017*math.sin(xx*11+yy*13)*(.25+.75*side)+.009*math.sin(yy*21+xx*3)+.008*math.cos(xx*22-yy*8)
   if kind=='sheet':zz-=.035;yy2=yy-.02;xx2=xx*.99
   else:yy2=yy+.06;xx2=xx
   vs.append((xx2,yy2,zz));uv.append(((xx+1.25)/1.28,t*2.03/1.28))
 fs=[]
 for j in range(nv-1):
  for i in range(nu-1):a=j*nu+i;fs.append((a,a+1,a+1+nu,a+nu))
 o=mesh(name,vs,fs,M['Linen'] if kind=='sheet' else M['Checker'],uv);m=o.modifiers.new('Real fabric thickness','SOLIDIFY');m.thickness=.005;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
cloth('Ivory sheet lower drape','sheet');cloth('Checker duvet with irregular soft drape','duvet')
# Exposed ivory folded throw along lower foot edge.
nu=65;nv=12;vs=[];uv=[]
for j in range(nv):
 t=j/(nv-1)
 for i in range(nu):
  u=i/(nu-1);xx=(u-.5)*2.25;yy=-2.48-t*.15;zz=.44-.085*t+.007*math.sin(xx*23)+.005*math.cos(xx*33+t*3);vs.append((xx,yy,zz));uv.append((u*3,t*.3))
fs=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)];o=mesh('Ivory exposed lower blanket fold',vs,fs,M['Linen'],uv);m=o.modifiers.new('Blanket thickness','SOLIDIFY');m.thickness=.018;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
for idx,(x,y,z,rz) in enumerate([(-.45,-.542,.715,.03),(.43,-.63,.627,-.045)]):
 o=cube('Checker pillow '+str(idx),(x,y,z),(.76,.21,.42 if idx==0 else .30),M['Checker'],.089,rot=(math.radians(-12 if idx==0 else -38),0,rz))
 uvbox(o,1/1.04)
cur='06_Bedside_cabinet'
nx=1.49;ny=-.64
cube('Cabinet top',(nx,ny,.68),(.67,.43,.035),M['Cabinet'],.007)
cube('Cabinet bottom',(nx,ny,.279),(.67,.43,.028),M['Cabinet'],.005)
for x in [nx-.32,nx+.32,nx+.105]:cube('Cabinet vertical partition',(x,ny,.476),(.026,.43,.375),M['Cabinet'],.004)
cube('Cabinet back',(nx,ny+.203,.48),(.62,.018,.37),M['Cabinet'],.002)
cube('Cabinet left opaque door',(nx-.103,ny-.204,.481),(.398,.025,.366),M['Cabinet'],.005)
for x in [nx+.172,nx+.254]:cube('Open right cabinet slender vertical bar',(x,ny-.204,.477),(.011,.017,.35),M['Cabinet'],.002)
rod('Side cabinet small handle',(nx-.342,ny-.113,.604),(nx-.342,ny+.027,.604),.008,M['dark'])
for x in [nx-.273,nx+.273]:
 for y in [ny-.15,ny+.15]:rod('Slender support under cabinet',(x,y,.28),(x,y,.028),.009,M['dark'])
 rod('Cabinet sled foot',(x,ny-.20,.026),(x,ny+.20,.026),.009,M['dark'])
cur='07_Lamp_clock_frames'
# Small image fronts are original graphic approximations on individual framed planes.
def artwork_mat(name,file):
 m=mat(name,(1,1,1),.7);n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures'/file));t.image.pack();l.new(t.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);return m
postmat=artwork_mat('Approximate illustrated red print','Poster_approximation.png');portraitmat=artwork_mat('Approximate framed portrait','Portrait_approximation.png')
def picture(name,x,y,z,w,h,ma):
 cube(name+' solid backing',(x,y+.012,z),(w,.024,h),M['black'],.005)
 for xx in [x-w/2,x+w/2]:cube(name+' vertical frame',(xx,y-.006,z),(.024,.028,h+.025),M['black'],.004)
 for zz in [z-h/2,z+h/2]:cube(name+' horizontal frame',(x,y-.006,zz),(w,.028,.024),M['black'],.004)
 mesh(name+' UV print',[(x-w/2+.018,y-.023,z-h/2+.018),(x+w/2-.018,y-.023,z-h/2+.018),(x+w/2-.018,y-.023,z+h/2-.018),(x-w/2+.018,y-.023,z+h/2-.018)],[(0,1,2,3)],ma,[(0,0),(1,0),(1,1),(0,1)])
picture('Wall comic poster approximation',.064,-.046,1.966,1.15,1.005,postmat)
picture('Small bedside framed portrait',1.285,-.69,.817,.192,.223,portraitmat)
# A small support wedge behind portrait.
cube('Portrait easel foot',(1.285,-.632,.708),(.13,.09,.02),M['black'],.005)
# Lamp has open hemisphere canopy with an actual inner shell and thin stem.
lx=1.54;ly=-.588
cyl('Mushroom lamp low circular base',(lx,ly,.706),.096,.014,M['dark'])
rod('Mushroom lamp narrow metal stem',(lx,ly,.72),(lx,ly,1.095),.008,M['dark'])
vs=[];fs=[];uv=[];nr=12;ns=48
for j in range(nr):
 theta=(j/(nr-1))*(math.pi/2);r=.107*math.sin(theta);zz=1.004+.127*math.cos(theta)
 for k in range(ns):
  phi=k/ns*2*math.pi;vs.append((lx+r*math.cos(phi),ly+r*math.sin(phi),zz));uv.append((k/ns,j/(nr-1)))
for j in range(nr-1):
 for k in range(ns):a=j*ns+k;b=j*ns+(k+1)%ns;fs.append((a,b,b+ns,a+ns))
o=mesh('Orange mushroom lamp domed shade',vs,fs,M['Orange'],uv);sol=o.modifiers.new('Lamp shade inner thickness','SOLIDIFY');sol.thickness=.004;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sol.name)
rod('Lamp top finial',(lx,ly,1.126),(lx,ly,1.149),.004,M['dark'])
bulb=mat('Warm lamp bulb',(.95,.54,.18),.25);b=bulb.node_tree.nodes.get('Principled BSDF');b.inputs['Emission Color'].default_value=(1,.55,.2,1);b.inputs['Emission Strength'].default_value=1.6;sphere('Lamp inner bulb',(lx,ly,1.012),(.017,.017,.022),bulb)
# Blue analog alarm clock, read from right-hand reference.
clx=1.67;cly=-.71;clz=.755
cyl('Clock blue case',(clx,cly,clz),.058,.030,M['blue'],(math.pi/2,0,0))
cyl('Clock ivory dial',(clx,cly-.019,clz),.049,.002,M['cream'],(math.pi/2,0,0))
for k in range(12):
 a=k*2*math.pi/12;rod('Clock tick',(clx+.039*math.sin(a),cly-.022,clz+.039*math.cos(a)),(clx+.044*math.sin(a),cly-.022,clz+.044*math.cos(a)),.0012,M['dark'])
rod('Clock hour hand',(clx,cly-.024,clz),(clx-.021,cly-.024,clz+.018),.0016,M['dark']);rod('Clock minute hand',(clx,cly-.025,clz),(clx+.008,cly-.025,clz+.034),.0012,M['dark'])
for sx in [-1,1]:
 sphere('Clock twin bell',(clx+sx*.037,cly,clz+.052),(.024,.019,.010),M['blue'])
 rod('Clock small foot',(clx+sx*.03,cly,clz-.04),(clx+sx*.041,cly-.006,.701),.003,M['dark'])
cur='08_Plant_inferred_hidden'
# Right edge foliage observed; exact planter and rear branches hidden, inferred.
px=2.92;py=-.31
cyl('Plant pot lower',(px,py,.17),.165,.32,M['pot'],vertices=40)
cyl('Plant pot rim',(px,py,.32),.185,.045,M['pot'],vertices=40)
cyl('Visible pot soil',(px,py,.344),.166,.010,M['soil'],vertices=32)
for q in range(12):
 ang=q*2.399;h=.81+q*.065;reach=.34+.17*math.sin(q*1.13)**2
 start=(px,py,.33);end=(px+math.cos(ang)*reach,py+math.sin(ang)*reach,h)
 mid=(px+math.cos(ang)*reach*.22,py+math.sin(ang)*reach*.22,h*.72)
 rod('Leaf stalk lower',start,mid,.0045,M['vein']);rod('Leaf stalk upper',mid,end,.003,M['vein'])
 # Curved leaf mesh, its silhouette is a wide split-leaf/monstera approximation.
 tip=Vector((end[0]+math.cos(ang)*.42,end[1]+math.sin(ang)*.42,end[2]+.03));base=Vector(end);tangent=(tip-base).normalized();cross=Vector((-math.sin(ang),math.cos(ang),0));v=[];uv=[];segments=16
 for i in range(segments+1):
  t=i/segments;c=base+(tip-base)*t;c.z+=.07*math.sin(t*math.pi)
  width=.17*(math.sin(math.pi*t)**.65)*(1-.28*math.sin(t*7*math.pi)**8)
  for side in [-1,0,1]:
   pt=c+cross*width*side;pt.z-=.025*abs(side)*math.sin(t*math.pi);v.append(tuple(pt));uv.append(((side+1)/2,t))
 f=[]
 for i in range(segments):
  for k in range(2):a=i*3+k;f.append((a,a+1,a+4,a+3))
 leaf=mesh('Curved broad plant leaf %02d'%q,v,f,M['Leaf'],uv);sol=leaf.modifiers.new('Leaf thickness','SOLIDIFY');sol.thickness=.0015;bpy.context.view_layer.objects.active=leaf;bpy.ops.object.modifier_apply(modifier=sol.name)
 rod('Leaf main rib',end,tuple(tip),.0016,M['vein'])
cur='09_Cameras_lighting'
def camera(name,loc,target,lens,shift=0):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COL[cur].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.sensor_width=36;d.clip_start=.05;d.clip_end=100;d.shift_y=shift;return o
camera('MATCH_front_50m07_same_axis',(0,-13.5,2.60),(0,0,.97),83)
camera('MATCH_close_50m10_same_axis',(-.03,-7.3,1.61),(-.03,0,1.46),83)
camera('QA_wide_level',(3.3,-5.75,1.52),(-.15,-.7,1.52),27,shift=-.07)
camera('QA_opposite_level',(-3.1,-5.45,1.5),(.3,-.9,1.5),27,shift=-.07)
def area(name,loc,target,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);COL[cur].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area('Large soft frontal key',(-2.1,-4.2,3.0),(0,-1.1,.55),370,3.8,(1,.79,.62))
area('Soft camera right fill',(2.2,-3,2.6),(.2,-1.2,.65),190,2.8,(1,.92,.8))
area('Upper diffuse room ambient',(0,-1.7,3.2),(0,-1.6,0),100,3,(1,.85,.72))
s=bpy.context.scene;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.36,.30,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.23
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=False;s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1188;s.render.resolution_y=668;s.render.resolution_percentage=70;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.35
s.unit_settings.system='METRIC';s.unit_settings.length_unit='METERS'
s['SOURCE']='BV1mx4y1z7oY 2024-04-19 与星瞳共度的一天';s['EVIDENCE_LIMIT']='Single forward axis with wide and tight framing. No independent side or reverse reference. Hidden surfaces, sizes and room depth are inference.';s['ARTWORK']='Individually drawn graphic approximations; no screenshot applied to room surfaces.';s['NO_CHARACTER']=True;s['BED_ASSUMPTIONS']='Bed outer 2.29 x 2.30 m, mattress 2.19 x 2.27 m, top 0.50 m, headboard 0.944 m. Scale inferred.'
for o in bpy.data.objects:
 if o.type=='MESH' and not o.data.uv_layers:uvbox(o)
s.camera=bpy.data.objects['QA_wide_level'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'bedroom_blockout.blend'),compress=True)
for cam,file in [('QA_wide_level','blockout_wide'),('MATCH_front_50m07_same_axis','blockout_front')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(R/'renders'/(file+'.png'));bpy.ops.render.render(write_still=True)
print('BEDROOM_BLOCKOUT_READY')
