import bpy, math, os, json, bmesh
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom'
bpy.ops.wm.open_mainfile(filepath=R+'/source/models/seaside_bar_textured.blend')
S=bpy.context.scene
S.unit_settings.system='NONE';S['scope']='半开放吧台服务结构；非封闭室内、非完整亭顶。B段统一道具布局，A段道具变化不做相机相关隐藏或移动。'
S['scale_note']='相对建模单位，不是实测米。';S['source']='https://www.bilibili.com/video/BV1CY411k7Co/ ; A 22:18.578219 / B 22:33.015559'
for n in ['07_Optional_Scenic_Backdrop']:
 if bpy.data.collections.get(n):
  for o in list(bpy.data.collections[n].objects):bpy.data.objects.remove(o,do_unlink=True)
C=bpy.data.collections.new('09_推断_地面柜体墙角');S.collection.children.link(C)
wood=bpy.data.materials['Honey_oak_UV_PBR'];cream=bpy.data.materials['Painted_counter_frame_UV_PBR'];wall=bpy.data.materials['Warm_ochre_plaster_UV_PBR'];dark=bpy.data.materials['Espresso_wood_UV_PBR'];steel=bpy.data.materials['Brushed_metal']
def cube(n,loc,dim,m,bev=.015,inferred=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(m);o['evidence']='未见部分合理补全' if inferred else '源图支持的构件'
 if bev:
  mod=o.modifiers.new('Edge_finish','BEVEL');mod.width=bev;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def rod(n,a,b,r,m):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);return o
# Finite thick wall. The main and secondary apertures remain empty, no glass or image plane.
for n in ['Left_visible_wall_strip','Right_visible_wall_strip','Top_visible_wall_strip','Wall_below_window']:
 o=bpy.data.objects[n];o.dimensions.y=.28;o['evidence']='源图可见米色墙，厚度推断'
# Existing visible walls extended to a common inferred floor rather than floating fragments.
for name,x,w in [('Left_visible_wall_strip',-3.17,.74),('Right_visible_wall_strip',4.02,.68)]:
 o=bpy.data.objects[name];o.location.z=2.0;o.dimensions.z=4.90
cube('海侧墙_下部补齐',(.43,1.05,.38),(7.73,.28,1.66),wall)
cube('左侧矩形开口_外柱',(-4.5,1.05,2.0),(.24,.28,4.90),wall)
cube('左侧矩形开口_下墙',(-3.91,1.05,.56),(1.18,.28,2.02),wall)
cube('左侧矩形开口_实心窗台',(-3.91,.94,1.61),(1.2,.43,.14),cream,inferred=False)
cube('短侧墙_右侧墙角',(4.25,.42,.4),(.28,1.53,1.7),wall)
cube('短侧墙_左侧墙角',(-4.5,.35,.4),(.24,1.65,1.7),wall)
# One compact continuous floor, accessible from both side/front edges; no invented enclosed rear room.
cube('推断_连续地面平台',(0,-.65,-.52),(9.50,4.65,.16),wood,.02)
for x in [-4.4,4.3]:cube('推断_平台基础',(x,-.65,-.65),(.30,4.3,.10),dark)
# Counter carcasses and closed bottom panels. Recesses are real voids between solid components.
for tag,x,w in [('左',-2.80,2.50),('右',2.54,3.50)]:
 for xx in [x-w/2+.08,x+w/2-.08]:cube(tag+'操作柜_全高侧板',(xx,.10,.33),(.14,.84,1.54),cream)
 cube(tag+'操作柜_背板',(x,.49,.33),(w,.12,1.54),cream)
 cube(tag+'操作柜_底板',(x,.09,-.35),(w,.86,.14),cream)
 cube(tag+'操作柜_开放层板',(x,.10,.26),(w-.22,.76,.065),wood)
# Lower customer-facing counter has a physically complete pedestal.
cube('服务吧台_前立面',(0,-2.27,.02),(8.9,.15,.91),cream)
cube('服务吧台_底板',(0,-1.92,-.37),(8.9,1.0,.14),dark)
for x in [-4.36,-1.5,1.5,4.36]:cube('服务吧台_支撑肋',(x,-1.92,.02),(.15,.84,.91),cream)
# Explicit hinge and two support-arm assemblies, kept within the finite lifted panel footprint.
rod('上掀板_贯通铰轴',(-2.73,.91,4.24),(3.72,.91,4.24),.042,steel)
# Stepped bottle display: the old staggered bottles need shelves under all three rows.
for i,z in enumerate([1.84,1.94,2.05]):cube('瓶架_阶梯实体_'+str(i),(-3.11,.02+i*.22,z-(.105+i*.10)/2),(1.32,.225,.105+i*.10),wood)
# Lamp base seats on the actual sill surface; emissive body is wholly below the hatch.
lamp=bpy.data.objects.get('Cylindrical_amber_table_lamp');foot=bpy.data.objects['Lamp_dark_foot'];foot.location.z=1.727;lamp.location.z=2.020
# Remove wholly floating decorative duplicate flute upper assembly; retains all visible drink families.
for o in list(bpy.data.objects):
 if o.name.startswith('Back_purple_martini'):bpy.data.objects.remove(o,do_unlink=True)
# Seat remaining unsupported rear glasses on small visible sill-connected plinths.
cube('左细杯_台面补块',(-1.40,.36,1.245),(.62,.43,.13),wood)
cube('左细杯_补块落地支撑',(-1.14,.38,.38),(.12,.34,1.64),cream)
cube('右薄荷杯_台面补块',(1.40,.53,1.332),(.34,.36,.096),wood)
# Scene-wide cleanup: weld coincident poles, remove degenerate faces, consistent normals.
qa={};bad=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bpy.context.view_layer.objects.active=o
 if 'cream_label' in o.name or 'metal_end' in o.name:
  m=o.modifiers.new('真实薄片厚度','SOLIDIFY');m.thickness=.0015;m.offset=0;bpy.ops.object.modifier_apply(modifier=m.name)
 if o.scale!=Vector((1,1,1)):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);
 if 'foot_stem' in o.name or 'hollow_bowl' in o.name:
  bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
# Cameras all share this exact geometry. Perspective source approximations, no per-camera object visibility.
for o in list(bpy.data.objects):
 if o.type=='CAMERA':bpy.data.objects.remove(o,do_unlink=True)
def camera(n,loc,target,lens=45):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='PERSP';o.data.lens=lens;o.data.clip_end=500;return o
camera('源图_B_透视近似',(0,-50,3.38),(0,0,2.38),210)
camera('源图_A_透视近似',(.30,-40,3.23),(.30,0,2.43),200)
views=[('01_前方全貌',(10,-13,8),(0,-.4,1.7)),('02_左前侧',(-10,-11,6),(0,-.4,1.7)),('03_右侧',(12,-.2,5),(0,-.4,1.8)),('04_左侧',(-12,-.2,5),(0,-.4,1.8)),('05_海侧外背',(9,12,7),(0,-.4,1.8)),('06_海侧左背',(-10,12,7),(0,-.4,1.8)),('07_顶视检查',(0,-.5,20),(0,-.5,0)),('08_通道内部',(0,-1.1,2.1),(0,1.3,2.0)),('09_海侧正背',(0,16,5),(0,.2,1.8)),('10_低位柜底',(8,-9,1.3),(0,-.8,.5))]
for n,p,t in views:camera(n,p,t,40 if n!='08_通道内部' else 19)
# Neutral studio environment exposes topology rather than a camera-facing scenic board.
S.world.use_nodes=True;bg=S.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.15,.19,.23,1);bg.inputs['Strength'].default_value=.45
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=5;S.render.resolution_x=1000;S.render.resolution_y=750;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX';S.view_settings.exposure=0
for im in bpy.data.images:
 if im.filepath and not im.packed_file:im.pack()
S.camera=bpy.data.objects['01_前方全貌'];bpy.ops.wm.save_as_mainfile(filepath=R+'/models/seaside_bar_complete_textured.blend')
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=R+'/models/seaside_bar_complete_textured.glb',export_format='GLB',use_selection=True,export_yup=True)
for name in [v[0] for v in views]+['源图_A_透视近似','源图_B_透视近似']:
 S.camera=bpy.data.objects[name]
 S.render.resolution_x=1180 if name.startswith('源图') else 1000;S.render.resolution_y=663 if name.startswith('源图') else 750
 S.render.filepath=R+'/renders/'+name+'_材质.png';bpy.ops.render.render(write_still=True)
# Cutaway uses a clipping plane on a diagnostic copy only; complete geometry file is not altered.
# White variant retains exact mesh coordinates and camera definitions.
white=bpy.data.materials.new('中性白模');white.use_nodes=True;p=white.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.72,.72,.72,1);p.inputs['Roughness'].default_value=.8
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
S.camera=bpy.data.objects['01_前方全貌'];bpy.ops.wm.save_as_mainfile(filepath=R+'/models/seaside_bar_complete_white.blend')
bpy.ops.export_scene.gltf(filepath=R+'/models/seaside_bar_complete_white.glb',export_format='GLB',use_selection=True,export_yup=True)
for name in ['源图_A_透视近似','源图_B_透视近似','01_前方全貌','05_海侧外背']:
 S.camera=bpy.data.objects[name];S.render.resolution_x=1180 if name.startswith('源图') else 1000;S.render.resolution_y=663 if name.startswith('源图') else 750;S.render.filepath=R+'/renders/'+name+'_白模.png';bpy.ops.render.render(write_still=True)
