"""Bounded observed passenger corner, model units. Blender 4.3.2.
No camera-dependent mesh or visibility changes. Door states are timeline frames 1/2.
Run: blender -b -t 8 --python scripts/build_geometry.py
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
base=bpy.data.collections.get('Collection');base.name='GEOMETRY_BOUNDED_CANDIDATE'
scene=bpy.context.scene
scene.unit_settings.system='NONE'
scene['status']='LOCAL PARTIAL RECONSTRUCTION CANDIDATE; not complete car/cabin; source calibration pending'
scene['scale']='Model units only; no measured scale, character not used as ruler'
scene['state_mapping']='Frame 1 closed (S01,S03), frame 2 open (S02); 54 degree angle inferred. No camera triggers.'
scene['context_S04']='605.763813 forward view, adjacency only. No complete dashboard/steering reconstruction.'
records=[]
white=bpy.data.materials.new('WHITE_same_geometry');white.diffuse_color=(.63,.65,.67,1);white.use_nodes=True
bs=white.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.63,.65,.67,1);bs.inputs['Roughness'].default_value=.7
def reg(o,id,group,role,evidence='S01,S02,S03',note='Visible shape approximate; unseen thickness/back inferred'):
    o.name=id;o['object_id']=id;o['material_group']=group;o['evidence_class']=role;o['source_ids']=evidence;o['limitations']=note
    if o.type=='MESH':o.data.materials.append(white)
    records.append(dict(id=id,material_group=group,evidence_class=role,source_ids=evidence,limitations=note))
    return o
def bevel(o,amt=.015):
    b=o.modifiers.new('physical_edge_radius','BEVEL');b.width=amt;b.segments=3
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
    for p in o.data.polygons:p.use_smooth=True
    m=o.modifiers.new('weighted_normals','WEIGHTED_NORMAL');m.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=m.name)
    return o
def cube(id,loc,dim,group='leather',role='observed-front_inferred-solid',radius=.015,evidence='S01,S02,S03',note='Visible surface approximate; backside and thickness inferred'):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    reg(o,id,group,role,evidence,note)
    if radius:bevel(o,radius)
    return o
def prism(id,poly,x0,x1,group='leather',role='observed-front_inferred-solid',radius=.01,note='YZ outline approximate; thickness/back inferred',evidence='S01,S02,S03'):
    n=len(poly);vs=[(x,y,z) for x in (x0,x1) for y,z in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new(id+'_mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(id,me);base.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
    reg(o,id,group,role,evidence,note)
    if radius:bevel(o,radius)
    return o
def tube(id,points,radius,group='rubber',role='observed-front_inferred-solid',evidence='S01,S02,S03',note='Curve envelope approximated; cross-section inferred'):
    cu=bpy.data.curves.new(id+'_curve','CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=radius;cu.bevel_resolution=3;cu.use_fill_caps=True
    s=cu.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    o=bpy.data.objects.new(id,cu);base.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
    return reg(o,id,group,role,evidence,note)
def ellipsoid(id,loc,scale,group='leather',role='observed-front_inferred-solid',note='Visible outer contour approximate; rear profile inferred'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    reg(o,id,group,role,note=note)
    for p in o.data.polygons:p.use_smooth=True
    return o
def ring_y(id,center,r0,r1,depth,group='metal'):
    x,y,z=center;N=64;vs=[]
    for yy,r in ((y-depth/2,r0),(y-depth/2,r1),(y+depth/2,r0),(y+depth/2,r1)):
        vs += [(x+r*math.cos(a*2*math.pi/N),yy,z+r*math.sin(a*2*math.pi/N)) for a in range(N)]
    fs=[]
    for j in range(N):
        k=(j+1)%N
        fs.extend([(j,k,N+k,N+j),(2*N+j,3*N+j,3*N+k,2*N+k),(j,2*N+j,2*N+k,k),(N+j,N+k,3*N+k,3*N+j)])
    m=bpy.data.meshes.new(id);m.from_pydata(vs,[],fs);m.update();o=bpy.data.objects.new(id,m);base.objects.link(o);reg(o,id,group,'observed-ring_inferred-depth');bevel(o,.002)
    return o
def bool_cut(obj,cut):
    bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('true_circular_vent_opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Fixed local boundary. These end at exposed study edges, not unknown whole car surfaces.
cube('B01_inferred_floor_boundary',(.41,.03,.07),(1.25,2.08,.10),'carpet','inferred-support',.025,note='Unseen finite floor support and scope boundary, not measured full floor')
cube('B02_sill_fixed',(.98,.02,.16),(.15,1.90,.14),'trim','part-observed_inferred-extent',.025,evidence='S02',note='Open-door sill visible in S02; cross-section/extent inferred')
cube('B03_front_footwell_back',(.41,1.025,.38),(1.25,.11,.57),'carpet','inferred-support',.035,note='Unseen local footwell closure, not full firewall')
prism('A01_fixed_A_pillar',[(1.06,.96),(.93,.97),(.23,1.66),(.37,1.72)],.87,1.04,'headliner',radius=.033)
cube('A02_side_roof_rail',(.955,-.29,1.695),(.16,1.3,.16),'headliner',radius=.045)
cube('A03_partial_headliner',(.45,-.13,1.77),(1.1,1.85,.12),'headliner','observed-front_inferred-boundary',.05,note='Visible roof patch, inferred cap thickness and trimmed left/rear boundaries')
cube('A04_partial_rear_window_return',(.98,-.92,1.30),(.13,.12,.76),'rubber','part-observed_inferred-extent',.03,note='Right edge/window return visible; not a complete B pillar')
visor=cube('A05_passenger_visor',(.57,.40,1.62),(.62,.38,.065),'visor','observed-front_inferred-solid',.032);visor.rotation_euler.x=math.radians(-9)
tube('A06_visor_support_inferred',[(.31,.52,1.71),(.31,.52,1.64),(.44,.52,1.64)],.012,'metal','inferred-support',note='Attachment support unobserved')
cube('A07_windshield_lower_return',(.38,1.10,1.02),(1.36,.10,.08),'rubber','part-observed_inferred-extent',.03,evidence='S01,S03; S04 conditional',note='Only right-side connection constrained; broader forward association conditional')
# Dashboard right end. Lower fascia has a physical hole and dark recessed cavity.
cube('D01_dashboard_top',(.38,.91,.985),(1.30,.56,.095),'dash_top',radius=.045)
fas=cube('D02_dashboard_end_fascia',(.38,.787,.745),(1.30,.30,.39),'carbon',radius=.025)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.112,depth=.6,location=(.80,.78,.77),rotation=(math.pi/2,0,0));bool_cut(fas,bpy.context.object)
ring_y('D03_vent_round_rim',(.80,.626,.77),.101,.117,.025)
ring_y('D04_vent_recess_wall',(.80,.725,.77),.100,.111,.19,'rubber')
cube('D05_vent_recess_end',(.80,.833,.77),(.203,.025,.203),'rubber','inferred-cavity',.01,note='Deep unobserved cavity termination; front aperture is not filled')
for i,z in enumerate([.715,.770,.825]):
    width=2*math.sqrt(.098**2-(z-.77)**2)
    sl=cube(f'D06_vent_louver_{i+1}',(.80,.665,z),(width,.052,.014),'vent',radius=.004,note='Three approximate visible louvers, depth inferred');sl.rotation_euler.x=.18
cube('D07_lower_dash_local',(.38,.83,.48),(1.28,.26,.16),'leather','part-observed_inferred-extent',.045,note='Visible lower right corner only; hidden continuation approximate')
# Door assembly, one immutable mesh set, physically parented to one hinge.
hinge=bpy.data.objects.new('STATE_passenger_door_hinge',None);base.objects.link(hinge);hinge.location=(.99,.93,0);hinge['state_info']='Frame 1: closed; frame 2: open 54deg inferred; source time identity explicit'
door_start=set(bpy.data.objects)
poly=[(.91,.22),(.91,.98),(-.88,.98),(-.92,.24),(-.74,.14),(.66,.14)]
prism('P01_door_carrier',poly,.956,1.035,'leather',radius=.025,note='Outline inferred through character occlusion; thickness/back unobserved')
prism('P02_upper_belt',[(.87,.86),(.87,.98),(-.85,.98),(-.87,.85)],.898,.971,'leather',radius=.022)
prism('P03_woven_upper_insert',[(.84,.755),(.86,.855),(-.85,.855),(-.86,.745)],.892,.958,'carbon',radius=.008,note='Woven strip visible at left/right; middle correspondence occluded')
prism('P04_padded_mid_panel',[(.82,.53),(.83,.743),(-.83,.733),(-.83,.50)],.89,.962,'leather',radius=.03)
prism('P05_armrest_woven',[(.77,.39),(.79,.51),(.46,.54),(-.59,.51),(-.80,.45),(-.80,.38)],.765,.967,'carbon',radius=.022,note='Armrest visible in fragments; curvature/hidden span inferred')
tube('P06_armrest_edge',[(.757,.70,.435),(.757,.40,.48),(.757,-.20,.46),(.757,-.64,.42)],.009,'trim',note='Visible light edge; cross-section inferred')
cube('P07_handle_recess',(.872,.43,.65),(.035,.24,.065),'rubber','part-observed_inferred-extent',.02,note='Small dark pull region; exact handle mechanism unknown')
cube('P08_pull_handle',(.844,.43,.65),(.025,.17,.018),'metal','part-observed_inferred-extent',.007,note='Approximate pull, not verified mechanical assembly')
# Pocket: opening is physical space between carrier and front lip, with side/base closures.
cube('P09_pocket_base',(.866,-.08,.22),(.20,1.10,.045),'rubber','part-observed_inferred-extent',.015)
cube('P10_pocket_outer_wall',(.774,-.08,.305),(.035,1.10,.18),'leather','part-observed_inferred-extent',.015)
for i,y in enumerate([-.61,.45]):cube(f'P11_pocket_end_{i+1}',(.87,y,.305),(.20,.04,.18),'leather','inferred-support',.012,note='Pocket end closure inferred, opening remains above lip')
win=[(.83,.99),(.23,1.61),(-.76,1.61),(-.88,.99)]
prism('P12_side_window_glass',win,.994,1.000,'glass','observed-transparent_inferred-thickness',radius=0,note='Transparent pane; no opaque fill; thickness .006 model units inferred')
for i in range(4):
    a=win[i];b=win[(i+1)%4]
    tube(f'P13_window_frame_{i+1}',[(.996,*a),(.996,*b)],.019,'rubber',note='Continuous frame around genuine glazed opening; profile inferred')
prism('P14_mirror_sail',[(.85,.99),(.59,.99),(.66,1.22)],.98,1.045,'rubber',radius=.012)
tube('P15_mirror_stem',[(1.02,.73,1.07),(1.12,.74,1.09)],.027,'trim',note='Visible stem attachment; cross-section inferred')
ellipsoid('P16_mirror_housing',(1.18,.73,1.14),(.075,.16,.10),'metal')
ellipsoid('P17_mirror_glass',(1.110,.718,1.14),(.010,.141,.085),'mirror',note='Black reflective appearance; environmental reflected content not reconstructed')
for o in set(bpy.data.objects)-door_start:
    mw=o.matrix_world.copy();o.parent=hinge;o.matrix_world=mw
for frame,angle in [(1,0),(2,54)]:
    hinge.rotation_euler.z=math.radians(angle);hinge.keyframe_insert(data_path='rotation_euler',frame=frame)
for fc in hinge.animation_data.action.fcurves:
    for kp in fc.keyframe_points:kp.interpolation='CONSTANT'
scene.frame_start=1;scene.frame_end=2;scene.frame_set(1)
scene.timeline_markers.new('S01_S03_CLOSED',frame=1);scene.timeline_markers.new('S02_OPEN_ANGLE_INFERRED',frame=2)
# Limited seat edge only: no hidden seat/body reconstruction.
prism('S01_visible_seat_outer_bolster',[(-.72,.32),(-.59,.43),(-.74,1.25),(-.86,1.46),(-.96,1.40),(-.93,1.13)],.71,.89,'seat','part-observed_inferred-extent',radius=.04,note='Narrow right visible seat edge only; complete cushion/back/headrest deliberately absent')
tube('S02_seat_edge_piping',[(.705,-.71,.40),(.705,-.71,.72),(.705,-.82,1.18),(.705,-.91,1.39)],.007,'trim','part-observed_inferred-extent',note='Visible side border approximate; not full seat perimeter')
# The upper-left interior mirror is visible in S01/S03; include a bounded partial assembly.
cube('M01_partial_interior_mirror',(-.02,.78,1.49),(.32,.065,.14),'rubber','part-observed_inferred-extent',.035,evidence='S01,S03',note='Visible cropped interior mirror; full placement and support uncalibrated')
cube('M02_interior_mirror_glass',(-.02,.743,1.49),(.275,.009,.105),'mirror','part-observed_inferred-extent',.025,evidence='S01,S03')
tube('M03_mirror_support_inferred',[(.01,.80,1.54),(.01,.89,1.69)],.018,'rubber','inferred-support',evidence='S01,S03',note='Mount unobserved')
# Cameras: approximate initial source viewpoints, never used as state selectors.
cams=bpy.data.collections.new('CAMERAS_uncalibrated');scene.collection.children.link(cams)
def camera(name,loc,target,lens=30):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);cams.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.01;d.clip_end=100;o['calibration']='Manual approximate; source fit not accepted';return o
camera('SRC_S01_closed',(-.40,-.02,1.15),(.95,.02,1.10),25)
camera('SRC_S02_open',(-.40,-.10,1.16),(.97,.03,1.08),25)
camera('SRC_S03_closed',(-.57,-.06,1.15),(.95,.04,1.08),26)
camera('CTX_S04_forward_not_registered',(-.12,-.05,1.18),(-.12,2.0,1.18),24)
camera('MAIN_passenger_local',(-1.35,-1.35,1.30),(.65,.13,.96),36)
checks=[((-2.5,0,1.1),(.5,0,.9)),((2.8,.2,1.3),(.7,0,.9)),((.4,-3,1.4),(.5,0,.9)),((.4,3,1.5),(.5,0,.9)),((-1.8,-2.2,2.6),(.5,0,.9)),((2.4,-2.2,2.4),(.7,0,.9)),((.4,0,4),(.4,0,.6)),((-1.7,-1.5,.05),(.5,0,.7))]
for i,(loc,target) in enumerate(checks):camera(f'CHECK_{i+1:02}',loc,target,42 if i!=6 else 40)
lights=bpy.data.collections.new('LIGHTS_fixed_diagnostic_rig');scene.collection.children.link(lights)
for name,loc,power,color,size in [('key',(-2,-1,3),180,(.73,.83,1),3),('door',(2,0,2.4),130,(1,.78,.55),2),('front',(.1,2,2),100,(.78,.85,1),2),('fill',(-1,-2,.8),60,(1,1,1),2)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);lights.objects.link(o);o.location=loc;o.rotation_euler=(Vector((.5,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.055,.055,.055)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.067,.09,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.camera=bpy.data.objects['MAIN_passenger_local']
scene['lighting']='Fixed neutral inspection rig across all source cameras; source night lighting not recovered'
for o in bpy.context.selected_objects:o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/car_passenger_cabin_white.blend'))
(ROOT/'qa/object-registry.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('WHITE_SAVED',len(records),'objects')
