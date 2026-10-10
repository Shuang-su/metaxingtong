import bpy,math,json,bmesh,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent; D=R/'final7p7';D.mkdir(exist_ok=True)
for p in ['models','renders','analysis','references','textures','scripts']: (D/p).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'source/unpacked/models/01_bedroom_material.blend'));s=bpy.context.scene;s.unit_settings.system='NONE'
for n in ['Rear wall verified visible face','Left room return inferred','Right room return inferred','Floor substrate','Plain ceiling inferred unseen','Skirting bottom shadow']:
 bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
C=bpy.data.collections.new('90_推定完整围护_固定几何');s.collection.children.link(C)
wall=bpy.data.materials['Wall'];wood=bpy.data.materials['Oak'];white=bpy.data.materials['Cabinet']
def cube(n,p,d,m=wall):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(m);o['evidence']='推定完整空间；模型单位，不是实测米';return o
def boolean(target,operand,op):
 mod=target.modifiers.new(op,'BOOLEAN');mod.operation=op;mod.solver='EXACT';mod.object=operand;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(operand,do_unlink=True)
# Interior [-3.52,3.92] x [-7.7,.03], ceiling 3.3. Shared shell fused at corners.
shell=cube('完整四墙_厚0.18_真实门窗洞',(.2,.079,1.65),(7.8,.18,3.3))
for p,d in [((-3.61,-3.835,1.65),(.18,7.91,3.3)),((4.01,-3.835,1.65),(.18,7.91,3.3)),((.2,-7.79,1.65),(7.8,.18,3.3))]:boolean(shell,cube('fuse',p,d),'UNION')
# Inferred rear-facing entrance and side window. No claimed connectivity to any other room.
boolean(shell,cube('door_cut',(-2.35,-7.79,1.15),(1.1,.7,2.3)),'DIFFERENCE')
boolean(shell,cube('window_cut',(-3.61,-2.25,1.85),(.7,1.9,1.4)),'DIFFERENCE')
floor=cube('实体地板_厚0.16',(.2,-3.835,-.08),(7.8,8.09,.16),wood)
roof=cube('实体天花_厚0.16',(.2,-3.835,3.38),(7.8,8.09,.16))
# Existing parquet clipped to interior to avoid protruding wall tails.
for o in list(bpy.data.collections['03_Parquet_floor'].objects):
 if o.type=='MESH':
  # wholly remove planks that cross wall boundary; seamless underlying oak remains.
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  if any(v.x< -3.52 or v.x>3.92 or v.y< -7.7 or v.y>.03 for v in pts):bpy.data.objects.remove(o,do_unlink=True)

# Extend only inferred front floor using the same herringbone world lattice.
L=.55;W=.11
for i in range(-40,41):
 for j in range(-100,101):
  bx=i*L+j*W;by=i*L-j*W
  for typ in [0,1]:
   cx=bx+L*.5 if typ==0 else bx+W*.5;cy=by+W*.5 if typ==0 else by+1.5*L
   dx,dy=(L-.003,W-.003) if typ==0 else (W-.003,L-.003)
   if cx-dx/2>=-3.52 and cx+dx/2<=3.92 and cy-dy/2>=-7.7 and cy+dy/2<=-5.55:
    cube('推定延长人字木地板',(cx,cy,.002),(dx,dy,.012),wood)

# Continuous solid perimeter trim, interrupted by door. Rear trim brought into contact with rear wall.
o=bpy.data.objects['Rear skirting'];o.location.x=.2;o.dimensions.x=7.44;o.location.y=-.036;o.dimensions.y=.05
for x in [-3.495,3.895]:cube('侧墙踢脚线',(x,-3.835,.062),(.05,7.73,.124))
for a,b in [(-3.52,-2.93),(-1.77,3.92)]:cube('门墙踢脚线',((a+b)/2,-7.675,.062),(b-a,.05,.124))
# Real door reveals with architraves both sides; no door leaf blocks the inspection path.
for y in [-7.68,-7.9]:
 for x in [-2.935,-1.765]:cube('推定门洞双面立边',(x,y,1.15),(.07,.045,2.3),white)
 cube('推定门洞双面上边',(-2.35,y,2.335),(1.24,.045,.07),white)
cube('推定门洞门槛',(-2.35,-7.79,.008),(1.1,.23,.016),wood)
# window jambs continuous through wall depth, sill and header; real opening, solid thin glass.
for y in [-3.23,-1.27]:cube('推定窗洞立框',(-3.61,y,1.85),(.25,.06,1.52),white)
for z in [1.12,2.58]:cube('推定窗洞横框',(-3.61,-2.25,z),(.25,2.02,.06),white)
cube('推定窗中梃',(-3.61,-2.25,1.85),(.12,.05,1.4),white)
cube('推定窗台',(-3.55,-2.25,1.095),(.43,2.1,.07),white)
glass=bpy.data.materials.new('推定玻璃_真实薄实体');glass.use_nodes=True;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.77,.88,.94,1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['Roughness'].default_value=.08
cube('推定窗玻璃_厚0.012',(-3.61,-2.25,1.85),(.012,1.87,1.37),glass)
# Rear print wall mount blocks bridge the small physical standoff.
for x in [-.36,.48]:cube('画框背部挂块',(x,-.017,1.77),(.06,.014,.08),white)
# Actual support adjustments, entire functional groups; not view-dependent.
def bounds(objs):
 ps=[o.matrix_world@v.co for o in objs if o.type=='MESH' for v in o.data.vertices];return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
bpy.context.view_layer.update()
# Rug underside .01 vs parquet .008: lower by .002. Plinth buried slightly in rug previously; now planted on rug.
rug=bpy.data.objects['Large low pile bedside rug'];rug.location.z-=.002
pl=bpy.data.objects['Bed recessed dark plinth'];pl.location.z+=.018
# Cabinet skid .017 vs floor .008: lower cabinet and supported items together by .009.
for cn in ['06_Bedside_cabinet','07_Lamp_clock_frames']:
 for o in bpy.data.collections[cn].objects:
  if not o.name.startswith('Wall comic'):o.location.z-=.009
for o in bpy.data.collections['08_Plant_inferred_hidden'].objects:o.location.z-=.002
# Portrait/print surfaces need a true thickness, backing remains untouched.
for o in list(s.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 if 'UV print' in o.name:
  mod=o.modifiers.new('真实画纸薄厚','SOLIDIFY');mod.thickness=.001;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
# Remove all giant old lights. New horizontal disks completely inside the room.
for o in list(s.objects):
 if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
for i,(p,size,power) in enumerate([((-1.75,-3.5,3.05),1.6,190),((1.8,-2.3,3.04),1.7,150),((0,-.9,3.06),1.4,100)]):
 data=bpy.data.lights.new('受限室内柔光'+str(i),'AREA');data.shape='DISK';data.size=size;data.energy=power;data.color=(1,.88,.75);o=bpy.data.objects.new(data.name,data);s.collection.objects.link(o);o.location=p
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.65,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
# Camera-only refit inside finite envelope: no mesh visibility changes.
fit=json.loads((R/'delivery/analysis/bounded_depth_comparison.json').read_text())[2]
p=fit['parameters']
for name,mult in [('MATCH_front_50m07_same_axis',1),('MATCH_close_50m10_same_axis',1.971)]:
 o=bpy.data.objects[name];o.location=p[:3];o.rotation_euler=Vector((0,math.cos(p[3]),-math.sin(p[3]))).to_track_quat('-Z','Y').to_euler();o.data.lens=p[4]*mult;o.data.clip_start=.03;o['sparse_anchor_RMSE_px']=fit['rms_px'];o['evidence']='房间深度上限7.7的有界折中；七手工锚点约30px，不是全图或精确源片还原'
# Existing QA cameras relocated inward; independent normal walkable views.
def camera(n,p,t,l=25):
 data=bpy.data.cameras.new(n);data.lens=l;data.clip_start=.03;data.clip_end=150;o=bpy.data.objects.new(n,data);s.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();return o
views=[('01_入口看床',(-2.35,-7.25,1.55),(0,-1.25,1.15),25),('02_右前看床',(3.45,-4.9,1.55),(0,-1.2,1.15),25),('03_左侧沿墙',(-3.05,-3.25,1.5),(.3,-.85,1.2),25),('04_床尾正向',(0,-4.9,1.5),(0,-.4,1.3),27),('05_右侧床柜',(3.5,-2.4,1.55),(.6,-.65,.95),27),('06_反向门窗',(2.1,-1.2,1.55),(-1.7,-6.8,1.4),23),('07_反向入口',(-2.8,-.45,1.55),(.1,-6.8,1.4),23),('08_窗边横向',(-3.1,-1.6,1.6),(1.2,-2.7,1.1),24),('09_门洞近看',(-1.0,-6.75,1.6),(-2.5,-7.75,1.5),24),('10_窗洞近看',(-1.9,-2.1,1.7),(-3.6,-2.25,1.75),25),('11_墙角近看',(3,-1,2.6),(3.9,.01,3.15),22),('12_外壳完整',(-9,-12,8),(.2,-3.8,1.4),35)]
for v in views:camera(*v)
for n in ['QA_wide_level','QA_opposite_level']:
 if bpy.data.objects.get(n):bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
s.camera=bpy.data.objects['01_入口看床'];s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.view_settings.exposure=0
s['VERSION']='完整有限房间v1；模型单位非实测米；真实厚墙门窗；同轴源图不构成独立侧向验证；源片精确拟合未达标'
s['ROOM_ENVELOPE_INFERRED']='全体几何固定；没有按相机隐藏墙；推定门窗位置不证明其他场景相连'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  f=R/'source/unpacked/textures'/Path(im.filepath).name
  if f.exists():im.filepath=str(f);im.pack()
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/01_bedroom_material.blend'),compress=True)
print('BUILD_DONE',len(s.objects))
