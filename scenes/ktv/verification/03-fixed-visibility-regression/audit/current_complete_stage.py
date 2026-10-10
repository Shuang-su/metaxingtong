import bpy,bmesh,os,math,json
from mathutils import Vector
ROOT='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery'
bpy.ops.wm.open_mainfile(filepath='/workspace/scratch/fa58bfcf0425/ktv_fullroom/source/restored/models/Xingtong_KTV_Textured.blend')
sc=bpy.context.scene;sc.unit_settings.system='NONE';sc['scope']='Finite complete open stage. Indoor/outdoor and city screen/remote-background nature unconfirmed. No evidenced doors, glazing, walls or roof.'
sc['inference']='Platform thickness, underside, supporting beams, access ramp and star suspension gantry inferred; proportions are not surveyed metric dimensions.'
sc.render.threads_mode='FIXED';sc.render.threads=3;sc.render.resolution_x=792;sc.render.resolution_y=446;sc.render.resolution_percentage=100;sc.cycles.samples=48;sc.cycles.use_denoising=False
C=bpy.data.collections.new('11_INFERRED_Complete_Stage_Structure');sc.collection.children.link(C)
def mat(n,col):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.5;return m
blue=bpy.data.materials['Cobalt_stage_edge'];dark=bpy.data.materials['Satin_black_hardware'];silver=bpy.data.materials['Cool_brushed_aluminium']
def put(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o['evidence']='inferred hidden structure; not source-confirmed';return o
def box(n,loc,dim,ma=dark):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=put(bpy.context.object);o.name='INFERRED_'+n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o
def beam(n,a,b,r=.04,ma=silver):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=put(bpy.context.object);o.name='INFERRED_'+n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(ma);return o
def prism(n,poly,z0,z1,ma):
 N=len(poly);me=bpy.data.meshes.new(n);me.from_pydata([(x,y,z) for z in [z0,z1] for x,y in poly],[],[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]);me.update();o=bpy.data.objects.new(n,me);C.objects.link(o);o.data.materials.append(ma);o['evidence']='inferred continuous support under observed surface';return o
old=bpy.data.objects.get('INFERRED_support_under_visible_patch');bpy.data.objects.remove(old,do_unlink=True)
poly=[(-6,-4.5),(6,-4.5),(6,.95),(.82,3.65),(-6,.9)]
prism('INFERRED_continuous_closed_deck',poly,-.45,-.012,blue)
# Existing upper checker/band surfaces become thin solid finishes, retaining their top coordinates.
repair=[]
for o in list(sc.objects):
 if o.type!='MESH' or any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection):continue
 bm=bmesh.new();bm.from_mesh(o.data);n0=len(bm.verts)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 if n0!=len(o.data.vertices):repair.append([o.name,n0,len(o.data.vertices)])
 if o.name.startswith(('Checker_','Visible_blue_rear_band')):
  mod=o.modifiers.new('Real_finish_thickness','SOLIDIFY');mod.thickness=.014;mod.offset=-1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
# Load-bearing subframe grounded on a compact finite underside; no infinite ground plane.
for x in [-4.8,0,4.8]:box('underside_longitudinal_beam',(x,-1.8,-.56),(.16,5.3,.22))
for y in [-3.7,-.4]:box('underside_crossbeam',(0,y,-.56),(11.5,.16,.22))
for x in [-4.8,4.8]:
 for y in [-3.7,-.4]:box('support_foot',(x,y,-.79),(.35,.35,.26))
# A finite front access ramp meets the deck without a floating edge.
vs=[(-1,-4.5,0),(1,-4.5,0),(-1,-7.5,-.92),(1,-7.5,-.92),(-1,-4.5,-.92),(1,-4.5,-.92)]
me=bpy.data.meshes.new('ramp');me.from_pydata(vs,[],[(0,2,3,1),(0,1,5,4),(0,4,2),(1,3,5),(2,4,5,3)]);me.update();o=bpy.data.objects.new('INFERRED_front_access_ramp',me);C.objects.link(o);o.data.materials.append(blue)
# Four post gantry, deliberately no roof panel or invented enclosing walls.
for x in [-5.65,5.65]:
 for y in [-.8,0.75]:
  box('gantry_base',(x,y,-.006),(.3,.3,.012));beam('gantry_post',(x,y,0),(x,y,6.3),.055)
for z in [6.05,6.3]:
 for y in [-.8,0.75]:beam('gantry_crossbar',(-5.65,y,z),(5.65,y,z))
 for x in [-5.65,5.65]:beam('gantry_depthbar',(x,-.8,z),(x,0.75,z))
for x,y in [(-1.36,.1),(1.2,.6),(2.88,.5)]:
 beam('suspension_pickup_crossbar',(x,-.8,6.3),(x,0.75,6.3),.025)
 beam('suspension_extension',(x,y,5.7),(x,y,6.3),.0035)
# Add tiny contact pads under old foot endpoints rather than move evidence-based furnishings.
for o in list(sc.objects):
 if o.type=='MESH' and ('short_dark_foot' in o.name or 'Tripod_silver_foot' in o.name):
  p=o.matrix_world.translation;beam('furniture_contact_pad',(p.x,p.y,-.01),(p.x,p.y,.025),.054 if 'short' in o.name else .027, dark)
for i,(x,y) in enumerate([(-1.36,.1),(1.2,.6),(2.88,.5)]):
 star=bpy.data.objects['Silver_star_%02d'%i];top=max((star.matrix_world@v.co).z for v in star.data.vertices)
 beam('star_line_connector_%02d'%i,(x,y,top-.035),(x,y,top+.025),.01)
# Small solid seating pads beneath stage hardware preserve the observed elevations.
for i,(x,y) in enumerate([(-3.85,1.48),(-2.13,2.58),(-.56,3.08),(1.80,3.08),(3.38,2.11)]):box('stage_lamp_contact_pad_%02d'%i,(x,y,0),(.28,.24,.02))
for i,(x,y) in enumerate([(-2.98,1.94),(2.35,2.58)]):box('monitor_contact_pad_%02d'%i,(x,y,.005),(.57,.33,.03))
beam('lamp_foot_contact',(-2.55,2.05,-.012),(-2.55,2.05,0),.188,dark)
beam('planet_pickup_bracket',(-3.42,-.8,6.3),(-3.42,1,6.3),.025)
beam('planet_suspension',(-3.42,1,3.38),(-3.42,1,6.3),.0035)
# Move only fixed lighting rig to sit below gantry, same lighting for every view; no view-conditioned geometry.
for name in ['Magenta_left_rim','Cyan_right_rim']:
 o=bpy.data.objects[name];o.location.y=-1.3;o.data.size=1.5;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['Pale_ceilingless_soft_reflection'].location.z=5.35;bpy.data.objects['Pale_ceilingless_soft_reflection'].data.size=1.8
bpy.data.collections['09_Optional_Moving_Balloon_Dog'].hide_render=True;bpy.data.collections['09_Optional_Moving_Balloon_Dog'].hide_viewport=True
sc['lighting_note']='Area emitters are not ceiling geometry. No wall/roof exists to intersect. All emitter discs are documented in QA.'
def camera(n,p,t,lens=35):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=250;return o
views=[('01_front',(0,-10,2.7),(0,0,1.6)),('02_left',(-5,-4,1.7),(0,.6,1.3)),('03_right',(5,-4,1.7),(0,.6,1.3)),('04_rear',(0,3.35,1.7),(0,-1,1.1)),('05_rear_left',(-4.7,1.6,1.7),(0,-.6,1.1)),('06_rear_right',(4.7,1.6,1.7),(0,-.6,1.1)),('07_front_left',(-4.5,-3.9,1.7),(1,.3,1.4)),('08_front_right',(4.5,-3.9,1.7),(-1,.3,1.4)),('09_shell',(11,-14,10),(0,-.5,2)),('10_underside',(9,-10,-4),(0,-1,-.3)),('11_rear_structure',(10,8,5),(0,0,2.5)),('12_top',(0,-.5,14),(0,-.5,0))]
for n,p,t in views:camera(n,p,t,32 if n.startswith(('09','10','11')) else 35)
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
sc.camera=bpy.data.objects['01_front'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/KTV_Complete_Open_Stage.blend',compress=True)
json.dump({'merged_degenerate_vertices':repair,'view_geometry':'identical all views, no hidden walls or per-camera scene changes'},open(ROOT+'/qa/repair_log.json','w'),indent=2)
if os.getenv('PREVIEW_ONLY')=='1':
 sc.camera=bpy.data.objects['09_shell'];sc.render.filepath=ROOT+'/renders/09_shell.png';bpy.ops.render.render(write_still=True);quit()
