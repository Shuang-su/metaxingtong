import bpy,math,json,random,os
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1'
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
S.render.engine='CYCLES';S.cycles.samples=64;S.cycles.use_denoising=False
S.render.resolution_x=1180;S.render.resolution_y=664;S.render.resolution_percentage=100
S.world=bpy.data.worlds.new('World');S.world.color=(.11,.13,.17);S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast'
# Small deterministic procedural raster, authored for portability rather than extracted from a source frame.
random.seed(21);im=bpy.data.images.new('自制灰混凝土微纹理',width=128,height=128);px=[]
for y in range(128):
 for x in range(128):
  q=.68+random.random()*.11+.018*math.sin(x*.28)*math.sin(y*.14);px.extend([q,q,q,1])
im.pixels=px;im.filepath_raw=R+'/textures/concrete_micro.png';im.file_format='PNG';im.save();im.pack()
def mat(name,c,metal=0,rough=.5,tex=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if tex:
  colored=bpy.data.images.new(name+'_烘入颜色',width=128,height=128);values=[]
  def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
  def srgb(v):return 12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
  for i in range(0,len(px),4):values.extend([srgb(lin(px[i])*c[0]),srgb(lin(px[i+1])*c[1]),srgb(lin(px[i+2])*c[2]),1])
  colored.pixels=values;colored.filepath_raw=R+'/textures/'+('wall_color.png' if '墙' in name else 'floor_color.png');colored.file_format='PNG';colored.save();colored.pack()
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=colored;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])

 return m
wall=mat('暗蓝灰墙_推定微纹理',(.075,.10,.145),0,.8,True);floor=mat('冷灰微反射地面',(.10,.14,.19),.12,.26,True);iron=mat('黑色铁栏',(.009,.013,.018),.25,.63);hardware=mat('枪灰收边及支撑',(.046,.06,.08),.7,.35);white=mat('统一白模',(.68,.68,.68),0,.65);glass=mat('灯罩',(.7,.82,1),0,.35)
def box(n,loc,scale,m=wall,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bev:
  mod=o.modifiers.new('实体小倒角','BEVEL');mod.width=bev;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o['evidence']='推定补全' if n.startswith('推定') else '可见类型，尺寸推定';return o
def cyl(n,loc,r,depth,m=iron):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(m);return o
# Full finite shell, 0.22 units slab, 0.22 units walls, 0.20 units roof. Front entrance is a true absence of wall.
box('推定_厚地板',(0,-.40,-.11),(6.84,5.84,.22),floor)
box('推定_厚顶板',(0,-.40,4.40),(6.84,5.84,.20))
box('推定_后墙',(0,2.41,2.15),(6.84,.22,4.3))
box('推定_左墙',(-3.31,-.40,2.15),(.22,5.4,4.3))
box('推定_右墙',(3.31,-.40,2.15),(.22,5.4,4.3))
# Entrance x=1.85..2.95, z=0..2.5 at y=-3.21.
box('推定_前墙左',(-.675,-3.21,2.15),(5.05,.22,4.3))
box('推定_前墙右',(3.075,-3.21,2.15),(.25,.22,4.3))
box('推定_入口过梁',(2.4,-3.21,3.4),(1.10,.22,1.8))
for x in [1.85,2.95]:box('推定_入口竖向收边',(x,-3.21,1.25),(.055,.27,2.5),hardware)
box('推定_入口顶部收边',(2.4,-3.21,2.5),(1.15,.27,.055),hardware)
box('推定_栏上完整填板',(0,0,3.90),(6.4,.26,.80))
# Cage: full-height posts and real bars socketed into top and bottom rails.
box('栏杆左厚墙',(-2.69,0,1.75),(1.02,.26,3.5))
box('栏杆主支撑左',(-2.12,0,1.75),(.12,.16,3.5),iron)
box('栏杆主支撑右',(2.12,0,1.75),(.12,.16,3.5),iron)
box('推定_门右支撑',(3.14,0,1.75),(.12,.16,3.5),iron)
box('推定_全宽顶梁',(.51,0,3.39),(5.38,.20,.22),hardware)
box('栏杆底轨',(0,0,.065),(4.24,.13,.13),iron)
box('栏杆顶轨',(0,0,3.31),(4.24,.13,.13),iron)
for i in range(13):
 x=(i-6)*.32+.12;box('可见竖栏_%02d'%i,(x,0,1.69),(.037,.055,3.24),iron,.003)
# 0.9 units clear gate, open inward 80 degrees; placement outside the anchor's central observation.
pivot=bpy.data.objects.new('推定_可转动门铰链轴',None);S.collection.objects.link(pivot);pivot.location=(3.08,0,0);pivot.rotation_euler.z=math.radians(-80)
def gate(n,x,z,sz):
 o=box('推定_门_'+n,(0,0,0),sz,iron,.004);o.parent=pivot;o.location=(x,0,z);return o
for x in [-.91,0]:gate('竖框',x,1.32,(.055,.065,2.64))
for z in [.07,2.59]:gate('横框',-.455,z,(.965,.065,.07))
for i in range(1,5):gate('竖栏_%d'%i,-i*.182,1.33,(.029,.045,2.50))
for z in [.34,1.32,2.30]:
 cyl('推定_门铰链',(3.09,0,z),.052,.18,hardware)
 box('推定_铰链固定叶',(3.12,0,z),(.13,.09,.13),hardware)
box('推定_门上方填板',(2.63,0,3.07),(.90,.12,.86))
for n,loc,dim in [('把手座',(-.91,.048,1.2),(.095,.05,.30)),('把手支座下',(-.91,.095,1.10),(.045,.10,.04)),('把手支座上',(-.91,.095,1.30),(.045,.10,.04)),('把手握杆',(-.91,.14,1.2),(.035,.035,.23))]:
 o=box('推定_门_'+n,(0,0,0),dim,hardware,.004);o.parent=pivot;o.location=loc
# Base coving is shallow solid material, all seams installed against shell.
for x in [-3.185,3.185]:box('推定_侧踢脚',(x,-.40,.065),(.03,5.4,.13),hardware)
box('推定_后踢脚',(0,2.285,.065),(6.4,.03,.13),hardware)
# Complete closed lighting fixtures, area boundaries lie wholly within their diffuser footprints.
lightdata=[]
for j,y in enumerate([1.1,-1.7]):
 box('推定_封闭灯盒_%d'%j,(0,y,4.255),(1.06,1.36,.09),hardware)
 box('推定_实体灯罩_%d'%j,(0,y,4.196),(.96,1.26,.028),glass)
 l=bpy.data.lights.new('推定_面光_%d'%j,'AREA');l.shape='RECTANGLE';l.size=.88;l.size_y=1.18;l.energy=100 if j<1 else 10;l.color=(.57,.73,1)
 o=bpy.data.objects.new(l.name,l);S.collection.objects.link(o);o.location=(0,y,4.177)
 lightdata.append({'name':o.name,'boundary_x':[-.44,.44],'boundary_y':[y-.59,y+.59],'z':4.177,'diffuser_bottom_z':4.182,'inside_diffuser_footprint':True})
# Fixed cameras. No ordinary camera changes geometry or visibility.
views={
 '01_来源932正面':((0,-2.68,1.67),(0,3.4,1.67),23),
 '02_走廊左前':((-2.75,-2.5,1.7),(.4,1.3,1.5),20),
 '03_走廊右前':((2.75,-2.55,1.7),(-.4,1.3,1.45),20),
 '04_室内左后':((-2.8,1.95,1.7),(.8,-.2,1.5),20),
 '05_室内右后':((2.8,1.95,1.7),(-.7,-.2,1.5),20),
 '06_室内面向后墙':((0,.65,1.6),(0,2.3,1.6),20),
 '07_入口通道':((2.4,-4.5,1.6),(2.4,2,1.6),24),
 '08_门铰链近景':((1.8,1.35,1.4),(3.05,.05,1.45),37),
 '09_外部前右':((10,-12,8),(0,.7,1.5),40),
 '10_外部背面':((-9,12,6),(0,.7,1.5),40),
 '11_底面':((8,-10,-9),(0,.7,1.2),40),
 '12_剖切诊断':((9,-11,10),(0,.7,1.1),43),
 '13_3626关系未证实':((0,1.85,1.65),(0,-1,1.65),23)}
for n,(pos,targ,lens) in views.items():
 c=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,c);S.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(targ)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=lens;c.clip_start=.03;c.clip_end=200
S.camera=bpy.data.objects['01_来源932正面']
S['scope']='932秒前景栏杆为锚；完整房间厚壳、走廊、门和灯为有限推定；3626秒空间关系未证实。'
for o in bpy.data.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=R+'/models/dark_cell_textured.blend')
bpy.ops.export_scene.gltf(filepath=R+'/models/dark_cell_textured.glb',export_format='GLB',export_cameras=False,export_lights=False)
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=R+'/models/dark_cell_white.blend')
bpy.ops.export_scene.gltf(filepath=R+'/models/dark_cell_white.glb',export_format='GLB',export_cameras=False,export_lights=False)
json.dump({'views':list(views),'area_lights':lightdata,'gate_angle_degrees':80,'entrance_clear_width':1.045,'gate_nominal_opening_width':.90,'room_inner_bounds':[[-3.2,-3.1,0],[3.2,2.3,4.3]],'source':'https://www.bilibili.com/video/BV1F8QzY7EAY/','source_frame_seconds':932.522162},open(R+'/qa/build_facts.json','w'),ensure_ascii=False,indent=2)
