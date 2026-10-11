import bpy,math,random,json,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];random.seed(71110)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
S.world=bpy.data.worlds.new('Hall World')
COL={}
for name in ['01_Architecture','02_Fluted_Columns','03_Arched_Glazing','04_Banquet_Tables','05_Cakes_and_Pastries','06_Flowers','07_Gifts_and_Balloons','08_Lighting','09_Cameras']:
 c=bpy.data.collections.new(name);S.collection.children.link(c);COL[name[:2]]=c

def mat(name,col,rough=.5,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if emit:b.inputs['Emission Color'].default_value=(*col,1);b.inputs['Emission Strength'].default_value=emit
 return m

def pbr(stem,metal=0):
 m=mat(stem+' | original UV PBR',(.4,.3,.2),.5,metal);n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF')
 for ch,cs in [('BaseColor','sRGB'),('Roughness','Non-Color'),('Normal','Non-Color')]:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures'/f'{stem}_{ch}.png'));t.image.colorspace_settings.name=cs;t.image.pack()
  if ch=='BaseColor':l.new(t.outputs['Color'],b.inputs['Base Color'])
  elif ch=='Roughness':l.new(t.outputs['Color'],b.inputs['Roughness'])
  else:
   nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.35;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],b.inputs['Normal'])
 return m
ivory=pbr('IvoryMarble');dark=pbr('DarkMarble');stone=pbr('RoseStone');plaster=pbr('Plaster');linen=pbr('IvoryLinen');gold=pbr('AntiqueGold',.65)
cream=mat('Vanilla icing',(.86,.67,.45),.48);icing=mat('Cream piping',(.97,.83,.62),.45);pink=mat('Rose pink satin',(.45,.033,.095),.25,.15);red=mat('Garnet ribbon',(.33,.011,.039),.28,.25);lightpink=mat('Soft pink paper',(.60,.24,.32),.55);purple=mat('Plum wrapping',(.19,.032,.12),.5);giftwhite=mat('Pearl paper',(.78,.61,.58),.6);green=mat('Flower foliage',(.045,.095,.027),.62);rose=mat('Raspberry roses',(.50,.016,.07),.52);petal=mat('Blush roses',(.73,.27,.36),.6);bronze=mat('Dark bronze',(.12,.065,.027),.35,.7);glass=mat('Night blue glazing',(.023,.061,.12),.23,.12,.16);bulb=mat('Warm candle flame',(.95,.62,.22),.3,0,5);crystal=mat('Faceted crystal',(.69,.63,.43),.13,.2);grout=mat('Cream grout',(.13,.105,.08),.8)

# All visible architecture and furnishings are editable real mesh.
def mesh(name,vs,fs,ma,col='01',smooth=False,uvscale=1):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);COL[col].objects.link(o)
 if ma:me.materials.append(ma)
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=smooth;a=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=a]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*uvscale,v[axes[1]]*uvscale)
 return o

def cube(name,loc,d,ma,col='01',bev=0):
 x,y,z=loc;a,b,c=[v/2 for v in d];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];o=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,col)
 if bev:m=o.modifiers.new('Rounded physical edge','BEVEL');m.width=bev;m.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def lathe(name,x,y,profile,ma,col='02',n=48,flutes=0):
 vs=[];fs=[]
 for z,r in profile:
  for k in range(n):
   a=k*math.tau/n;rr=r-(flutes*.032*(.5+.5*math.cos(a*24)) if r>.38 else 0);vs.append((x+rr*math.cos(a),y+rr*math.sin(a),z))
 for j in range(len(profile)-1):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
 fs+=[tuple(range(n-1,-1,-1)),tuple((len(profile)-1)*n+k for k in range(n))]
 return mesh(name,vs,fs,ma,col,True)

def cyl(name,a,b,r,ma,col='05',n=12):
 v=Vector(b)-Vector(a);w=v.normalized();u=w.cross(Vector((0,0,1)))
 if u.length<.01:u=w.cross(Vector((0,1,0)))
 u.normalize();vv=w.cross(u);vs=[tuple(Vector(p)+r*(math.cos(k*math.tau/n)*u+math.sin(k*math.tau/n)*vv)) for p in [a,b] for k in range(n)];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)];return mesh(name,vs,fs,ma,col,True)

def ellipsoid(name,loc,sc,ma,col='07',n=16,m=10):
 vs=[];fs=[]
 for j in range(m+1):
  p=math.pi*j/m
  for i in range(n):a=i*math.tau/n;vs.append((loc[0]+sc[0]*math.sin(p)*math.cos(a),loc[1]+sc[1]*math.sin(p)*math.sin(a),loc[2]+sc[2]*math.cos(p)))
 for j in range(m):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
 return mesh(name,vs,fs,ma,col,True)

def curve_mesh(name,pts,r,ma,col):
 # Connected beveled curve converted to mesh immediately for GLB parity.
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=1;s=cu.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,cu);COL[col].objects.link(o);o.data.materials.append(ma);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

# Measured in nominal metres, scale inferred rather than recovered from source assets.
W=14.0;L=27.0;H=8.8;back=22.0;front=-5.0
cube('Continuous marble floor substrate',(0,8.5,-.12),(W,L,.22),grout)
# Clipped octagonal cream tiles with small contrasting diamond inserts, all real polygons.
vs=[];fs=[];vd=[];fd=[];pitch=1.28;cut=.22;h=pitch/2-.004
for i in range(-5,6):
 for j in range(-4,18):
  x=i*pitch;y=j*pitch
  pts=[(-h+cut,-h),(h-cut,-h),(h,-h+cut),(h,h-cut),(h-cut,h),(-h+cut,h),(-h,h-cut),(-h,-h+cut)];a=len(vs);vs += [(x+xx,y+yy,.003) for xx,yy in pts];fs.append(tuple(range(a,a+8)))
  a=len(vd);rr=cut-.008;vd +=[(x+pitch/2+xx,y+pitch/2+yy,.004) for xx,yy in [(-rr,0),(0,-rr),(rr,0),(0,rr)]];fd.append(tuple(range(a,a+4)))
mesh('Octagonal polished ivory floor tiles',vs,fs,ivory);mesh('Dark marble diamond inlay',vd,fd,dark)
# Side walls and modest inferred roof, concealed in reference-facing view.
for side in [-1,1]:
 cube('Rose plaster side wall',(side*7.1,8.5,H/2),(.2,L,H),plaster)
 cube('Stone lower skirting',(side*6.98,8.5,.20),(.12,L,.40),stone,bev=.018)
 for z,wid,dep in [(7.85,.16,.22),(8.10,.24,.26),(8.30,.35,.35)]:cube('Stepped upper entablature',(side*6.95,8.5,z),(dep,L,wid),stone,bev=.02)
 for y in [-1.0,5.0,11.0,17.0]:
  cube('Side recessed night panel',(side*6.975,y,4.1),(.035,3.15,6.6),glass,'03')
  for yy in [y-1.64,y+1.64]:cube('Side window vertical moulding',(side*6.93,yy,4.05),(.10,.14,6.8),gold,'03',.016)
  for zz in [.68,7.43]:cube('Side window sill and lintel',(side*6.92,y,zz),(.12,3.42,.17),stone,'03',.02)
  cube('Side window narrow mullion',(side*6.90,y,4.08),(.13,.055,6.60),bronze,'03')
  for zz in [2.5,5.8]:cube('Side window transom',(side*6.90,y,zz),(.13,3.2,.055),bronze,'03')
# No ceiling: not constrained by references.
# Four columns per side. Occluded counts are inferred and stated in README.
for side in [-1,1]:
 for idx,y in enumerate([0.0,6.0,12.0,18.0]):
  x=side*4.25;tag=f'{"L" if side<0 else "R"}{idx+1}'
  lathe('Column '+tag+' moulded round base',x,y,[(0,.82),(.09,.82),(.13,.76),(.21,.76),(.25,.69),(.31,.66),(.36,.62),(.42,.59),(.48,.60),(.51,.55)],stone)
  lathe('Column '+tag+' 24-flute entasis shaft',x,y,[(.50,.54),(.68,.545),(1.5,.536),(3.4,.510),(5.5,.478),(7.2,.46),(7.36,.46)],stone,n=192,flutes=1)
  lathe('Column '+tag+' capital collars',x,y,[(7.30,.48),(7.40,.53),(7.48,.58),(7.56,.60),(7.78,.66),(7.85,.71),(7.93,.71),(8.00,.68)],gold)
  cube('Column '+tag+' capital abacus',(x,y,8.06),(1.53,1.53,.20),stone,'02',.025)
  # Low-relief acanthus-like folded leaves, actual petal-shaped geometry.
  for k in range(12):
   a=k*math.tau/12;pts=[]
   for t in range(9):
    zz=7.46+t*.048;rr=.53+.12*math.sin(t/8*math.pi*.7);wi=.12*math.sin(t/8*math.pi)
    for q in [-1,1]:pts.append((x+rr*math.cos(a)-q*wi*math.sin(a),y+rr*math.sin(a)+q*wi*math.cos(a),zz))
   mesh('Capital folded leaf',pts,[(j*2,j*2+1,j*2+3,j*2+2) for j in range(8)],gold,'02',True)
# End wall and grand central arched night glazing.
for x,w in [(-5.65,2.7),(5.65,2.7)]:cube('End plaster wing',(x,back,H/2),(w,.25,H),plaster)
cube('Grand window top spandrel',(0,back,8.23),(8.6,.25,1.16),plaster)
# Glass rectangular lower part plus semicircular arch geometry.
ww=6.15;spring=5.20;rad=ww/2
poly=[(-rad,0),(rad,0),(rad,spring)]+[(rad*math.cos(k*math.pi/40),spring+rad*math.sin(k*math.pi/40)) for k in range(1,41)]
mesh('Central arched blue glass',[(x,back+.02,z) for x,z in poly],[tuple(range(len(poly)))],glass,'03')
for xx in [-rad,rad,-rad/3,rad/3]:cube('Central window full-height mullion',(xx,back-.07,3.68),(.095,.18,7.36),stone,'03',.015)
for zz in [0.12,3.36,5.2]:cube('Central window horizontal frame',(0,back-.07,zz),(ww,.18,.09),stone,'03',.009)
for rrr in [rad,rad+.15]:curve_mesh('Arched carved window surround',[(rrr*math.cos(k*math.pi/64),back-.07,spring+rrr*math.sin(k*math.pi/64)) for k in range(65)],.06,stone,'03')
# Unlit opening behind blue glazing and balcony railing visible along the base.
for x in [-3.64,3.64]:
 lathe('End slender fluted pier',x,back-.12,[(0,.53),(.28,.48),(.5,.37),(7.6,.35),(7.78,.48),(8,.5)],stone,n=144,flutes=1)
for x in [i*.47 for i in range(-6,7)]:lathe('Balcony turned baluster',x,back+.18,[(.06,.07),(.16,.11),(.33,.07),(.46,.14),(.64,.10),(.80,.05),(.91,.08)],stone,'03',20)
for zz in [.08,.97]:cube('Balcony continuous stone rail',(0,back+.19,zz),(6.25,.27,.15),stone,'03',.025)
# Subtle night particles outside window, geometric points rather than a scene image.
for i in range(65):
 x=random.uniform(-3,3);z=random.uniform(1,7.6)
 if z>spring and x*x+(z-spring)**2>rad*rad:continue
 ellipsoid('Outside dim light point',(x,back+.09,z),(.012,.014,.018),mat('Night pinprick '+str(i),(.12,.22,.37),.6,0,.4),'03',6,4)
# Real draped rectangular banquet cloth, tabletop and four metal legs.
def table(x,y,w,d,name):
 top=1.00;cube(name+' wooden top',(x,y,top-.045),(w,d,.075),stone,'04',.024)
 for xx in [x-w/2+.14,x+w/2-.14]:
  for yy in [y-d/2+.12,y+d/2-.12]:cyl(name+' slender brass leg',(xx,yy,.035),(xx,yy,top-.05),.025,gold,'04',12)
 cube(name+' white linen top',(x,y,top+.014),(w+.035,d+.035,.028),linen,'04',.015)
 # Four hanging fabric panels with distinct folds and scalloped free edges.
 for axis,length,depth in [(0,w,.46),(1,d,.49)]:
  for side in [-1,1]:
   vs=[];fs=[];nu=48;nv=10
   for j in range(nv+1):
    t=j/nv
    for i in range(nu+1):
     u=i/nu;along=(u-.5)*(length+.07);out=t*.045+.028*math.sin(u*math.tau*9)*t;z=top+.014-depth*t+.03*math.cos(u*math.tau*4)*t*t
     if axis==0:vs.append((x+along,y+side*(d/2+.017+out),z))
     else:vs.append((x+side*(w/2+.017+out),y+along,z))
   for j in range(nv):
    for i in range(nu):a=j*(nu+1)+i;fs.append((a,a+1,a+nu+2,a+nu+1))
   o=mesh(name+' draped cloth',vs,fs,linen,'04',True);m=o.modifiers.new('Physical cloth thickness','SOLIDIFY');m.thickness=.003
 return top+.028

def cake(x,y,z,scale=1,tiers=4):
 lathe('Cake pedestal',x,y,[(z,.30*scale),(z+.025,.31*scale),(z+.055,.29*scale),(z+.16*scale,.045*scale),(z+.24*scale,.10*scale),(z+.26*scale,.30*scale)],gold,'05',32)
 z+=.27*scale
 for k in range(tiers):
  rr=(.29-.060*k)*scale;hh=.22*scale
  lathe('Tiered celebration cake',x,y,[(z,rr),(z+.015,rr+.01*scale),(z+hh-.014,rr+.008*scale),(z+hh,rr)],cream,'05',40)
  for t in [0,1]:lathe('Cake icing rim',x,y,[(z+t*hh-.01,rr+.012),(z+t*hh+.013,rr+.016)],icing,'05',40)
  for j in range(14):a=j*math.tau/14;ellipsoid('Cake piped rosette',(x+rr*math.cos(a),y+rr*math.sin(a),z+.05*scale),(.021*scale,.021*scale,.022*scale),icing,'05',8,5)
  z+=hh
 cyl('Cake single candle',(x,y,z),(x,y,z+.11*scale),.012*scale,cream,'05');ellipsoid('Candle flame',(x,y,z+.125*scale),(.013,.013,.031),bulb,'05',8,5)

def flowers(x,y,z,sz=1):
 lathe('Flower urn',x,y,[(z,.085*sz),(z+.02*sz,.12*sz),(z+.21*sz,.15*sz),(z+.32*sz,.095*sz),(z+.34*sz,.12*sz)],gold,'06',24)
 # Petals accumulated per bouquet into only three meshes.
 vv={0:[],1:[],2:[]};ff={0:[],1:[],2:[]}
 def leaf(center,scale,key,ang):
  vs=vv[key];fs=ff[key];start=len(vs);cx,cy,cz=center
  for zz,rr in [(-scale*.25,0),(0,scale),(.18*scale,scale*.78)]:
   for j in range(7):a=j*math.tau/7+ang;vs.append((cx+rr*math.cos(a),cy+rr*math.sin(a),cz+zz))
  for k in range(2):
   for j in range(7):a=start+k*7+j;b=start+k*7+(j+1)%7;fs.append((a,b,b+7,a+7))
  fs.append(tuple(start+14+j for j in range(7)))
 for j in range(17):
  a=j*2.4;rr=random.uniform(.08,.26)*sz;tip=(x+rr*math.cos(a),y+rr*math.sin(a),z+random.uniform(.43,.77)*sz);cyl('Bouquet visible stem',(x,y,z+.27*sz),tip,.006*sz,green,'06',6)
  leaf((tip[0],tip[1],tip[2]-.07*sz),.13*sz,2,a)
  for k in range(5):
   aa=a+k*2.4;loc=(tip[0]+.029*sz*math.cos(aa),tip[1]+.029*sz*math.sin(aa),tip[2]+k*.009*sz);leaf(loc,(.065-.006*k)*sz,j%2,aa)
 for k,ma in [(0,rose),(1,petal),(2,green)]:mesh('Bouquet petals' if k<2 else 'Bouquet leaves',vv[k],ff[k],ma,'06',True)

def gift(x,y,w,d,h,ma):
 cube('Wrapped gift box',(x,y,h/2),(w,d,h),ma,'07',.013);cube('Gift box lid',(x,y,h+.01),(w+.025,d+.025,.055),ma,'07',.01)
 cube('Gift narrow cross ribbon',(x,y,h+.04),(.055,d+.03,.009),gold,'07');cube('Gift wide cross ribbon',(x,y,h+.046),(w+.03,.055,.009),red,'07')
 for xx in [-w/2,w/2]:cube('Gift side ribbon',(x+xx,y,h/2),(.008,.055,h),red,'07')
 for yy in [-d/2,d/2]:cube('Gift side ribbon',(x,y+yy,h/2),(.055,.008,h),gold,'07')
 for sg in [-1,1]:curve_mesh('Gift ribbon bow',[(x+sg*.115*(1-math.cos(t*math.tau/24)),y+.055*math.sin(t*math.tau/24),h+.06+.06*math.sin(t*math.pi/24)) for t in range(25)],.009,red,'07')

def balloons(x,y,z,sz=1):
 for j,(xx,yy,zz) in enumerate([(-.22,0,.18),(.12,-.07,.31),(.31,.06,.03),(-.03,.12,-.12),(-.27,.12,-.18),(0,-.03,0)]):
  pos=(x+xx*sz,y+yy*sz,z+zz*sz);ellipsoid('Pink balloon',pos,(.22*sz,.19*sz,.255*sz),[pink,red,purple][j%3],'07',20,12);cyl('Balloon knot',(pos[0],pos[1],pos[2]-.26*sz),(pos[0],pos[1],pos[2]-.29*sz),.019*sz,pink,'07')
  curve_mesh('Balloon hanging ribbon',[(pos[0]+.05*math.sin(t*.7),pos[1]+.04*math.sin(t),pos[2]-.29*sz-t*.075*sz) for t in range(20)],.003,gold,'07')

# Independently observed staggered cake buffet tables beside column rows.
for side in [-1,1]:
 for idx,y in enumerate([.9,8.3,15.2]):
  x=side*4.95;w=3.0 if idx==0 else 2.25;d=1.15;z=table(x,y,w,d,f'Buffet {side} {idx+1}')
  cake(x+side*.48,y,z,1.1 if idx==0 else .66,4)
  flowers(x-side*.72,y+.12,z,.85 if idx==0 else .65)
  if idx==2:cake(x-side*.43,y,z,.5,3)
  # Plates, pastries, glasses and candlesticks are individual meshes.
  for k in range(5):
   px=x-w/2+.24+k*(w-.48)/4;py=y-.29;lathe('Porcelain dessert plate',px,py,[(z+.004,.095),(z+.016,.103),(z+.025,.085)],giftwhite,'05',20)
   lathe('Small petit four',px,py,[(z+.025,.056),(z+.091,.054),(z+.106,.043)],cream,'05',16)
   ellipsoid('Pastry raspberry',(px,py,z+.118),(.025,.025,.022),rose,'05',8,5)
  for k in range(3):
   px=x-.40+k*.28;py=y+.26;lathe('Banquet goblet',px,py,[(z,.038),(z+.012,.042),(z+.13,.012),(z+.15,.045),(z+.23,.052)],crystal,'05',16)
  for j in range(5 if idx==0 else 3):
   gx=x-side*.10+random.uniform(-.85,.85);gy=y-1.1+random.uniform(-.23,.16);gift(gx,gy,random.uniform(.26,.45),random.uniform(.27,.42),random.uniform(.23,.43),[pink,purple,giftwhite,lightpink][j%4])
  if idx!=1:balloons(x+side*.4,y+.32,2.00+idx*.17,.9 if idx==0 else .7)
# Rear small buffet seen through the central opening.
z=table(0,21.0,2.5,.63,'End small buffet');flowers(.8,21,z,.55)
for xx in [-.65,-.2,.25]:lathe('End serving tray',xx,20.98,[(z,.14),(z+.04,.16)],gold,'05',20)
balloons(.2,21.1,2.13,.67)
# A few loose balloons on floor, as seen around plinth gifts.
for side in [-1,1]:
 for y in [1.1,8.5]:ellipsoid('Loose balloon at column base',(side*3.82,y,.28),(.24,.21,.29),pink,'07',20,12)

# Wall-mounted candelabra, geometric crystal drops and soft warm illumination.
def area(name,loc,target,energy,size,color,size_y=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='RECTANGLE';d.size=size;d.size_y=size_y or size;o=bpy.data.objects.new(name,d);COL['08'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o

def sconce(x,y,z):
 cube('Candelabra wall plate',(x,y+.08,z),(.15,.12,.50),gold,'08',.06)
 for sg in [-1,0,1]:
  curve_mesh('Candelabra curved arm',[(x+sg*.29*t/12,y-.10-.19*math.sin(t*math.pi/24),z-.16+.28*(t/12)**2) for t in range(13)],.026,gold,'08')
  xx=x+sg*.29;yy=y-.29;zz=z+.12;cyl('Ivory wall candle',(xx,yy,zz),(xx,yy,zz+.30),.036,icing,'08',12);ellipsoid('Wall candle luminous tip',(xx,yy,zz+.345),(.035,.035,.08),bulb,'08',10,6)
  for dx in [-.045,.045]:ellipsoid('Crystal pendant',(xx+dx,yy,z-.32),(.026,.025,.084),crystal,'08',8,5)
 area('Candelabra light',(x,y-.4,z+.35),(x,y-2,z),100,.7,(1,.56,.26))
for x in [-4.8,4.8]:sconce(x,21.79,4.45)
for side in [-1,1]:
 for y in [3,9,15,20]:
  # Interior warm pools between columns. They do not substitute for geometry.
  area('Soft interior ceiling pool',(side*3.3,y,6.9),(side*2.9,y,0),250,3.6,(1,.66,.39),3.5)
area('Broad warm forward fill',(0,-3.9,5.4),(0,11,1.3),900,6,(1,.66,.46),4)
area('Blue night light through grand window',(0,21.5,4.3),(0,6,1.2),1400,5.3,(.30,.48,1),7)
area('Soft center aisle fill',(0,7,6.5),(0,9,0),350,5,(1,.78,.60),8)

# Reference camera and a level wide view share all the geometry.
def camera(name,loc,target,lens,shift=0):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.05;d.clip_end=200;d.shift_y=shift;o=bpy.data.objects.new(name,d);COL['09'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o
camera('MATCH_A_45m15_empty_aisle',(-.04,-9.1,1.07),(0,18,1.07),36,.025)
camera('MATCH_B_75m07_oblique',(-1.7,-6.2,1.30),(.25,18,1.45),28,.005)
camera('QA_WIDE_LEVEL_FRONT',(0,-4.50,1.65),(0,18,1.65),19)
camera('QA_REVERSE_LEVEL',(0,20.5,1.65),(0,-4,1.65),19)
camera('QA_SIDE_LEVEL',(-6.55,7.4,1.6),(5.8,11.7,1.6),19)
S.render.engine='CYCLES';S.cycles.samples=20;S.cycles.use_denoising=False;S.cycles.max_bounces=5;S.cycles.diffuse_bounces=3;S.cycles.glossy_bounces=3;S.render.threads_mode='FIXED';S.render.threads=4;S.render.resolution_x=1188;S.render.resolution_y=668;S.render.resolution_percentage=65;S.render.image_settings.file_format='PNG';S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.10,.16,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.15
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=1.05;S.unit_settings.system='METRIC'
S['Reconstruction']='Xingtong castle banquet hall; real mesh from 2023-11-10 BV1aw411T7ws, 45:15 and 75:07.';S['Scale']='Nominal metres inferred from table and architectural priors, not surveyed dimensions.';S['Inferred']='Four columns per row and off-camera wall extents inferred. Rear closure and ceiling omitted. Garden excluded.';S['Text']='No invented lettering and no characters.'
S.camera=bpy.data.objects['QA_WIDE_LEVEL_FRONT'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/01_castle_hall_material.blend'))
for cname in ['MATCH_A_45m15_empty_aisle','MATCH_B_75m07_oblique','QA_WIDE_LEVEL_FRONT']:
 S.camera=bpy.data.objects[cname];S.render.filepath=str(R/'renders'/('draft_'+cname+'.png'));bpy.ops.render.render(write_still=True)
# Full-white uses exactly the same evaluated mesh; material slots are changed only.
white=mat('Neutral white clay',(.73,.73,.73),.72)
for o in bpy.data.objects:
 if o.type=='MESH':
  for i in range(len(o.data.materials)):o.data.materials[i]=white
S.camera=bpy.data.objects['QA_WIDE_LEVEL_FRONT'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/02_castle_hall_white.blend'));S.render.filepath=str(R/'renders/draft_WHITE_QA_WIDE_LEVEL_FRONT.png');bpy.ops.render.render(write_still=True)
print('HALL_FIRST_PASS_DONE',flush=True)
