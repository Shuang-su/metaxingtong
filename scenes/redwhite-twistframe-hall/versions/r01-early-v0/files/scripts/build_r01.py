import bpy, math, json, os, sys, random
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; VERSION='R01'
random.seed(24)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED'; scene.render.threads=4
scene.render.resolution_x=320; scene.render.resolution_y=176; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'; scene.world.color=(.035,.035,.035)
scene.unit_settings.system='NONE'
scene['status']='CONDITIONAL / UNACCEPTED; low-resolution published GIF research candidate'
scene['source_state']='a16 frame027 dark tunnel; no per-camera geometry or lighting changes'
scene['unit_warning']='All coordinates are arbitrary proportional Blender units; NOT measured metres.'
scene['unseen_geometry']='Hidden backs, supports, full footprint and tunnel depth are inference, not observed.'
COLS={}
for name in ['00_STAGE','01_FRAME_TUNNEL','02_RED_WALLS','03_UPPER_ARC','04_WHITE_PIERS','05_RED_DISC','06_GIFTS','07_EDGE_DECOR','08_LIGHTS','09_CAMERAS']:
 c=bpy.data.collections.new(name); scene.collection.children.link(c); COLS[name]=c
records=[]
def record(o,group,source,inference):
 for c in list(o.users_collection): c.objects.unlink(o)
 COLS[group].objects.link(o); o['source']=source; o['inference']=inference
 records.append(dict(name=o.name,group=group,source=source,inference=inference)); return o

def mat(name,color,rough=.4,metal=0,emission=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission: p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
white=mat('porcelain warm white',(.86,.86,.82),.26)
framewhite=mat('white square frames',(.87,.87,.87),.2,0,.12)
framegrey=mat('outer frame cool silver',(.44,.49,.54),.28,.55)
red=mat('red lacquer wall',(.56,.008,.017),.35)
redgift=mat('scarlet gift boxes',(.57,.018,.025),.32)
disc=mat('deep crimson disc face',(.50,.009,.032),.52)
rib=mat('disc subtle radial ribs',(.67,.025,.045),.46)
black=mat('tunnel dark charcoal',(.006,.007,.012),.91)
glass=mat('upper dark glazing',(.017,.025,.043),.18,.25)
floor=mat('glossy pale finite stage',(.60,.66,.73),.22,.18)
leaf=mat('low red decor silhouette',(.34,.008,.017),.65)
clay=mat('WHITE_CHECK neutral',(.72,.72,.72),.65)
def finish(o,m,b=.02):
 if m:o.data.materials.append(m)
 if b:
  mod=o.modifiers.new('small physical edge bevel','BEVEL');mod.width=b;mod.segments=2
  mod=o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 return o

def cube(name,loc,scale,m,group,source,inference,b=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 finish(o,m,b);record(o,group,source,inference);return o

def mesh(name,verts,faces,m,group,source,inference,b=0):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);finish(o,m,b);record(o,group,source,inference);return o

def beam(name,a,b,width,depth,m,group,source,inference):
 a=Vector(a);b=Vector(b);o=cube(name,(a+b)/2,(width,depth,(b-a).length),m,group,source,inference,.008);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def slab(name,poly,y0,depth,m,group,source,inference):
 n=len(poly);vs=[(x,y,z) for y in [y0,y0+depth] for x,z in poly]
 fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,m,group,source,inference,.015)

src='a16 frame027; corroborated a15 frame110 and a16 frame107'
# Finite stage, not an infinite plane. Total plan edge inferred.
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=11.5,depth=.28,location=(0,0,-.14));o=bpy.context.object;o.name='finite pale stage slab';finish(o,floor,.05);record(o,'00_STAGE',src,'Visible white ground observed; full circular footprint, thickness and perimeter inferred.')
# Linear white outlines seen on floor, represented as finite surface inlays.
for i,(a,b) in enumerate([((-8,-3,.006),(0,4,.006)),((0,4,.006),(8,-3,.006)),((-8,-3,.006),(8,-3,.006))]):
 beam('floor white inlay %02d'%i,a,b,.023,.012,white,'00_STAGE','a16 027 / 107: pale angular floor lines','Exact endpoints and closed triangle continuity inferred; not a structural wall.')
# Red facade with a real aperture: no flat black occluder over a closed wall.
slab('central red upper lintel',[(-4.75,6.65),(4.75,6.65),(4.75,5.50),(2.9,5.50),(0,6.10),(-2.9,5.50),(-4.75,5.50)],5.85,.22,red,'02_RED_WALLS',src,'Unseen back thickness inferred; polygonal opening approximate.')
slab('central red left flank',[(-4.75,0),(-4.75,5.50),(-2.9,5.50),(-3.45,3.7),(-3.35,0)],5.85,.22,red,'02_RED_WALLS',src,'Opening silhouette and backing thickness approximate.')
slab('central red right flank',[(3.35,0),(3.45,3.7),(2.9,5.50),(4.75,5.50),(4.75,0)],5.85,.22,red,'02_RED_WALLS',src,'Opening silhouette and backing thickness approximate.')
# Twisted genuine open frames. Rotated square lower edges clipped to floor.
frame_defs=[(5.9,4.7,2.55,20,framegrey,.105),(5.25,4.95,2.47,-33,framewhite,.13),(4.85,6.2,2.48,14,framewhite,.075),(4.65,7.5,2.48,-8,framewhite,.068),(4.45,8.85,2.48,20,framewhite,.060),(4.25,10.2,2.48,-17,framewhite,.055),(4.05,11.5,2.48,12,framewhite,.05),(3.9,12.8,2.48,-10,framewhite,.045)]
frame_spec=[]
for k,(s,y,z,angle,m,w) in enumerate(frame_defs):
 a=math.radians(angle);pts=[]
 for x0,z0 in [(-s/2,-s/2),(s/2,-s/2),(s/2,s/2),(-s/2,s/2)]:pts.append(Vector((x0*math.cos(a)-z0*math.sin(a),y,z+x0*math.sin(a)+z0*math.cos(a))))
 for j in range(4):
  p=pts[j].copy();q=pts[(j+1)%4].copy()
  if max(p.z,q.z)<.02:continue
  if p.z<.02:p=p+(q-p)*((.02-p.z)/(q.z-p.z))
  if q.z<.02:q=q+(p-q)*((.02-q.z)/(p.z-q.z))
  beam('frame %02d edge %d'%(k+1,j+1),p,q,w,.14 if k<2 else .085,m,'01_FRAME_TUNNEL',src,'Frame sequence visible, but count, depth spacing, full obscured corners and static pose inferred. Floor-clipped finite beams; not texture.')
 frame_spec.append(dict(index=k+1,side=s,depth_y=y,center_z=z,rotation_degrees=angle))
# Tunnel side solids remain outside the open frames, not a closed box masquerading as a tunnel.
cube('tunnel left return',(-4.05,9.9,2.9),(.22,8.5,5.8),black,'01_FRAME_TUNNEL',src,'Dark occlusion seen; exact wall return inferred.')
cube('tunnel right return',(4.05,9.9,2.9),(.22,8.5,5.8),black,'01_FRAME_TUNNEL',src,'Dark occlusion seen; exact wall return inferred.')
cube('tunnel distant dark stop',(0,14.5,3),(8.3,.18,6),black,'01_FRAME_TUNNEL',src,'Unseen terminal depth and end wall are inferred, not source-observed.')
cube('tunnel upper dark return',(0,10,6),(8.3,9,.16),black,'01_FRAME_TUNNEL',src,'Hidden ceiling inferred for light control; not observed.')
# Curved band and glazing. Arc is partial; no invented complete closed roof.
def arc_band(name,r0,r1,z0,z1,t0,t1,m,group):
 steps=64;vs=[]
 for z in [z0,z1]:
  for r in [r0,r1]:
   for i in range(steps+1):
    a=math.radians(t0+(t1-t0)*i/steps);vs.append((r*math.sin(a),-4+r*math.cos(a),z))
 n=steps+1;fs=[]
 for i in range(steps):
  fs +=[(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),(i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)]
 fs +=[(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)]
 return mesh(name,vs,fs,m,group,'a16 frame027 upper arc, a15 frame110 partial arc','Visible arc curvature observed; radius, depth and full unseen extent inferred.',.014)
arc_band('white curved upper fascia',9.8,10.12,6.28,6.82,-76,76,white,'03_UPPER_ARC')
arc_band('upper curved dark glazing',9.94,9.98,6.83,10.0,-76,76,glass,'03_UPPER_ARC')
arc_band('upper narrow glazing rail',9.88,10.01,9.1,9.17,-76,76,framegrey,'03_UPPER_ARC')
for a in [-72,-54,-36,-18,0,18,36,54,72]:
 t=math.radians(a);x=9.94*math.sin(t);y=-4+9.94*math.cos(t)
 cube('glazing mullion %+03d'%a,(x,y,8.4),(.055,.075,3.15),framegrey,'03_UPPER_ARC','a16 frame027 dark upper glazed sectors','Mullion spacing/thickness and hidden heights inferred.')
for a in [-59,-29,29,59]:
 t=math.radians(a);x=9.9*math.sin(t);y=-4+9.9*math.cos(t)
 o=cube('white pier %+03d'%a,(x,y,3.15),(.70,.65,6.3),white,'04_WHITE_PIERS',src,'Vertical white piers observed; depth and exact cross-section inferred.');o.rotation_euler.z=-t
# Side red screens, with actual oval holes, set in front of dark returns.
for s in [-1,1]:
 o=cube(('left' if s<0 else 'right')+' red screen',(s*7.1,3.35,2.9),(2.75,.16,5.8),red,'02_RED_WALLS','a16 frame027 side red bays; a18 frame000 corroboration','Panel thickness and exact aperture shape inferred.',0)
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1,depth=1,location=(s*7.95,3.35,2.9),rotation=(math.pi/2,0,0));cut=bpy.context.object;cut.scale=(.98,2.0,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('true oval side opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);finish(o,None,.025)
 cube(('left' if s<0 else 'right')+' dark bay return',(s*7.1,4.25,3),(3.6,.2,6),black,'02_RED_WALLS','a16 frame027 dark side recesses','Depth and hidden return inferred.')
# Red disc, tilt inferred from ellipse. No invented pole/support.
center=Vector((3.80,3.30,1.05));normal=Vector((.0,-.80,.60)).normalized();u=Vector((1,0,0));v=normal.cross(u)
N=96;rad=1.22;vs=[]
for d in [-.035,.035]:
 for i in range(N):
  a=2*math.pi*i/N;vs.append(tuple(center+rad*(math.cos(a)*u+math.sin(a)*v)+normal*d))
fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
mesh('tilted crimson circular disc',vs,fs,disc,'05_RED_DISC',src,'Disc silhouette observed; umbrella interpretation, full diameter, angle and back inferred. No unseen handle added.',.012)
for k in range(24):
 a=k*2*math.pi/24;start=center+normal*.042;end=start+rad*.98*(math.cos(a)*u+math.sin(a)*v)
 beam('disc radial detail %02d'%k,start,end,.009,.008,rib,'05_RED_DISC','a16 frame107 faint radial structure','Low-resolution radial pattern suggests ribs; count/depth provisional.')
# Gift blocks and white bands.
def gift(name,loc,size):
 x,y,z=loc;w,d,h=size
 cube(name+' box',(x,y,z+h/2),(w,d,h),redgift,'06_GIFTS',src,'Red blocks and pale bands observed; individual sizes/backs inferred.')
 cube(name+' lid',(x,y,z+h+.025),(w*1.06,d*1.06,.065),redgift,'06_GIFTS',src,'Lid division provisional from low-resolution source.')
 for suff,dim in [('X band',(.07,d+.018,h+.08)),('Y band',(w+.018,.07,h+.08))]:cube(name+' '+suff,(x,y,z+h/2+.015),dim,white,'06_GIFTS',src,'Pale gift bands visible; underside wrap inferred.',.002)
 for k in [-1,1]:
  bpy.ops.curve.primitive_bezier_circle_add(radius=.14,location=(x+k*.09,y,z+h+.12),rotation=(math.pi/2,0,k*.3));o=bpy.context.object;o.name=name+' loop '+str(k);o.data.bevel_depth=.018;o.data.bevel_resolution=2;o.scale=(1,.65,1);o.data.materials.append(white);record(o,'06_GIFTS',src,'Bow interpretation provisional; low detail does not establish exact ribbon shape.')
for i,(loc,size) in enumerate([((5.35,3.4,0),(.55,.50,.60)),((5.95,3.50,0),(.48,.45,.78)),((6.32,3.22,0),(.34,.33,.46)),((-6.2,3.1,0),(.42,.46,.52)),((-8.6,1.4,0),(.62,.58,.63))]):gift('gift %02d'%i,loc,size)
# Low simplified red edge clusters. No false individual botanical reconstruction.
for j,(x,y) in enumerate([(-5.0,3.8),(-5.8,3.7),(5.05,3.8),(6.5,3.7),(-8.4,2.2),(8.6,2.2)]):
 for k in range(10):
  xx=x+random.uniform(-.4,.4);yy=y+random.uniform(-.22,.22);z=random.uniform(.08,.40)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(xx,yy,z));o=bpy.context.object;o.name='decor cluster %02d fragment %02d'%(j,k);o.scale=(random.uniform(.08,.19),random.uniform(.08,.18),random.uniform(.13,.33));o.data.materials.append(leaf);record(o,'07_EDGE_DECOR',src,'Only low red cluster silhouette observed; fragments deliberately abstract, species/leaves unknown.')
# Static lighting shared by every camera, never retuned per view.
def light(name,loc,power,color,size,target):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();record(o,'08_LIGHTS','a16 light appearance only','Light placement/power inferred, fixed across all source and check cameras.')
light('large neutral front key',(0,-4,8),1900,(1,.94,.9),7,(0,4,1.8))
light('soft left warm fill',(-7,-1,5),850,(1,.50,.54),4,(-2,4,2))
light('soft right cool fill',(7,-1,4),600,(.65,.67,1),4,(2,4,2))
light('upper facade wash',(0,2.5,7),850,(1,.80,.76),4,(0,6,3))
# Source cameras are estimates, not solved/calibrated. Same shared scene.
def camera(name,loc,target,lens=35,ortho=None):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_end=200;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 record(o,'09_CAMERAS','Estimated from source composition' if name.startswith('SRC') else 'Model-only diagnostic view','Camera pose and focal length inferred. No image registration or warping.');return o
camera('SRC_a16_f027',(0,-14,4.1),(0,5.0,3.25),29)
camera('SRC_a15_f110',(3.2,-8.7,3.0),(0,5,2.7),32)
camera('SRC_a16_f107',(-3.1,-6.3,4.4),(0,4.6,1.9),32)
camera('CHECK_front',(0,-14,4),(0,5,3),29)
camera('CHECK_left',(-12,-8,6),(0,5,2.8),34)
camera('CHECK_right',(12,-8,6),(0,5,2.8),34)
camera('CHECK_high',(9,-6,14),(0,5,2.5),34)
camera('CHECK_plan',(0,3,24),(0,3,0),35,26)
camera('CHECK_tunnel',(.4,4.4,2.9),(0,13,2.8),22)
camera('CHECK_rear',(0,22,8),(0,5,3),32)
camera('CHECK_disc_detail',(7,-2,3),(4.5,3.5,1),43)
scene.camera=bpy.data.objects['SRC_a16_f027']
# Named clay layer uses same object datablocks and camera, only material override.
layer=scene.view_layers[0];layer.name='MATERIAL'
wl=scene.view_layers.new('WHITE');wl.material_override=clay;wl.use=False
# Save source/camera parameter trace.
(ROOT/'qa'/f'{VERSION}_object_source_inference.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(ROOT/'qa'/f'{VERSION}_frame_parameters.json').write_text(json.dumps(frame_spec,indent=2))
(ROOT/'qa'/f'{VERSION}_cameras.json').write_text(json.dumps([dict(name=o.name,location=list(o.location),rotation_euler=list(o.rotation_euler),lens=o.data.lens,projection=o.data.type,ortho_scale=o.data.ortho_scale) for o in COLS['09_CAMERAS'].objects],indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models'/f'{VERSION}_twistframe_hall.blend'))
# Native Blender glTF exporter. Export baked evaluated meshes and cameras.
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models'/f'{VERSION}_twistframe_hall.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=True,export_extras=True)
print('R01_SAVED',len(records))
