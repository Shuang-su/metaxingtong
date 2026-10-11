import bpy, math, os, json, bmesh, sys
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1'
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
S.render.engine='CYCLES';S.cycles.samples=20;S.cycles.use_denoising=False
S.render.resolution_x=1180;S.render.resolution_y=664;S.render.resolution_percentage=100
S.world=bpy.data.worlds.new('柔和环境');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.065,.065,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.5
S.view_settings.view_transform='AgX'
def mat(n,c,metal=0,rough=.4,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 return m
red=mat('红色亮片漆_程序近似',(.38,.012,.028),.25,.4);gold=mat('暖金边框',(.30,.12,.03),.5,.4);black=mat('深黑紫绒帘',(.024,.018,.027),0,.86);floor=mat('深棕反光地面',(.065,.027,.022),.42,.18);steel=mat('推定后台钢架',(.07,.075,.08),.6,.4);bulb=mat('暖白灯泡', (1,.62,.25),0,.24,5);white=mat('白模中性',(.65,.65,.65),0,.7)
# Portable small packed procedural image swatches instead of nonportable shader noise.
import random
random.seed(42)
im=bpy.data.images.new('红漆微闪_512',width=256,height=256);px=[]
for i in range(256*256):
 f=random.uniform(.55,1.3); f=2 if random.random()<.06 else f;px.extend((min(.38*f,1),.012*f,.028*f,1))
im.pixels=px;im.pack();nt=red.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
def finish(o,n,m,obs=True):
 o.name=n;o.data.materials.append(m);o['证据等级']='正面观测形体，尺寸估计' if obs else '未见部分：有限推定补全';return o
def box(n,loc,dim,m,obs=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,m,obs)
def mesh(n,vs,fs,m,obs=True):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);S.collection.objects.link(o);finish(o,n,m,obs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return o
def poly(n,pts,y,depth,m,obs=True):
 pts=[p for i,p in enumerate(pts) if i==0 or (Vector(p)-Vector(pts[i-1])).length>1e-7]
 if (Vector(pts[-1])-Vector(pts[0])).length<1e-7:pts.pop()
 N=len(pts);vs=[(x,yy,z) for yy in (y,y+depth) for x,z in pts];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(n,vs,fs,m,obs)
def beam(n,a,b,w,d,m,obs=True):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(w,d,(b-a).length),m,obs);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def uvall():
 for o in list(S.objects):
  if o.type=='MESH':
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
   if o.data.materials[0]==red:
    for uv in o.data.uv_layers.active.data:uv.uv*=12
# All stage geometry is fixed; no view-dependent hiding.
box('前地面_有限边界',(0,-1.5,-.10),(16,12,.2),floor,False)
# Three actual risers, gold nosings are highlights/trim, not additional stairs.
for i,(front,top) in enumerate([(-1.65,.18),(-1.22,.38),(-.8,.6)]):
 back=2.8;box('台阶实体_%02d'%(i+1),(0,(front+back)/2,top/2),(13,back-front,top),red)
 box('台阶金色鼻口_%02d'%(i+1),(0,front-.013,top-.016),(13,.035,.035),gold)
# Arch ring spans x±5.15; front observed; back thickness inferred.
N=112;ang=[math.pi*i/N for i in range(N+1)]
pts=[(5.15*math.cos(t),.6+5.15*math.sin(t)) for t in ang]+[(4.65*math.cos(t),.6+4.65*math.sin(t)) for t in reversed(ang)]
poly('红色拱台实体_深度推定',pts,.30,.40,red)
for r1,r2,name in [(5.15,5.20,'拱台外金线'),(4.60,4.65,'拱台内金线')]:
 p=[(r2*math.cos(t),.6+r2*math.sin(t)) for t in ang]+[(r1*math.cos(t),.6+r1*math.sin(t)) for t in reversed(ang)];poly(name,p,.278,.025,gold)
# Solid side spandrels to finite rectangle, no invented banquet hall.
for sign in [-1,1]:
 p=[(sign*6.5,.6),(sign*6.5,6.35),(0,6.35),(0,5.8)]+[(sign*5.2*math.cos(t),.6+5.2*math.sin(t)) for t in reversed([math.pi/2*i/56 for i in range(57)])]
 poly(('左' if sign<0 else '右')+'金棕侧景板',p,.35,.28,gold)
# Curtain closed solid corrugated mesh, hidden top edges remain physical.
xs=[-4.63+9.26*i/320 for i in range(321)];ys=[.93+.09*math.cos(i/320*math.pi*92) for i in range(321)];vs=[]
for yy in [0,.035]:
 for z in [.6,5.5]:vs.extend((x,y+yy,z) for x,y in zip(xs,ys))
k=len(xs);fs=[]
for i in range(k-1):fs += [(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)]
fs += [(0,k,3*k,2*k),(k-1,3*k-1,4*k-1,2*k-1)]
mesh('褶皱黑帘_闭合薄实体',vs,fs,black)
box('帘顶部悬挂横梁',(0,1.02,5.51),(9.55,.20,.18),steel,False)
for x in [-4.75,4.75]:box('悬挂支柱_'+str(x),(x,1.02,3.08),(.18,.20,4.96),steel,False)
# Two layers of angular illuminated wings.
lamps=[]
def lightchain(prefix,points,y):
 for j in range(len(points)-1):
  a,b=Vector(points[j]),Vector(points[j+1]);count=max(2,round((b-a).length/.30))
  beam(prefix+'金边_%d'%j,(a.x,y+.13,a.y),(b.x,y+.13,b.y),.32,.25,gold)
  for k2 in range(count):
   q=a+(b-a)*k2/count
   bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.088,location=(q.x,y-.04,q.y));o=bpy.context.object;o.scale=(1,.70,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,prefix+'灯泡_%d_%d'%(j,k2),bulb);lamps.append(o.name)
for s in [-1,1]:
 name='左' if s<0 else '右'
 p=[(s*1.83,.60),(s*6.45,.60),(s*6.45,3.15),(s*1.83,1.57)]
 poly(name+'内折线翼板',p,-.22,.38,red)
 lightchain(name+'内灯排',[(s*6.38,3.05),(s*1.98,1.52),(s*1.98,.80),(s*6.4,.80)],-.37)
 p=[(s*3.13,.38),(s*6.48,.38),(s*6.48,2.44),(s*3.13,1.39)]
 poly(name+'外折线翼板',p,-1.01,.40,red)
 lightchain(name+'外灯排',[(s*6.4,2.32),(s*3.26,1.31),(s*3.26,.56),(s*6.4,.56)],-1.16)
# Stars are only partially observed, full contour completion flagged.
for s in [-1,1]:
 p=[]
 for j in range(10):
  t=math.pi/2+j*math.pi/5;r=.75 if j%2==0 else .34;p.append((s*4.3+r*math.cos(t),4.97+r*math.sin(t)))
 poly(('左' if s<0 else '右')+'星饰_未见尖角推定',p,.0,.25,gold,False)
 box(('左' if s<0 else '右')+'星饰背安装座',(s*4.3,.31,4.97),(.40,.22,.40),steel,False)
 # bulbs inset, no emissive sheets crossing frame
 for j in range(10):
  a,b=Vector(p[j]),Vector(p[(j+1)%10]);a=Vector((s*4.3,4.97))+(a-Vector((s*4.3,4.97)))*.8;b=Vector((s*4.3,4.97))+(b-Vector((s*4.3,4.97)))*.8
  for kk in range(4):
   q=a+(b-a)*kk/4;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=.043,location=(q.x,-.025,q.y));finish(bpy.context.object,'星饰灯泡',bulb)
# Denser inner star lamps observed in source; exact count remains approximate.
for s in [-1,1]:
 for rr,nn in [(.0,1),(.15,8),(.29,12)]:
  for j in range(nn):
   t=2*math.pi*j/nn;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=.035,location=(s*4.3+rr*math.cos(t),-.024,4.97+rr*math.sin(t)));finish(bpy.context.object,'星饰内部灯泡_数量近似',bulb)
# Backside practical supports explicitly inferred, seated on platform.
for x in [-5.6,5.6]:
 box('后台支柱',(x,1.3,3.40),(.22,.22,5.6),steel,False)
 box('后台支脚',(x,1.70,.68),(.70,1.9,.16),steel,False)
 beam('后台斜撑',(x,2.50,.72),(x,1.3,4.9),.16,.16,steel,False)
 box('景板背部连接块',(x,.98,4.9),(.34,.78,.22),steel,False)
box('景板后横梁',(0,1.30,6.15),(11.45,.22,.22),steel,False)
uvall()
# Render lighting, separate from exported geometry.
def area(n,loc,power,size,col,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('柔光正面',(0,-7,7),1000,8,(1,.72,.55),(0,0,2));area('左侧柔光',(-7,-3,4),500,5,(1,.4,.25),(0,0,2));area('背部检查光',(0,6,7),1800,7,(.7,.8,1),(0,1,2))
d=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',d);S.collection.objects.link(cam);S.camera=cam
views={'源图匹配':((.12,-12.5,2.25),(.12,0,1.60),43),'正面全景':((0,-17,6),(0,.2,2.65),38),'左前':((-12,-13,7),(0,.4,2.1),42),'右前':((12,-13,7),(0,.4,2.1),42),'左侧':((-15,1,6),(0,.5,2.4),43),'右侧':((15,1,6),(0,.5,2.4),43),'背面':((0,19,8),(0,.5,2.5),36),'左后':((-12,11,8),(0,.5,2.4),42),'右后':((12,11,8),(0,.5,2.4),42),'俯视':((0,-1,19),(0,.5,0),43),'底面':((0,-8,-10),(0,.5,1),38)}
def camera(v):
 loc,target,lens=views[v];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
camera('源图匹配')
# Exports only fixed mesh, no light dependency.
def save(typ):
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/red_gold_stage_'+typ+'.blend');bpy.ops.object.select_all(action='DESELECT')
 for o in S.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/red_gold_stage_'+typ+'.glb',export_format='GLB',use_selection=True,export_extras=True)
save('textured')
for v in ([] if '--geometry-only' in sys.argv else views):
 camera(v);S.render.filepath=R+'/renders/'+v+'_材质.png';bpy.ops.render.render(write_still=True)
for o in S.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
camera('源图匹配');save('white')
for v in ([] if '--geometry-only' in sys.argv else ['源图匹配','左前','背面','底面']):
 camera(v);S.render.filepath=R+'/renders/'+v+'_白模.png';bpy.ops.render.render(write_still=True)
json.dump({'views':views,'lamps':lamps,'source_fit':'单正面机位近似，不是独立多视标定','step_count':3,'real_scale':'未知；全场尺寸为比例假设','history':'首个可核实建模版本，无已确认旧模型'},open(R+'/qa/build_facts.json','w'),ensure_ascii=False,indent=2)
