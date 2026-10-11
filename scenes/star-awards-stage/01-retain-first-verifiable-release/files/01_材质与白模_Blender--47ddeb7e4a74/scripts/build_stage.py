import bpy, math, json, os, sys, hashlib
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
from pathlib import Path
P=Path(__file__).resolve().parents[1];(P/'textures').mkdir(exist_ok=True)
FIT=json.loads((P/'qa/camera_fit.json').read_text());PROP=json.loads((P/'qa/shared_prop_fit.json').read_text());K=FIT['k'];H=5.7;W=5.3
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials:bpy.data.materials.remove(d)
sc=bpy.context.scene;sc.unit_settings.system='NONE';sc['单位说明']='比例建模单位，非测绘米。';sc['范围']='有顶折角舞台，摄像方向开敞；未见观众厅、舞台外房间与出入口不作事实补造。';sc['source']='https://www.bilibili.com/video/BV1xgBEYYEXF/'

def mat(name,color,metal=0,rough=.45,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit;return m
navy=mat('深蓝墙体',(0.015,.025,.08),.25,.3);dark=mat('紫黑星形实体饰板',(.065,.019,.085),.65,.2);pink=mat('粉紫发光凹槽',(.42,.09,.31),.35,.3,.35);edge=mat('金色细边',(.58,.31,.10),.8,.18);whitepink=mat('浅紫内星斜边',(.4,.24,.53),.4,.25,.35);inner=mat('内星灰紫面',(.105,.052,.13),.3,.42);glow=mat('暖白吊球',(.95,.56,.24),.1,.22,2.8);chrome=mat('玫紫镜面吊球',(.27,.075,.21),.96,.095);rodmat=mat('深色吊杆',(.06,.025,.07),.7,.28);floor=mat('黑紫反光地面',(.026,.014,.045),.7,.19);line=mat('地面淡金网格',(.57,.30,.38),.7,.25,.5);led=mat('舞台发光边线',(.69,.36,.84),.3,.23,2);cyan=mat('蓝青边光',(.05,.32,.45),.25,.3,2);gold=mat('地面虹彩金属球',(.43,.27,.14),.87,.12);rug=mat('圆形浅紫台心',(.25,.09,.24),.45,.33);struct=mat('隐藏面与支撑',(.028,.033,.06),.5,.5);neon=mat('右侧粉紫霓虹',(.76,.09,.64),.2,.3,3);cupmat=mat('杯具白瓷',(.7,.68,.66),0,.21)
glass=mat('半透粉紫玻璃球',(.37,.12,.27),.18,.10);glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.45;glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.45
allgeom=[]
def finish(o,name,m):
 o.name=name;o.data.materials.clear();o.data.materials.append(m);allgeom.append(o);return o

def cube(name,loc,scale,m,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,m)
 if bev:
  mod=o.modifiers.new('实体倒角','BEVEL');mod.width=bev;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def mesh(name,verts,faces,m):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);finish(o,name,m);return o

def cylinder(name,a,b,r,m,vertices=16):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return finish(o,name,m)

def sphere(name,loc,r,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=r,location=loc);o=finish(bpy.context.object,name,glass if m==chrome else m)
 for p in o.data.polygons:p.use_smooth=True
 return o

def polygon_prism(name,poly,zlo,zhi,m):
 n=len(poly);verts=[(x,y,z) for z in [zlo,zhi] for x,y in poly];faces=[]
 # triangulated n-gon caps robustly
 coords=[Vector((x,y,0)) for x,y in poly];tris=tessellate_polygon([coords])
 for tri in tris:
  ids=[(p if isinstance(p,int) else min(range(n),key=lambda i:(coords[i]-p).length)) for p in tri];faces.append(tuple(reversed(ids)));faces.append(tuple(i+n for i in ids))
 for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
 return mesh(name,verts,faces,m)

def clip(poly,axis,val,greater):
 out=[]
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];ina=(a[axis]>=val-1e-8) if greater else(a[axis]<=val+1e-8);inb=(b[axis]>=val-1e-8)if greater else(b[axis]<=val+1e-8)
  if ina:out.append(a)
  if ina!=inb:
   t=(val-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+t*(b[j]-a[j]) for j in range(2)))
 clean=[]
 for a in out:
  if not clean or math.hypot(a[0]-clean[-1][0],a[1]-clean[-1][1])>1e-7:clean.append(a)
 if len(clean)>1 and math.hypot(clean[0][0]-clean[-1][0],clean[0][1]-clean[-1][1])<1e-7:clean.pop()
 return clean

def folded_solid(name,poly,offset,thick,m):
 # Geometry split at crease, physical caps and wall-normal thickness. Not camera dependent.
 for side in [-1,1]:
  q=clip(poly,0,0,side==1)
  for axis,val,g in [(0,-W,True),(0,W,False),(1,(-.10 if name=='厚实折角背墙' else .015),True),(1,(H+.08 if name=='厚实折角背墙' else H-.12),False)]:q=clip(q,axis,val,g) if q else []
  if len(q)<3:continue
  v=[]
  for dep in [offset,offset+thick]:
   v.extend([(x,4-K*abs(x)+dep,z) for x,z in q])
  n=len(q);coords=[Vector((x,z,0)) for x,z in q];faces=[]
  for t in tessellate_polygon([coords]):
   ids=[(p if isinstance(p,int) else min(range(n),key=lambda i:(coords[i]-p).length)) for p in t];faces.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
  faces.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
  mesh(name+('_左' if side==-1 else '_右'),v,faces,m)

def starpoly(R,rr=None):
 rr=R*.45 if rr is None else rr
 return [(math.sin(i*math.pi/5)*(R if i%2==0 else rr),2.427+math.cos(i*math.pi/5)*(R if i%2==0 else rr)) for i in range(10)]

boundary=[(-W,-7.25),(W,-7.25),(W,4-K*W+.55),(0,4.55),(-W,4-K*W+.55)]
polygon_prism('有厚度完整舞台底板',boundary,-.38,0,struct)
polygon_prism('反光地面顶层',boundary,0,.018,floor)
# Back walls are closed thick panels; source shows a crease, ceiling and floor join.
folded_solid('厚实折角背墙',[(-W,-.10),(W,-.10),(W,H+.08),(-W,H+.08)],.28,.22,navy)
# End jambs/frame close the shell side edges, camera side remains open.
for s in [-1,1]:
 x=s*W;y=4-K*W
 cube('端部连接柱_'+str(s),(x,y+.05,H/2),(.22,.34,H),struct,.025)
 cube('前侧支撑柱_'+str(s),(x,-6.8,H/2),(.24,.24,H),struct,.02)
 cube('侧顶梁_'+str(s),(x,(y-6.8)/2,H-.13),(.24,abs(y+6.8),.26),struct,.025)
polygon_prism('连续有厚度顶板',boundary,H,H+.22,navy)
# Shell explicitly open to camera/front; no invented doors.
for R,off,ma in [(11,.19,pink),(9.7,.16,dark),(8.65,.13,pink),(7.7,.10,dark),(6.65,.08,pink),(5.65,.055,dark),(4.45,.025,pink),(3.0,0,dark),(2.38,-.035,pink),(2.12,-.07,whitepink),(1.97,-.09,inner)]:
 shape=starpoly(R)
 if R>3:shape=[(x,z-.627)for x,z in shape]
 if R<3:shape=[(x*.70,z)for x,z in shape]
 folded_solid('星形饰面_R%.2f'%R,shape,off,.34-off,ma)
# Fine gilded outer edge follows visible middle silhouette. Each edge section split at wall crease.
poly=starpoly(3)
for i in range(10):
 a,b=poly[i],poly[(i+1)%10]
 if min(a[1],b[1])<.02:continue
 cylinder('中星金属收边_%02d'%i,(a[0],4-K*abs(a[0])-.009,a[1]),(b[0],4-K*abs(b[0])-.009,b[1]),.013,edge,12)
# ceiling perimeter line; full finite emitter strips, no unbounded planes
for s in [-1,1]:
 cylinder('顶边蓝光_'+str(s),(0,3.94,H-.05),(s*W,4-K*W-.06,H-.05),.018,cyan,12)
 for t in [.15,.5,.85]:
  xx=s*W*t;yy=4-K*abs(xx)-.06;cylinder('顶边灯支座', (xx,yy,H-.05),(xx,yy,H+.02),.018,struct,12)
# Floor tile network clipped analytically to footprint, intentionally finite.
for ix in range(-7,8):
 x=ix*.72
 if abs(x)>W:continue
 cylinder('地面纵线_%d'%ix,(x,-6.85,.02),(x,4-K*abs(x)-.03,.02),.008,line,8)
for iy in range(-8,6):
 y=iy*.72;xm=min(W,(4-y)/K)
 if xm>0:cylinder('地面横线_%d'%iy,(-xm,y,.02),(xm,y,.02),.008,line,8)
# Complete disk with side/bottom; radius constrained only approximately by source floor arc.
bpy.ops.mesh.primitive_cylinder_add(vertices=160,radius=3.0,depth=.14,location=(0,-4.0,.085));finish(bpy.context.object,'圆形反光主台_完整底面',floor)
bpy.ops.mesh.primitive_torus_add(major_radius=2.97,minor_radius=.018,major_segments=160,minor_segments=8,location=(0,-4.0,.165));finish(bpy.context.object,'圆台发光实体收边',led)
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.90,depth=.008,location=(0,-4.0,.159));finish(bpy.context.object,'中央粉紫圆盘',rug)
bpy.ops.mesh.primitive_torus_add(major_radius=.90,minor_radius=.008,major_segments=96,minor_segments=8,location=(0,-4.0,.164));finish(bpy.context.object,'中央圆盘金边',edge)
# Low black access ramp connects front floor to raised deck; hidden side assumption documented.
ramp=[(-.7,-7.20),(.7,-7.20),(.7,-5.9),(-.7,-5.9)]
mesh('前部薄台过渡坡_推定',[(-.7,-7.20,0),(.7,-7.20,0),(.7,-6.80,.155),(-.7,-6.80,.155),(-.7,-7.20,-.03),(.7,-7.20,-.03),(.7,-6.80,-.03),(-.7,-6.80,-.03)],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],struct)
# Project source C lamp centers into a shared, forward-offset folded plane.
def basis(c):
 x,y,z,tx,tz,f,roll=c;pos=Vector((x,y,z));fw=(Vector((tx,3,tz))-pos).normalized();rt=fw.cross(Vector((0,0,1))).normalized();up=rt.cross(fw);return pos,rt,up,fw

def raypoint(key,uv,depth=.65):
 c=FIT['cameras'][key]['params'];pos,rt,up,fw=basis(c);u=(uv[0]-590)/c[5];v=(331.5-uv[1])/c[5];co,si=math.cos(c[6]),math.sin(c[6]);u,v=co*u+si*v,-si*u+co*v;ray=fw+u*rt+v*up
 best=None
 for s in [-1,1]:
  den=ray.y+K*s*ray.x;t=(4-depth-pos.y-K*s*pos.x)/den;pt=pos+t*ray
  if pt.x*s>=-.01 and t>0:best=pt;break
 return best or (pos+10*ray)
lamps=[('顶部簇',(555,56),23,True),('上左',(482,118),20,False),('上右',(641,118),20,False),('左上簇',(395,156),19,True),('右上簇',(721,156),20,True),('左外',(246,218),17,False),('右外',(812,218),17,False),('左白',(321,225),24,True),('右白',(886,225),24,True),('左下簇',(399,279),20,True),('右下簇',(713,280),20,True),('左低',(486,310),21,False),('右低',(639,310),21,False),('中低簇',(559,362),18,True)]
for n,uv,rpx,cluster in lamps:
 pt=Vector(PROP['lamps'][n]['point']) if n in PROP['lamps'] else raypoint('C',uv,2.4);pos,rt,up,fw=basis(FIT['cameras']['C']['params']);r=rpx*((pt-pos).dot(fw))/FIT['cameras']['C']['params'][5]
 main=sphere('吊灯_'+n,pt,r,glow if n in ['左白','右白','顶部簇','右上簇'] else chrome)
 if not (n in ['左白','右白','顶部簇','右上簇']):sphere('球内暖光_'+n,pt,r*.22,glow)
 cylinder('吊杆_'+n,(pt.x,pt.y,pt.z+r*.4),(pt.x,pt.y,H),.009,rodmat,8)
 cylinder('顶座_'+n,(pt.x,pt.y,H-.025),(pt.x,pt.y,H),.065,rodmat,16)
 if cluster and n not in ['左白','右白']:
  for j,(dx,dz,sz) in enumerate([(-1.15,-.38,.65),(.88,.54,.58),(.94,-.64,.61)]):
   p=pt+Vector((dx*r,-.04,dz*r));sphere('簇球_'+n+str(j),p,r*sz,glow if n not in ['顶部簇','右上簇'] else chrome)
# Four-point curved gold sparkle suspended forward, closed thin extrusion.
sp=[(.72*math.cos(i*2*math.pi/64)**3,1.06*math.sin(i*2*math.pi/64)**3) for i in range(64)]
# Four equal astroid arms, adjusted vertical scale; horizontal front plane.
verts=[]
for y in [2.02,2.055]:
 verts.extend([(x,y,2.25+z) for x,z in sp])
n=len(sp);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh('中央金色四芒星_实体',verts,faces,glow)
cylinder('四芒星隐藏吊杆',(0,2.04,3.29),(0,2.04,H),.011,rodmat)
# Right-side table, cup, floor sphere. Known visible props; unseen backs simplified.
pt=raypoint('B',(1026,550),.35);campos,_,_,_=basis(FIT['cameras']['B']['params']);ray=pt-campos;pt=campos+ray*((.018-campos.z)/ray.z);tx,ty=pt.x,pt.y
topray=raypoint('B',(1026,420),.35)-campos;t=((pt.x-campos.x)*topray.x+(pt.y-campos.y)*topray.y)/(topray.x**2+topray.y**2);table_height=(campos+t*topray).z;table_zscale=table_height/1.03
cube('右侧桌面',(tx,ty,1.03),(.87,.52,.07),dark,.018)
for dx in [-.39,.39]:
 for dy in [-.22,.22]:cylinder('桌腿',(tx+dx,ty+dy,.01),(tx+dx,ty+dy,1),.019,rodmat,12)
cube('桌下层板',(tx,ty,.24),(.83,.48,.035),dark,.008)
bpy.ops.mesh.primitive_torus_add(major_radius=.074,minor_radius=.015,major_segments=24,minor_segments=8,location=(tx-.19,ty-.04,1.115));finish(bpy.context.object,'杯口_真实孔洞',cupmat)
# cup hollow wall annular mesh
v=[];seg=24
for z,r in [(1.07,.08),(1.19,.08),(1.19,.058),(1.086,.058)]:
 v.extend([(tx-.19+r*math.cos(i*2*math.pi/seg),ty-.04+r*math.sin(i*2*math.pi/seg),z) for i in range(seg)])
f=[]
for layer in range(3):
 for i in range(seg):j=(i+1)%seg;f.append((layer*seg+i,layer*seg+j,(layer+1)*seg+j,(layer+1)*seg+i))
f.extend([tuple(reversed(range(seg))),tuple(range(3*seg,4*seg))]);mesh('空心杯壁与杯底',v,f,cupmat)

# Cup rests on the table, and the table is aligned parallel to its wall.
for ob in allgeom:
 if ob.name.startswith(('右侧桌面','桌腿','桌下层板','杯口','空心杯')):
  pivot=Vector((tx,ty,0));ob.matrix_world=Matrix.Translation(pivot)@Matrix.Rotation(math.atan2(-K,1),4,'Z')@Matrix.Translation(-pivot)@ob.matrix_world
 if ob.name.startswith(('杯口','空心杯')):ob.matrix_world=Matrix.Translation(Vector((0,0,-.008)))@ob.matrix_world
for ob in allgeom:
 if ob.name.startswith(('右侧桌面','桌腿','桌下层板','杯口','空心杯')):ob.matrix_world=Matrix.Diagonal((1,1,table_zscale,1))@ob.matrix_world
sphere('地面金属球',(PROP['ball']['xyz'][0],PROP['ball']['xyz'][1],.405),.25,gold)
# source-derived art textures, cropped without rectification; source comparison frames unchanged.
def image_mat(name,file):
 m=mat(name,(.4,.4,.4),.1,.38,.22);nt=m.node_tree;im=bpy.data.images.load(str(file));im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Emission Color']);return m

def panel(name,center,width,height,m,side,rounded=False):
 # Wall-following billboard: closed thickness, front UV artwork, back uses same bound texture.
 tangent=Vector((1,-K*side,0)).normalized();normal=Vector((-K*side,-1,0)).normalized();c=Vector(center)
 poly=[]
 if rounded:
  rr=width/2
  for q,zc in [(0,height/2-rr),(1,-height/2+rr)]:
   for j in range(13):
    a=(0 if q==0 else math.pi)+j*math.pi/12
    poly.append((rr*math.cos(a),zc+rr*math.sin(a)))
 else:poly=[(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]
 vv=[]
 for dep in [0,-.045]:vv.extend([tuple(c+x*tangent+z*Vector((0,0,1))+dep*normal) for x,z in poly])
 n=len(poly);ff=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];o=mesh(name,vv,ff,m);uv=o.data.uv_layers.new(name='UVMap')
 for p in o.data.polygons:
  for li in p.loop_indices:
   idx=o.data.loops[li].vertex_index%n;x,z=poly[idx];uv.data[li].uv=(x/width+.5,z/height+.5)
 # Two real brackets from board back to wall core.
 for dz in [-height*.3,height*.3]:
  start=c-normal*.04+Vector((0,0,dz));end=Vector((start.x,4-K*abs(start.x)+.31,start.z));cylinder(name+'_背撑',start,end,.022,struct,12)
 return o
rightcenter=raypoint('B',(954,146),.33)
panel('右壁海报实体背板',rightcenter,1.50,2.1,image_mat('右壁源图纹理',P/'textures/right_poster.png'),1)
for i in range(5):
 center=raypoint('A',[(45,138),(108,184),(168,145),(227,190),(282,149)][i],.33)
 panel('左侧胶囊画板%d'%i,center,.32,1.35,image_mat('胶囊源纹理%d'%i,P/f'textures/left_{i}.png'),-1,True)
# Neon lattice with actual open diamonds (tubes), rather than painted solid backdrop.
c=Vector(PROP['neon_center']);tangent=Vector((1,-K,0)).normalized();vertical=Vector((0,0,1));normal=Vector((-K,-1,0)).normalized()
for i in range(-3,4):
 for j in range(-3,4):
  if abs(i)+abs(j) not in [2,3]:continue
  cen=c+tangent*(i*.104)+vertical*(j*.104)
  pts=[cen+tangent*.06825,cen+vertical*.06825,cen-tangent*.06825,cen-vertical*.06825]
  for a in range(4):cylinder('霓虹格孔_%d_%d_%d'%(i,j,a),pts[a],pts[(a+1)%4],.009,neon,8)
# thin 3D orbital rings, open centers; support rod below joins floor.
for rot in [-.48,.55]:
 pts=[]
 for i in range(65):
  a=i*math.pi/32;pts.append(c+tangent*(.6175*math.cos(a))+vertical*(.286*math.sin(a))+normal*(.2275*math.sin(a)*math.sin(rot)))
 for i in range(64):cylinder('轨道环',pts[i],pts[i+1],.012,chrome,8)
 cylinder('轨道环背部连接',c+vertical*.143,pts[48],.012,rodmat,8)
cylinder('霓虹装置支杆',(c.x,c.y,.02),(c.x,c.y,c.z+.16),.018,rodmat,12)
# pair of neon arrows, real bent tubes fixed to wall
for idx,(x,z) in enumerate([(3.40,1.62),(3.95,2.05)]):
 bas=raypoint('B',[(783,386),(863,334)][idx],.30);ta=Vector((1,-K,0)).normalized();up=Vector((0,0,1));tip=bas+ta*.22+up*.24
 cylinder('箭头隐藏背撑',bas,(bas.x,4-K*abs(bas.x)+.31,bas.z),.018,struct,12)
 for a,b in [(bas-ta*.15-up*.15,tip),(tip,tip-ta*.31),(tip,tip-up*.31)]:cylinder('箭头%d'%idx,a,b,.028,whitepink,12)
for ob in list(allgeom):
 if ob.name.startswith('星形饰面'):
  mod=ob.modifiers.new('可见星墙边缘倒角','BEVEL');mod.width=.026;mod.segments=2;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
# UV every non-image mesh using automatic cube projection. Normals made outward consistently.
import bmesh
for o in allgeom:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
 if not o.data.uv_layers:
  uv=o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   n=p.normal;axis=max(range(3),key=lambda j:abs(n[j]));axes=[j for j in range(3)if j!=axis]
   for li in p.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 o['geometry_class']='shared_all_cameras'
# cameras use same fitted geometric interpretation; Blender local +Y is image up.
def camera_fit(name,c):
 pos,rt,up,fw=basis(c);roll=c[6];r2=rt*math.cos(roll)+up*math.sin(roll);u2=-rt*math.sin(roll)+up*math.cos(roll)
 data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=Matrix((r2,u2,-fw)).transposed().to_euler();data.type='PERSP';data.lens=c[5]*36/1180;data.sensor_width=36;data.clip_end=200;return o
for key,data in FIT['cameras'].items():camera_fit('源机位_'+key,data['params'])
def cam(name,pos,target,lens=30):
 da=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,da);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();da.lens=lens;return o
views=[('普通01_前方全台',(0,-15,3.6),(0,0,2.4),27),('普通02_左前',(-8,-12,4.5),(0,0,2.6),28),('普通03_右前',(8,-12,4.5),(0,0,2.6),28),('普通04_左外侧',(-12,-2,4),(0,0,2.8),27),('普通05_右外侧',(12,-2,4),(0,0,2.8),27),('普通06_背面',(0,12,4),(0,0,2.6),25),('普通07_顶面',(0,-1,15),(0,-1,1),26),('普通08_底面',(0,-1,-13),(0,-1,1),26),('普通09_内部广角',(0,-6.80,2.8),(0,2,2.6),20)]
for name,pos,target,lens in views:cam(name,pos,target,lens)
# Area lights fixed outside the open front, small enough to clear all structure.
for name,loc,power,size,color in [('正前柔光',(0,-7.5,4),700,2,(.7,.66,1)),('左前暖光',(-4,-7.8,3.5),450,1.5,(1,.55,.3)),('右前紫光',(4,-7.8,3.5),450,1.5,(.7,.22,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,1,2.4))-o.location).to_track_quat('-Z','Y').to_euler();o['fixed_all_cameras']=True
sc.world.color=(.08,.08,.08);sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.085,.14,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.3
sc.render.engine='CYCLES';sc.cycles.samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_x=1180;sc.render.resolution_y=663;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.camera=bpy.data.objects['源机位_C'];sc.render.film_transparent=False
# Boundaries and assumptions in the delivered file.
text=bpy.data.texts.new('中文_场景说明');text.write('星光颁奖舞台候选，2026-10-10重新建档。旧模型未恢复，不追认任何旧发布。采用同一几何材质与固定灯光验证左、右、正面三个真实源机位。比例单位非测绘米。源视频可见顶板、折角背墙、吊杆及圆台；建成有厚度的有顶有限舞台并保留摄像方向开敞，不无证据补观众厅。隐蔽底板厚度、背面、前角支撑与小坡为推定，非来源证实。人物、表演动作和片头片尾不重建。源艺术海报仅截图局部纹理，尚含透视烘焙误差。稀疏星形轮廓拟合不是全场还原通过。查看源图/材质/白模/直接50%叠图和残差说明。')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Star_Awards_Candidate.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'Star_Awards_Candidate.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=False)
print('BUILT',len(allgeom),'meshes')
# Optional specified render list
mode=os.environ.get('STAGE_RENDER','none')
if mode!='none':
 names=['源机位_A','源机位_B','源机位_C'] if mode=='source' else [v[0]for v in views]
 for n in names:
  sc.camera=bpy.data.objects[n];sc.render.filepath=str(P/'renders'/f'{n}_材质.png');bpy.ops.render.render(write_still=True)
