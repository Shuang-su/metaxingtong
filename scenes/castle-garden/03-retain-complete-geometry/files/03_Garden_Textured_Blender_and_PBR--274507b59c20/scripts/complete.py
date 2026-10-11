import bpy,bmesh,json,math,os
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';D=R+'/delivery'
bpy.ops.wm.open_mainfile(filepath=R+'/source/restored/models/Xingtong_Castle_Garden_Textured.blend');s=bpy.context.scene
C=bpy.data.collections.new('08_推定_隐藏闭合与支撑');s.collection.children.link(C)
def cube(n,p,d,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(bpy.data.materials[mat]);o['evidence']='推定隐藏结构；模型单位，非实测';return o
changes=[]
for o in list(s.objects):
 if o.type!='MESH':continue
 plant=('planting' in o.name or o.name.startswith(('04_Near','05_Far')))
 o['surface_class']='天然双面薄叶/花瓣' if plant else '实体构件'
 bm=bmesh.new();bm.from_mesh(o.data)
 if not plant:
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000001)
  if o.name.startswith(('Pointed_double_door','Tall_cyan_leaded_window')):
   res=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces));vv=[v for v in res['geom'] if isinstance(v,bmesh.types.BMVert)];bmesh.ops.translate(bm,verts=vv,vec=o.matrix_world.inverted().to_3x3()@Vector((0,.20,0)))
   changes.append([o.name,'向后实体厚度0.20'])
  elif o.name.startswith('Classical_flower_urn'):
   # Close the base only; retain a recessed inner bowl rather than filling mouth with a flat disk.
   edges=[e for e in bm.edges if e.is_boundary];zmin=min(v.co.z for v in bm.verts);base=[e for e in edges if all(abs(v.co.z-zmin)<1e-5 for v in e.verts)]
   bmesh.ops.holes_fill(bm,edges=base,sides=0)
   top=sorted([v for v in bm.verts if abs(v.co.z-max(x.co.z for x in bm.verts))<1e-5],key=lambda v:math.atan2(v.co.y-sum(x.co.y for x in bm.verts)/len(bm.verts),v.co.x-sum(x.co.x for x in bm.verts)/len(bm.verts)))
   center=sum((v.co for v in top),Vector())/len(top);inner=[bm.verts.new(center+(v.co-center)*.87) for v in top];lower=[bm.verts.new(v.co+Vector((0,0,-.28))) for v in inner]
   for i in range(len(top)):
    j=(i+1)%len(top);bm.faces.new((top[i],top[j],inner[j],inner[i]));bm.faces.new((inner[i],inner[j],lower[j],lower[i]))
   bm.faces.new(tuple(reversed(lower)));changes.append([o.name,'盆底封闭、内壁与凹入盆底'])
  else:
   edges=[e for e in bm.edges if e.is_boundary]
   if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0);changes.append([o.name,'端口封闭'])
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 for m in o.data.materials:
  if m:m.use_backface_culling=False
# Contact repairs: preserve front silhouette, extend only toward supporting solids.
for o in list(s.objects):
 if o.type!='MESH':continue
 backtarget=None
 if o.name.startswith(('Gothic_door_frame','Window_pointed_stone_border','Pilaster_edge_flute','Window_sill')):backtarget=.55
 elif o.name.startswith(('Door_central_seam','Door_raised_diamond','Door_raised_panel_border')):backtarget=.445
 elif o.name.startswith('Window_dark_mullion'):backtarget=.425
 if backtarget is not None:
  pts=[o.matrix_world@v.co for v in o.data.vertices];front=min(p.y for p in pts);back=max(p.y for p in pts);inv=o.matrix_world.inverted()
  for v,p in zip(o.data.vertices,pts):
   p.y=front+(p.y-front)*(backtarget-front)/(back-front);v.co=inv@p
  changes.append([o.name,'正面不动，背部伸入承托体至y='+str(backtarget)])
 if o.name.startswith('Turned_stone_baluster'):
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z>.94:p.z=.97;v.co=inv@p
  changes.append([o.name,'顶端伸入上栏0.01，消除0.01悬空'])
 if o.name.startswith('Classical_flower_urn'):
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z<1.745:p.z=1.72;v.co=inv@p
  changes.append([o.name,'盆脚下延进入柱帽0.01，消除0.01悬空'])

# True architectural openings through the finite facade; closed leaves/glass remain in place.
wall=bpy.data.objects['Visible_violet_masonry_facade_patch']
for src in [o for o in s.objects if o.type=='MESH' and o.name.startswith(('Pointed_double_door','Tall_cyan_leaded_window'))]:
 pts=sorted(set((round((src.matrix_world@v.co).x,6),round((src.matrix_world@v.co).z,6)) for v in src.data.vertices))
 cx=sum(p[0] for p in pts)/len(pts);cz=sum(p[1] for p in pts)/len(pts)
 pts.sort(key=lambda p:math.atan2(p[1]-cz,p[0]-cx));n=len(pts)
 vs=[(x,y,z) for y in [.1,.95] for x,z in pts];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new('尖拱洞口切割体');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('TEMP_OPENING',me);s.collection.objects.link(ob)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 bpy.context.view_layer.objects.active=wall;mod=wall.modifiers.new('门窗真洞口','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(ob,do_unlink=True)
 changes.append([src.name,'对应立面真开尖拱孔，保留关闭门扇/玻璃和墙厚洞口回边'])
wall['evidence']='有限立面三个真尖拱孔；洞口深度及不可见背面为推定，无室内'
bm=bmesh.new();bm.from_mesh(wall.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(wall.data);bm.free()

# Replace finite underlay by a load-bearing finite slab, with no garden perimeter walls.
o=bpy.data.objects['INFERRED_thin_support_under_visible_patch'];bpy.data.objects.remove(o,do_unlink=True)
cube('推定_有限基础板_闭合底面',(0,-2.325,-.20),(13.10,6.35,.40),'violet_masonry')
for side in [-1,1]:
 cube('推定_侧栏连续承托基座',(side*5,-2.30,.09),(.64,5.15,.28),'aged_limestone')
 cube('推定_花槽后端挡土边',(side*3.35,.13,.08),(3.45,.12,.25),'aged_limestone')
for i,(ya,yb,top) in enumerate([(-.47,-.14,.085),(-.14,.14,.17),(.14,.47,.25)]):
 cube('门前浅阶_%02d_踏步'%i,(0,(ya+yb)/2,top/2),(2.48,yb-ya,top),'aged_limestone')
for x,y in [(-2.9,-3.9),(2.9,-3.9),(-2.145,-.625),(2.145,-.625)]:
 cube('推定_花架埋入式柱脚',(x,y,-.02),(.18,.18,.30),'dark_stem')
# repair world surface normals, fill UVs on additions
for o in s.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  uv=o.data.uv_layers.new()
  for p in o.data.polygons:
   ax=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
   for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=(o.data.vertices[vi].co[ax[0]],o.data.vertices[vi].co[ax[1]])
s.unit_settings.system='NONE';s['说明']='开放式花园和有限立面，无新增屋顶/围墙/城堡厅连接。所有隐藏闭合与支撑是合理推定，模型单位非实测米。'
# Lights placed well outside structural mesh bounds; one consistent setup for all ordinary cameras.
for o in list(s.objects):
 if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
for name,p,energy,size in [('检视主光',(0,-8,13),2300,5),('检视后光',(1,8,12),1800,4),('底面补光',(-2,-3,-7),650,3)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.size=size;o.rotation_euler=(Vector((0,-2,2))-o.location).to_track_quat('-Z','Y').to_euler()
s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
views=[('01_正面',(0,-15,5.0)),('02_左前',(-12,-13,7)),('03_右前',(12,-13,7)),('04_右侧',(16,-2,6)),('05_右后',(12,9,8)),('06_背面',(0,14,6)),('07_左后',(-12,9,8)),('08_左侧',(-16,-2,6)),('09_俯视',(0,-2,19)),('10_底面',(10,-11,-9))]
for n,pos in views:
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=n;o.rotation_euler=(Vector((0,-1.8,2.4))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=30
s.camera=bpy.data.objects['02_左前'];s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
json.dump(changes,open(D+'/qa/真实几何变更.json','w'),ensure_ascii=False,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=D+'/models/Garden_Complete_Textured.blend',compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=D+'/models/Garden_Complete_Textured.glb',export_format='GLB',use_selection=True,export_extras=True)
if not os.path.exists(R+'/RENDER_APPROVED'):raise SystemExit('Geometry candidate only; awaiting independent contact review')
# ordinary geometry views in stable material-color workbench. Textured source views separately use Cycles.
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.07,.07,.07)
for n,_ in views:
 s.camera=bpy.data.objects[n];s.render.filepath=D+'/views/'+n+'.png';bpy.ops.render.render(write_still=True)
# Explicit cut through the center x=0, only in separate diagnostic copy.
bpy.ops.wm.save_as_mainfile(filepath=R+'/inspection_working.blend',compress=True)
for o in list(s.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);p=o.matrix_world.inverted()@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((1,0,0));bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=p,plane_no=normal,clear_outer=True,clear_inner=False);bm.to_mesh(o.data);bm.free()
s.camera=bpy.data.objects['03_右前'];s.render.filepath=D+'/views/11_明确剖视_沿X0切除右半.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=D+'/models/Garden_DIAGNOSTIC_CUTAWAY.blend',compress=True)
