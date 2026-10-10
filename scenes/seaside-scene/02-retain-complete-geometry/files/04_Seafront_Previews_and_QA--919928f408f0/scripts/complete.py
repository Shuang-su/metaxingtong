import bpy,bmesh,os,json,math
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
bpy.ops.wm.open_mainfile(filepath=R+'/source/models/Seafront_Textured.blend');S=bpy.context.scene
S.unit_settings.system='NONE';S['dimensions']='无量纲相对建模单位；非测绘米制';S['scope']='独立开放海滨；未增加室内连接、墙或顶棚。';S['evidence']='BV1mx4y1z7oY; stored 360p viewport captures, crop1188x668; camera changes shown but no calibrated baseline.'
os.makedirs(R+'/models',exist_ok=True)
changes=[]
def bmfix(o,fill=False,weld=False):
 bm=bmesh.new();bm.from_mesh(o.data)
 if weld:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
 if fill:bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
def slab(o,bottom):
 me=o.data;vs=[tuple(v.co) for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons];n=len(vs)
 bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();es=[(e.verts[0].index,e.verts[1].index) for e in bm.edges if e.is_boundary];bm.free()
 vs+= [(v[0],v[1],bottom) for v in vs];fs += [tuple(i+n for i in reversed(f)) for f in list(fs)];fs += [(a,b,b+n,a+n) for a,b in es]
 mats=list(me.materials);uvs=[tuple(d.uv) for d in me.uv_layers.active.data] if me.uv_layers else []
 new=bpy.data.meshes.new(me.name+'_closed');new.from_pydata(vs,[],fs);new.update();o.data=new
 for m in mats:new.materials.append(m)
 uv=new.uv_layers.new(name='UVMap')
 for p in new.polygons:
  for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=uvs[li] if li<len(uvs) else (vs[vi][0],vs[vi][1])
 bmfix(o);o['completion']='推断实体底面与边缘，不是源图证实断面';changes.append(o.name+' closed bottom '+str(bottom))
for o in list(bpy.data.objects):
 if o.type!='MESH':continue
 n=o.name
 if n.startswith('Curb_vertical_riser'):bpy.data.objects.remove(o,do_unlink=True);continue
 if n.startswith('Chain_'):bmfix(o,weld=True)
 elif n.startswith('Palm_') and not n.endswith('true_leaflet_surfaces'):bmfix(o,fill=True)
 elif n.endswith('curved_pole'):bmfix(o,fill=True)
 elif n=='Two_way_road_7m20':slab(o,-.45)
 elif n in ['Promenade_2m25','Inland_walk_1m10'] or n.startswith('Curb_top'):slab(o,-.45)
 elif n in ['Continuous_rocky_seawall_slope','Undulating_coastal_land_slope']:slab(o,-4.8)
 elif n.startswith('Continuous_white_edge') or n.startswith('Center_dash'):slab(o,-.003)
# finite structural fill ties underside road and verge, not a new building.
road=bpy.data.objects['Two_way_road_7m20'];o=road.copy();o.data=road.data.copy();o.name='Inferred_finite_roadbed_core';bpy.data.collections['05_Cliff_and_Terrain'].objects.link(o)
# Strip top section retained same path, transverse extension to under both walks.
for v in o.data.vertices:
 s=v.co.y;der=-.00044*max(s-38,0);nx=1/math.sqrt(1+der*der);center=-.00022*max(s-38,0)**2;off=(v.co.x-center)/nx
 v.co.x += (-2.4 if off<0 else 1.25)*nx
 v.co.z=-.45 if v.co.z>-.2 else -4.8
bmfix(o);o.data.materials.clear();o.data.materials.append(bpy.data.materials['PBR_Coastal_Rock']);o['completion']='推断有限路基，非实测结构'
# Contact fixes via actual terrain ray intersections, entire plant group together.
terrain=bpy.data.objects['Undulating_coastal_land_slope'];contacts=[]
for trunk in [o for o in bpy.data.objects if o.name.startswith('Palm_') and o.name.endswith('curved_trunk')]:
 pts=sorted([trunk.matrix_world@v.co for v in trunk.data.vertices],key=lambda p:p.z)[:9];base=sum(pts,Vector())/len(pts)
 hit,loc,nor,ind=terrain.ray_cast(Vector((base.x,base.y,50)),Vector((0,0,-1)))
 if hit:
  dz=loc.z-base.z-.015
  for q in bpy.data.objects:
   if q.name.startswith('_'.join(trunk.name.split('_')[:2])+'_'):q.location.z+=dz
  contacts.append({'object':trunk.name,'vertical_shift':dz,'terrain_z':loc.z})
# All vegetation surfaces legitimately double sided; no artificial solid leaves.
for m in bpy.data.materials:m.use_backface_culling=False
# remove view-dependent theatrical optional disk rather than toggle by camera.
for n in ['OPTIONAL_6310_Stylized_Record_Sun','Far_ocean_to_horizon','Physical_visible_sun_disc']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
S['environment_note']='无限远海/舞台日轮未包含；保留可编辑有限起伏水面，所有相机统一几何。'
# Stable proof illumination for boundaries.
S.world.use_nodes=True;nt=S.world.node_tree;nt.nodes.clear();bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.38,.44,.52,1);bg.inputs[1].default_value=.65;out=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],out.inputs[0])
for o in bpy.data.objects:
 if o.type=='LIGHT':
  if o.data.type=='SUN':o.data.energy=2.3;o.data.color=(1,.93,.83);o.rotation_euler=(.55,-.5,-.5)
  elif o.data.type=='AREA':o.data.energy=0
S.use_nodes=False;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
for im in bpy.data.images:
 if im.source=='FILE':
  p=R+'/source/textures/'+os.path.basename(im.filepath)
  if not im.packed_file and os.path.exists(p):im.filepath=p;im.pack()
core=[o for o in S.objects if o.type=='MESH']
for o in core:
 o['source_status']='类型/前景关系由源图支持；后侧、底面、尺寸及远处延伸是推断'
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
# ordinary perspectives, not visibility-dependent.
def camera(n,loc,target,lens=35):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=2500;return o
cams=[camera('QA01_海侧整体',(-35,-45,22),(0,45,1),28),camera('QA02_陆侧背面',(45,10,22),(-1,38,1),28),camera('QA03_近端断面',(-14,-118,7),(-1,-75,-1),38),camera('QA04_远端断面',(-77,584,16),(-55,515,-1),35),camera('QA05_路面通行',(0,-32,2.2),(0,30,2),28),camera('QA06_栏杆外侧',(-13,-8,2),(-5,6,.4),40),camera('QA07_底部',(-18,-40,-16),(-1,25,-2),28),camera('QA08_高位整体',(70,-120,110),(-30,180,0),28),camera('QA09_灯具背面',(15,-18,13),(3,-14,11),45),camera('QA10_地形背侧',(55,34,6),(15,60,1),35)]
S.camera=bpy.data.objects['Camera_B_reference_6435'];S.render.resolution_x=1188;S.render.resolution_y=668
bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_Textured.blend',compress=True)
def export(n):
 bpy.ops.object.select_all(action='DESELECT')
 for o in core:o.hide_set(False);o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/'+n+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
export('Seafront_Textured')
json.dump({'changes':changes,'palm_contacts':contacts},open(R+'/qa/changes.json','w'),indent=2)
for c in cams:
 S.camera=c;S.render.resolution_x=960;S.render.resolution_y=600;S.render.filepath=R+'/renders/'+c.name+'.png';bpy.ops.render.render(write_still=True)
for n in ['Camera_A_reference_6170','Camera_B_reference_6435','Camera_C_side_6310']:
 S.camera=bpy.data.objects[n];S.render.resolution_x=1188;S.render.resolution_y=668;S.render.filepath=R+'/renders/Textured_'+n+'.png';bpy.ops.render.render(write_still=True)
white=bpy.data.materials.new('QA_白模');white.diffuse_color=(.7,.7,.7,1);white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.7,.7,.7,1)
for o in core:o.data.materials.clear();o.data.materials.append(white)
export('Seafront_White');bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Seafront_White.blend',compress=True)
for n in ['Camera_A_reference_6170','Camera_B_reference_6435','Camera_C_side_6310']:
 S.camera=bpy.data.objects[n];S.render.filepath=R+'/renders/White_'+n+'.png';bpy.ops.render.render(write_still=True)
print('COMPLETE')
