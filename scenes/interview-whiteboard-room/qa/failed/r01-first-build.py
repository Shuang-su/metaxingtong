"""Run: blender -b -t 8 -P scripts/build_scene.py -- [--preview]
All cameras share one immutable set of meshes/materials/lights. No camera-driven visibility.
"""
import bpy, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
PREVIEW='--preview' in sys.argv
cfg=json.loads((ROOT/'docs/camera-fit.json').read_text()); g=cfg['geometry']
OUT=ROOT/'models/r01'; QA=ROOT/'qa/r01'; OUT.mkdir(parents=True,exist_ok=True); QA.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials,bpy.data.meshes,bpy.data.cameras,bpy.data.lights):
    for d in list(datablocks):
        if d.users==0: datablocks.remove(d)
s=bpy.context.scene
s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=24
s.cycles.use_denoising=False; s.cycles.use_adaptive_sampling=True
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.image_settings.color_mode='RGB'
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast' if False else 'None'
s.view_settings.exposure=0;s.view_settings.gamma=1
s.world.color=(.05,.05,.05)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.57,.60,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
s.unit_settings.system='NONE'
s['status']='RECONSTRUCTION CANDIDATE — NOT SOURCE ACCEPTED'
s['units']='model units; board outer width2.06; no metric/character scale'
s['inferred_shell']='front closure/ceiling/wall thickness unknown; finite model assumption only'
manifest=[]

def material(name,color,rough=.6,metal=0,texture=None):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if texture:
        im=bpy.data.images.load(str(ROOT/'textures'/texture),check_existing=True)
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
        m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
        im.pack()
    return m
wall=material('WALL warm gray plaster observed hue / inferred response',(.48,.475,.44),.88)
floor=material('FLOOR dark gray observed / inferred response',(.065,.063,.057),.72)
skirt=material('SKIRT charcoal satin',(.034,.033,.030),.5)
black=material('BOARD black painted metal',(.025,.025,.023),.36,.45)
metal=material('TABLE gray coated metal',(.25,.26,.245),.40,.38)
rubber=material('rubber inferred feet',(.014,.014,.013),.82)
cloth=material('CHAIR black upholstered fabric',(.026,.025,.024),.9)
wood=material('TABLE inferred wood grain',(.5,.35,.2),.47,0,'wood-inferred.png')
board=material('BOARD photographed front text / baked light retained',(.8,.8,.8),.72,0,'whiteboard-source-plane.png')
rearboard=material('BOARD inferred plain reverse',(.55,.54,.50),.7)
white=material('WHITE MODEL same geometry',(.72,.72,.72),.8)

def tag(o,id,evidence,notes):
    o['stable_id']=id;o['evidence']=evidence;o['notes']=notes
    o['source']='BV14ioLBAEDt 1283.813032 / 1505.632497'
    manifest.append({'object':o.name,'id':id,'evidence':evidence,'notes':notes})
    return o
def cube(name,loc,dim,mat,id,evidence='mixed',notes='',bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('physical rounded edges','BEVEL');mod.width=bevel;mod.segments=3
        mod=o.modifiers.new('weighted corner normals','WEIGHTED_NORMAL')
    return tag(o,id,evidence,notes)
def rod(name,a,b,width,mat,id,evidence='inferred',notes='',rect=None):
    a,b=Vector(a),Vector(b);d=b-a
    o=cube(name,(a+b)/2,(width,width,d.length) if rect is None else (*rect,d.length),mat,id,evidence,notes,.003)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def cyl(name,loc,r,depth,mat,id,axis='X',evidence='mixed',notes=''):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc)
    o=bpy.context.object;o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    o.data.materials.append(mat)
    mod=o.modifiers.new('rim bevel','BEVEL');mod.width=.003;mod.segments=2
    for p in o.data.polygons:p.use_smooth=True
    return tag(o,id,evidence,notes)

# Finite complete shell. No door or opening invented. Source-facing wall corners observed;
# all invisible closure extent explicitly inferred. Camera always inside, no cutaway.
wh=g['wall_half'];wy=g['wall_y'];ry=g['return_y'];H=2.8;front=-6.8;t=.12
cube('ROOM.floor',(0,(wy+front)/2,-.06),(2*(wh+.4),wy-front,.12),floor,'ROOM-FLOOR','observed surface / inferred thickness','No real unit scale')
cube('ROOM.ceiling_INFERRED',(0,(wy+front)/2,H+.06),(2*(wh+.4),wy-front,.12),wall,'ROOM-CEILING','inferred','Not visible in either source')
cube('ROOM.rear-wall',(0,wy+t/2,H/2),(2*wh,t,H),wall,'ROOM-REAR','observed front surface / inferred thickness','Rear of interview nook, not building rear')
cube('ROOM.right-wall',(wh+t/2,(wy+front)/2,H/2),(t,wy-front,H),wall,'ROOM-RIGHT','mixed','Front extension unobserved')
cube('ROOM.left-return',(-wh-t/2,(wy+ry)/2,H/2),(t,wy-ry,H),wall,'ROOM-LEFT-RETURN','observed front surface / inferred thickness','Visible short return at left corner')
cube('ROOM.left-projecting-face',(-wh-.2,ry-t/2,H/2),(.4,t,H),wall,'ROOM-LEFT-FACE','mixed','Projection face partly visible; outer extent inferred')
cube('ROOM.left-side_INFERRED',(-wh-.4-t/2,(ry+front)/2,H/2),(t,ry-front,H),wall,'ROOM-LEFT-CLOSURE','inferred','Unseen continuation')
cube('ROOM.front-wall_INFERRED',(-.2,front-t/2,H/2),(2*wh+.4,t,H),wall,'ROOM-FRONT-CLOSURE','inferred','Closed shell hypothesis; no evidence of door')
cube('SKIRT.rear',(0,wy-.012,.07),(2*wh,.024,.14),skirt,'SKIRT-REAR','observed silhouette / inferred profile',bevel=.004)
cube('SKIRT.right',(wh-.012,(wy+front)/2,.07),(.024,wy-front,.14),skirt,'SKIRT-RIGHT','mixed',bevel=.004)
cube('SKIRT.left-return',(-wh+.012,(wy+ry)/2,.07),(.024,wy-ry,.14),skirt,'SKIRT-LEFT-RETURN','observed silhouette / inferred profile',bevel=.004)
cube('SKIRT.left-face',(-wh-.2,ry-.012,.07),(.4,.024,.14),skirt,'SKIRT-LEFT-FACE','mixed',bevel=.004)
cube('SKIRT.left-closure',(-wh-.4+.012,(ry+front)/2,.07),(.024,ry-front,.14),skirt,'SKIRT-LEFT-CLOSURE','inferred',bevel=.004)
cube('SKIRT.front-closure',(-.2,front+.012,.07),(2*wh+.4,.024,.14),skirt,'SKIRT-FRONT-CLOSURE','inferred',bevel=.004)

# Rounded frame: true connected ring, physical depth; front plane at y=0.
bb=g['board_bottom'];bh=g['board_height'];bc=bb+bh/2
def rounded_loop(w,h,r,n=8):
    pts=[]
    for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(n+1):
            a=math.radians(start+i*90/n);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
    return pts
outer=rounded_loop(2.06,bh,.055);inner=rounded_loop(2.002,bh-.058,.026);N=len(outer)
verts=[(x,y,z+bc) for y,loop in [(-.015,outer),(-.015,inner),(.045,outer),(.045,inner)] for x,z in loop]
faces=[]
for i in range(N):
    j=(i+1)%N
    faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
me=bpy.data.meshes.new('rounded_frame_mesh');me.from_pydata(verts,[],faces);me.update()
o=bpy.data.objects.new('BOARD.physical-rounded-frame',me);s.collection.objects.link(o);o.data.materials.append(black)
tag(o,'BOARD-FRAME','observed silhouette / inferred section','True rounded ring, no black texture pretending hole')
cube('BOARD.sandwich-core',(0,.028,bc),(2.012,.044,bh-.048),rearboard,'BOARD-CORE','inferred','Sandwich thickness and reverse not observed',.018)
# textured plane, exact UV. Not a background billboard: bounded within solid board.
w=2.000;hh=bh-.060
me=bpy.data.meshes.new('source_text_plane');me.from_pydata([(-w/2,-.0005,bc-hh/2),(w/2,-.0005,bc-hh/2),(w/2,-.0005,bc+hh/2),(-w/2,-.0005,bc+hh/2)],[],[(0,1,2,3)]);me.update()
uv=me.uv_layers.new(name='source_sheet_UV')
for i,v in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=v
o=bpy.data.objects.new('BOARD.source-text-face',me);s.collection.objects.link(o);o.data.materials.append(board)
tag(o,'BOARD-TEXT','observed planar source / inferred reflectance','Non-solid decal plane, photograph includes original illumination; no character pixels')
for side,x in [('L',-1.065),('R',1.065)]:
    cube('BOARD.upright-'+side,(x,.045,(bc+.045)/2),(.032,.04,bc-.045),black,'BOARD-UPRIGHT-'+side,'mixed','Visible upper portion; bottom extension and support junction inferred',.004)
    cyl('BOARD.pivot-'+side,(x,.012,bc+.015),.035,.050,black,'BOARD-PIVOT-'+side,evidence='observed silhouette / inferred section')
    cyl('BOARD.pivot-screw-'+side,(x+(-.036 if x<0 else .036),.012,bc+.015),.016,.025,metal,'BOARD-SCREW-'+side,evidence='mixed')
    # T feet; completely occluded support hypothesis, stable ground contact.
    cube('BOARD.foot-'+side,(x,.035,.035),(.055,.52,.055),black,'BOARD-FOOT-'+side,'inferred','No source view confirms foot layout; no casters invented',.012)
    for k,y in enumerate([-.19,.26]):
        cube('BOARD.foot-pad-'+side+str(k),(x,y,.008),(.06,.065,.016),rubber,'BOARD-PAD-'+side+str(k),'inferred','Ground-contact pads',.005)
    cube('BOARD.rail-clamp-'+side,(x,-.005,bb-.145),(.046,.064,.055),black,'BOARD-CLAMP-'+side,'mixed','Upper clamp visible; section inferred',.006)
cube('BOARD.cross-rail',(0,.025,bb-.145),(2.10,.037,.028),black,'BOARD-CROSS-RAIL','observed upper edge / inferred depth',bevel=.003)
cube('BOARD.marker-tray-left',(-.68,-.025,bb-.145),(.71,.075,.025),metal,'BOARD-TRAY','observed left segment / inferred depth','Do not model large shadow below board as solid tray',.003)

# Single table with true four-legged frame and open knee space.
tx=g['table_x'];ty=g['table_y'];tw=g['table_width'];td=g['table_depth'];tz=g['table_z'];th=.028
cube('TABLE.wood-top',(tx,ty,tz-th/2),(tw,td,th),wood,'TABLE-TOP','observed outline / inferred grain and depth',bevel=.003)
for side,x in [('L',tx-tw/2+.065),('R',tx+tw/2-.065)]:
    for k,y in [('F',ty-td/2+.052),('B',ty+td/2-.052)]:
        cube('TABLE.leg-'+side+k,(x,y,(tz-th-.01)/2+.01),(.043,.043,tz-th-.01),metal,'TABLE-LEG-'+side+k,'mixed','Visible/occluded portions separate; square section inferred',.002)
        cube('TABLE.pad-'+side+k,(x,y,.006),(.045,.045,.012),rubber,'TABLE-PAD-'+side+k,'inferred','Ground pads',.002)
for k,y in [('F',ty-td/2+.052),('B',ty+td/2-.052)]:
    cube('TABLE.apron-'+k,(tx,y,tz-th-.018),(tw-.09,.035,.036),metal,'TABLE-APRON-'+k,'mixed','Front rail visible, rear inferred',.002)
for k,x in [('L',tx-tw/2+.065),('R',tx+tw/2-.065)]:
    cube('TABLE.side-apron-'+k,(x,ty,tz-th-.018),(.035,td-.08,.036),metal,'TABLE-SIDE-APRON-'+k,'inferred',bevel=.002)

# Black armless chair, seat/back cushions with modeled volume and metal open support.
cx=-.025;cy=-.22;seat=.40
cube('CHAIR.seat-cushion',(cx,cy,seat),(.52,.46,.090),cloth,'CHAIR-SEAT','observed front contour / inferred depth','Upholstery volume, not flat card',.075)
back=cube('CHAIR.back-cushion',(cx,cy+.23,.648),(.49,.075,.34),cloth,'CHAIR-BACK','partly observed / inferred hidden profile','Back upper arc seen behind table; lower region occluded',.08)
back.rotation_euler[0]=math.radians(-7)
for side,x in [('L',cx-.235),('R',cx+.235)]:
    rod('CHAIR.front-leg-'+side,(x+(-.035 if side=='L' else .035),cy-.225,.009),(x,cy-.18,seat-.028),.025,black,'CHAIR-FRONT-LEG-'+side,'mixed','Front leg silhouettes visible; exact section inferred')
    rod('CHAIR.rear-leg-'+side,(x+(-.015 if side=='L' else .015),cy+.27,.009),(x,cy+.16,seat-.03),.025,black,'CHAIR-REAR-LEG-'+side,'inferred','Occluded rear leg')
    rod('CHAIR.back-post-'+side,(x,cy+.16,seat-.03),(x,cy+.255,.72),.022,black,'CHAIR-BACK-POST-'+side,'inferred','Rear backing support')
    rod('CHAIR.side-stretcher-'+side,(x,cy-.18,.32),(x,cy+.16,.32),.025,black,'CHAIR-SIDE-RAIL-'+side,'inferred','Seat supporting frame')
rod('CHAIR.front-crossrail',(cx-.24,cy-.18,.32),(cx+.24,cy-.18,.32),.022,black,'CHAIR-FRONT-RAIL','mixed')

def area(name,loc,target,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('LIGHT shared broad frontal',(0,-3.2,2.5),(0,0,1),210,4)
area('LIGHT shared ceiling soft',(-.8,-.8,2.60),(0,0,0),75,2.5)

def camera_from_params(name,params):
    x,y,z,yaw,pitch,roll,f=params
    fw=Vector((math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
    rt=Vector((math.cos(yaw),-math.sin(yaw),0));up=rt.cross(fw)
    r=rt*math.cos(roll)+up*math.sin(roll);u=-rt*math.sin(roll)+up*math.cos(roll)
    d=bpy.data.cameras.new(name);d.lens=f*36/1920;d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.clip_start=.02;d.clip_end=200
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=(x,y,z);o.rotation_euler=Matrix((r,u,-fw)).transposed().to_euler()
    o['calibration']='conditional source fit, not accepted';return o
frontcam=camera_from_params('SOURCE front 1283.813032',cfg['front'])
obcam=camera_from_params('SOURCE oblique 1505.632497',cfg['oblique'])
def checkcam(name,loc,target,lens=24):
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.015
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
checks=[
    checkcam('CHECK01 left overview',(-2,-3,1.8),(0,-.3,.9),24),
    checkcam('CHECK02 right overview',(2,-3,1.8),(0,-.3,.9),24),
    checkcam('CHECK03 high interior',(.3,-2.6,2.55),(0,-.25,.6),22),
    checkcam('CHECK04 low support',(1.9,-2,.3),(0,-.15,.4),25),
    checkcam('CHECK05 board rear',(1.8,.44,1.7),(0,0,1.35),20),
    checkcam('CHECK06 left floor',(-1.8,-1.2,.28),(0,0,.15),20),
    checkcam('CHECK07 front closure',(0,-.2,2.1),(0,-5.5,1.2),18),
    checkcam('CHECK08 overhead interior',(-.1,-.35,2.68),(0,-.5,.1),15),
    checkcam('CHECK09 right joint',(1.75,-.25,1.05),(.9,0,1.1),30)]
def render(cam,path,res=(1920,1080),samples=24):
    s.camera=cam;s.render.resolution_x,s.render.resolution_y=res;s.cycles.samples=samples;s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)

(ROOT/'docs/object-provenance-r01.json').write_text(json.dumps({'status':'candidate','objects':manifest,'dynamic_person':'excluded, original source remains unchanged','closure':'finite inferred shell, all views shared'},indent=2))
# Geometry hash material-independent; object transforms included.
def signature():
    rows=[]
    for o in sorted([o for o in s.objects if o.type=='MESH'],key=lambda x:x.name):
        rows.append((o.name,[round(x,7) for row in o.matrix_world for x in row],[[round(c,7) for c in v.co] for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
bpy.context.view_layer.update(); sig=signature()
s.camera=frontcam
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'interview-room-material.blend'))
if PREVIEW:
    render(frontcam,QA/'front-preview.png',(960,540),12)
    render(obcam,QA/'oblique-preview.png',(960,540),12)
    print('PREVIEW_COMPLETE');sys.exit(0)

render(frontcam,QA/'source-front-render.png',samples=40)
render(obcam,QA/'source-oblique-render.png',samples=40)
for idx,cam in enumerate(checks,1):render(cam,QA/f'check-{idx:02d}.png',(1280,720),20)
s.camera=frontcam;s.render.resolution_x=1920;s.render.resolution_y=1080
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'interview-room-material.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'interview-room-material.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_extras=True)
for o in s.objects:
    if o.type=='MESH':
        o.data.materials.clear();o.data.materials.append(white)
bpy.context.view_layer.update(); wsig=signature()
assert sig==wsig, 'White/material geometry mismatch'
render(frontcam,QA/'source-front-white.png',samples=24)
render(obcam,QA/'source-oblique-white.png',samples=24)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'interview-room-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'interview-room-white.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_extras=True)
(QA/'geometry-equivalence.json').write_text(json.dumps({'material_hash':sig,'white_hash':wsig,'same_base_geometry_and_transforms':sig==wsig,'mesh_objects':sum(o.type=='MESH' for o in s.objects),'limitations':'signature covers base meshes/transforms; evaluated GLB checked independently'},indent=2))
print('BUILD_COMPLETE',sig)
