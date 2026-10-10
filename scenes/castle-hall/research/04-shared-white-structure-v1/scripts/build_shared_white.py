import bpy,bmesh,math,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];P=R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));S=bpy.context.scene
C=bpy.data.collections.new('13_Source_Right_Arch_and_Visible_Stairs');S.collection.children.link(C)
I=bpy.data.collections.new('14_Inferred_Bounded_Stairwell_Continuation');S.collection.children.link(I)
plaster=bpy.data.materials['Plaster | original UV PBR'];stone=bpy.data.materials['RoseStone | original UV PBR'];changes=[]
def mesh(name,vs,fs,ma=stone,col=C,evidence='Source-observed profile with approximate dimensions; physical thickness inferred'):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o)
 if ma:me.materials.append(ma)
 o['evidence']=evidence;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  ax=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=ax]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.25,v[axes[1]]*.25)
 return o
def box(name,loc,d,ma=stone,col=C,evidence='Source-observed profile; thickness and exact dimension approximate'):
 x,y,z=loc;dx,dy,dz=[v/2 for v in d];vs=[(x+i*dx,y+j*dy,z+k*dz) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,col,evidence)
def extrude_yz(name,poly,x0,x1,ma=stone,col=C,evidence='Source-observed arch profile; exact depth approximate'):
 n=len(poly);vs=[(x,y,z) for x in [x0,x1] for y,z in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,ma,col,evidence)
def boolean(o,cut):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Permanent actual through aperture','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name)
def kill(o,reason):
 changes.append({'removed':o.name,'reason':reason});bpy.data.objects.remove(o,do_unlink=True)
# Replace only the right-wall panel within the newly observed column bay. No view-dependent edits.
for o in list(S.objects):
 if o.type!='MESH':continue
 if o.name=='ARCH_Side_wall_1_with_apertures':kill(o,'Rebuild fixed right wall with 3 retained real windows and new permanent arched aperture');continue
 if o.name.startswith(('Side recessed night panel','Side window','Window_1_5','Window_1_-1')):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
  if (mn[0]+mx[0])/2>6.6 and 3<(mn[1]+mx[1])/2<7 and mx[1]-mn[1]<4:kill(o,'Remove unsupported repeated window in newly observed solid-panel/arch bay')
  elif (mn[0]+mx[0])/2>6.6 and -3<(mn[1]+mx[1])/2<.9 and mx[1]-mn[1]<4:
   for v in o.data.vertices:v.co.y=-2.575+(v.co.y+2.575)*(2.475/3.15)
   o['evidence']='Inherited near window shortened to avoid conflict with observed arched opening. Its unseen exact extent is inferred, not source validated.'
   changes.append({'modified':o.name,'reason':'Fixed adjacency repair: shorten inferred near-window end, keeping most of its geometry, rather than leave frame/glazing inside the arch passage'})
wall=box('ARCH_Side_wall_1_with_windows_and_right_arch',(7.18,5,4.4),(.36,34,8.8),plaster,evidence='Right wall corrected to include visible arched side opening; untouched extent remains inherited inference')
for y in [-1,11,17]:
 cut=box('TEMP_WINDOW_CUT',(7.18,-1.3375 if y==-1 else y,4.1),(1.2,2.475 if y==-1 else 3.15,6.6),None);boolean(wall,cut);bpy.data.objects.remove(cut,do_unlink=True)
# Candidate geometry from the existing X=7 wall, calibrated planar source correspondences, and visible lower jamb.
# Near jamb and arch apex partly cropped/occluded: width and top use a disclosed conservative prior, not measured truth.
yc=1.76;radius=1.30;spring=2.55;far=yc+radius;near=yc-radius
cutrad=radius+.025
poly=[(yc-cutrad,-.12),(yc+cutrad,-.12),(yc+cutrad,spring)]+[(yc+cutrad*math.cos(k*math.pi/96),spring+cutrad*math.sin(k*math.pi/96)) for k in range(1,97)]
cut=extrude_yz('TEMP_RIGHT_ARCH_CUT',poly,6.2,7.8,None);boolean(wall,cut)
for o in list(S.objects):
 if o.type=='MESH' and o.name.startswith('Stone lower skirting'):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  if min(p.x for p in pts)>6.5:boolean(o,cut);changes.append({'modified':o.name,'reason':'Cut skirting across same physical arch opening'})
bpy.data.objects.remove(cut,do_unlink=True)
# Three volumetric concentric archivolts and full-height jambs. Every part closed, not double-sided planes.
for n,(r0,r1,x0,x1) in enumerate([(radius,radius+.16,6.78,7.50),(radius+.16,radius+.30,6.66,7.44),(radius+.30,radius+.42,6.76,7.40)]):
 ring=[(yc+r0*math.cos(k*math.pi/96),spring+r0*math.sin(k*math.pi/96)) for k in range(97)]+[(yc+r1*math.cos(k*math.pi/96),spring+r1*math.sin(k*math.pi/96)) for k in range(96,-1,-1)]
 extrude_yz(f'RIGHT_ARCH_closed_archivolt_{n+1}',ring,x0,x1)
 for sg in [-1,1]:box(f'RIGHT_ARCH_jamb_layer_{n+1}_{sg}',((x0+x1)/2,yc+sg*(r0+r1)/2,spring/2),(x1-x0,r1-r0,spring))
for sg in [-1,1]:
 y=yc+sg*(radius+.29)
 box(f'RIGHT_ARCH_spring_capital_{sg}',(7.00,y,spring+.025),(.98,.79,.11))
 box(f'RIGHT_ARCH_spring_capital_upper_{sg}',(7.02,y,spring+.14),(.88,.65,.13))
 box(f'RIGHT_ARCH_jamb_plinth_{sg}',(7.04,y,.12),(.84,.67,.24))
# Wide decorative framing extends toward the next column; relief motifs are deliberately not invented in this white stage.
box('RIGHT_ARCH_far_outer_pilaster',(7.04,far+.70,1.34),(.57,.32,2.68))
box('RIGHT_ARCH_far_pilaster_spring_band',(6.93,far+.70,2.62),(.81,.62,.13))
# Grounded monolithic stair flight: 8 bounded treads. Lower 6 profile-supported; upper 2 and far landing are inferred continuation.
x0=7.36;rise=.18;run=.33;N=8;end=x0+N*run
# A single closed stepped profile extruded across Y provides continuous support down to the slab.
prof=[(x0,-.20),(end,-.20),(end,N*rise)]
for k in range(N-1,-1,-1):
 prof.append((x0+k*run,(k+1)*rise))
 if k>0:prof.append((x0+k*run,k*rise))
# Profile uses (X,Z), extrusion direction Y.
n=len(prof);vs=[(x,y,z) for y in [near-.02,far+.02] for x,z in prof];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
stair=mesh('RIGHT_STAIR_monolithic_8_treads',vs,fs,stone,evidence='Ascending lower steps observed in 4528/4529; lower six approximately traced. Upper two treads, exact dimensions and absolute scale inferred; not a recovered full staircase')
stair['observed_lower_treads']=6;stair['inferred_upper_treads']=2
inf='Inferred finite enclosure only. Unseen upper destination/extent is unknown; this is not evidence of a room, doorway, garden link or full staircase endpoint.'
box('INF_STAIR_bounded_floor_support',((7.36+11.20)/2,yc,-.20),(11.2-7.36,2*radius+.40,.4),plaster,I,inf)
for sg in [-1,1]:box(f'INF_STAIR_enclosure_side_{sg}',((7.36+11.2)/2,yc+sg*(radius+.205),2.3),(11.2-7.36,.36,4.6),plaster,I,inf)
box('INF_STAIR_upper_landing',(10.60,yc,.62),(1.20,2*radius,1.64),stone,I,inf)
box('INF_STAIR_unseen_far_closure',(11.20,yc,2.30),(.36,2*radius+.72,4.6),plaster,I,inf)
box('INF_STAIR_enclosure_roof',(9.25,yc,4.62),(4.3,2*radius+.72,.36),plaster,I,inf)
# Neutral inspection illumination; not used as a substitute for physical enclosure.
d=bpy.data.lights.new('RIGHT_STAIR_soft_bounce','AREA');d.energy=65;d.shape='DISK';d.size=2.0;o=bpy.data.objects.new('RIGHT_STAIR_soft_bounce',d);C.objects.link(o);o.location=(9.2,yc,4.0);o.rotation_euler=(Vector((8.3,yc,.4))-o.location).to_track_quat('-Z','Y').to_euler()
def camera_fit(name,data):
 d=bpy.data.cameras.new(name);d.lens=data['lens_mm'];d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.clip_start=.03;d.clip_end=200;o=bpy.data.objects.new(name,d);bpy.data.collections['09_Cameras'].objects.link(o)
 rr=Vector(data['right']);up=Vector(data['up']);fwd=Vector(data['forward']);o.matrix_world=Matrix((rr,up,-fwd)).transposed().to_4x4();o.location=data['location'];o['calibration']='Approximate source camera for fixed candidate geometry. No screenshot warp.';return o
fit=json.loads((R/'qa/source_camera_fits.json').read_text());p28=json.loads((R/'qa/planar_camera_fit_4528.json').read_text())
camera_fit('FIT_HD_4528_RIGHT_ARCH',p28);camera_fit('FIT_HD_4529_RIGHT_ARCH',fit['fit_4529'])
def cam(name,loc,target,lens):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.04;d.clip_end=200;o=bpy.data.objects.new(name,d);bpy.data.collections['09_Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o
main=cam('CANDIDATE_NORMAL_MAIN',(-2.9,-4.0,1.75),(3.6,7.8,2.45),22)
cam('QA_ARCH_DIRECT_INTERNAL',(3.55,yc,1.5),(9,yc,1.7),22)
cam('QA_STAIR_FROM_LANDING',(10.55,yc,2.85),(4,yc,.75),24)
for o in S.objects:
 if o.type=='MESH':o.hide_render=False;o.hide_viewport=False
S.camera=main;S['CandidateStage']='Shared white geometry candidate v1, 2026-10-10; not source accepted';S['InputBlendSHA256']=hashlib.sha256(P.read_bytes()).hexdigest();S['SourceNew']='BV1aw411T7ws, fit 4528.936245/4529.796014; holdouts 4527.768968 and 4509.252180 excluded from geometry fit';S['GeometryCompletion']='Inherited full hall shell plus fixed right-side arched opening and finite inferred stairwell envelope';S['UncertaintyNew']='Right opening observed, near jamb/apex partly occluded; width/top/thickness use disclosed priors. Only finite lower stairs are observed; upper continuation and closure inferred. No garden connection.'
S.render.engine='CYCLES';S.render.resolution_x=1180;S.render.resolution_y=664;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.cycles.use_denoising=False;S.cycles.samples=24;S.render.image_settings.file_format='PNG'
notes=bpy.data.texts.new('README_NEW_SHARED_WHITE_CANDIDATE.txt');notes.write('\n'.join(str(S[k]) for k in ['CandidateStage','SourceNew','GeometryCompletion','UncertaintyNew']))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/CastleHall_Shared_Structure_Candidate.blend'),compress=True)
# White file is exactly the same geometry with a neutral material and neutral light colors.
white=bpy.data.materials.new('WHITE_Clay_uniform');white.use_nodes=True;bs=white.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.55,.55,.55,1);bs.inputs['Roughness'].default_value=.75
for o in S.objects:
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(white)
 elif o.type=='LIGHT':o.data.color=(1,1,1)
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.18;S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.9
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/CastleHall_Shared_White_Candidate.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(R/'models/CastleHall_Shared_White_Candidate.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=False,export_extras=True)
(R/'qa/build_changes.json').write_text(json.dumps({'changes':changes,'new_arch':{'wall_x':7,'near_y':near,'far_y':far,'radius':radius,'spring':spring,'status':'candidate dimensions, near edge/apex partly inferred'},'stair':{'start_x':x0,'run':run,'rise':rise,'treads':N,'source_supported_lower_treads':6,'inferred_upper_treads':2,'onward_destination':'unknown'},'unchanged':'All inherited columns, furniture, floor pattern and other geometry, apart from removed obsolete right-bay window and cut skirting','camera_dependent_hiding':False},indent=2))
if os.environ.get('PREVIEW','1')=='1':
 S.camera=bpy.data.objects['FIT_HD_4528_RIGHT_ARCH'];S.render.resolution_percentage=50;S.cycles.samples=16;S.render.filepath=str(R/'renders/preview_fit_4528_white.png');bpy.ops.render.render(write_still=True)
print('SHARED_WHITE_BUILD_DONE',flush=True)
