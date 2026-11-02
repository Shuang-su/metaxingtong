"""Shared editable core from observed fixed module; all distances are model units.
No environment copied from CG; no claim of measured scale or source acceptance.
Run on this cloud computer only: blender -b -t 3 --python scripts/build_core_r01.py
"""
import bpy, bmesh, math, json, hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]; OUT=R/'stages/r01-core-white';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc['status']='CONDITIONAL CORE WHITE MODEL; NOT SOURCE ACCEPTED'
sc['scale']='MODEL UNITS ONLY; no measured metric scale'
sc['source_state']='Aug24 fixed module bridged to Aug16 preview structural angles; not a merged environment'
sc['missing']='Environment, final materials, calibrated source cameras, full assembly collision/raycast QA, later independent replay'
white=bpy.data.materials.new('WHITE_DIAGNOSTIC');white.diffuse_color=(.65,.7,.73,1);white.use_nodes=True
white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.7,.73,1)
white.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.62
def mesh(name,verts,faces,role,evidence='observed silhouette; hidden faces and dimensions inferred'):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);ob.data.materials.append(white)
    ob['stable_id']=name;ob['role']=role;ob['evidence']=evidence
    return ob
def annulus(name,ri,ro,z0,z1,role,center=(0,1),a0=0,a1=math.tau,n=128):
    full=abs(a1-a0-math.tau)<1e-5; count=n if full else n+1
    verts=[]
    for z,r in [(z0,ri),(z0,ro),(z1,ri),(z1,ro)]:
        for i in range(count):
            a=a0+(a1-a0)*i/n;verts.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),z))
    faces=[]
    for i in range(n):
        j=(i+1)%count
        faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    if not full:
        faces.extend([(0,count,3*count,2*count),(n,2*count+n,3*count+n,count+n)])
    return mesh(name,verts,faces,role)
def cylinder(name,r,z0,z1,role,center=(0,0),n=128):
    verts=[(center[0]+r*math.cos(math.tau*i/n),center[1]+r*math.sin(math.tau*i/n),z) for z in (z0,z1) for i in range(n)]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,role)
def rod(name,a,b,r,role,vertices=12):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();ob.data.materials.append(white)
    ob['stable_id']=name;ob['role']=role;ob['evidence']='support position/section inferred unless explicit appearance noted';return ob
def lathe(name,profile,role,center=(0,1),n=128):
    # Closed profile in radial/Z plane -> solid ring, not disconnected disks.
    verts=[(center[0]+r*math.cos(math.tau*i/n),center[1]+r*math.sin(math.tau*i/n),z) for r,z in profile for i in range(n)]
    faces=[]
    for j in range(len(profile)):
        k=(j+1)%len(profile)
        for i in range(n):
            q=(i+1)%n;faces.append((j*n+i,j*n+q,k*n+q,k*n+i))
    return mesh(name,verts,faces,role)
def curve_support(name,sign):
    pts=[Vector((.65,4.5)),Vector((.95,2.8)),Vector((2.0,1.3)),Vector((4.2,.75))];verts=[];n=64
    for i in range(n+1):
        t=i/n;c=(1-t)**3*pts[0]+3*(1-t)**2*t*pts[1]+3*(1-t)*t*t*pts[2]+t**3*pts[3]
        tangent=3*(1-t)**2*(pts[1]-pts[0])+6*(1-t)*t*(pts[2]-pts[1])+3*t*t*(pts[3]-pts[2])
        norm=Vector((-tangent.y,tangent.x)).normalized();w=.76*(1-t**5)+.08*t**5
        inside=c-norm*w/2;outside=c+norm*w/2
        if i==0: inside.y=outside.y=4.5
        if i==n: inside.y=outside.y=.75
        for y,p in [(.45,inside),(.45,outside),(1.55,inside),(1.55,outside)]:verts.append((sign*p.x,y,p.y))
    faces=[(0,2,3,1),(4*n,4*n+1,4*n+3,4*n+2)]
    for i in range(n):
        a=4*i;b=a+4;faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    return mesh(name,verts,faces,'primary curved support',
        'Two visible front curved supports confirmed in all five sources. Planar strip/depth/back/section inferred; no unobserved third/fourth leg invented.')
def chevron(name,x,y,sign):
    # Six-sided hollow concave frame. Opening is real topology, not black paint.
    outer=[(-.62,-.78),(.08,0),(-.62,.78),(.18,.78),(.88,0),(.18,-.78)]
    inner=[(-.27,-.59),(.27,0),(-.27,.59),(.10,.59),(.64,0),(.10,-.59)]
    verts=[]
    for yy,poly in [(y-.08,outer),(y-.08,inner),(y+.08,outer),(y+.08,inner)]:
        verts += [(x+sign*xx,yy,1.65+zz) for xx,zz in poly]
    faces=[]
    for i in range(6):
        j=(i+1)%6;faces.extend([(i,j,6+j,6+i),(12+i,18+i,18+j,12+j),(i,12+i,12+j,j),(6+i,6+j,18+j,18+i)])
    return mesh(name,verts,faces,'hollow side chevron frame','Three per side visible in preview; orientation and silhouette observed, exact spacing/thickness inferred')
# Stage core. Separate tier surfaces meet at Z boundaries, not coplanar overlapping shells.
cylinder('PLATFORM_MAIN',6.8,.25,.75,'circular performance platform')
cylinder('PLATFORM_BASE',7.0,0,.25,'under-stage base; thickness inferred')
annulus('PLATFORM_TOP_TRIM',6.8,6.85,.67,.75,'outer edge trim',center=(0,0))
for k,(ri,ro,z) in enumerate([(6.85,7.13,.50),(7.13,7.41,.25)]):
    annulus('STAIR_FRONT_%02d'%k,ri,ro,0,z,'front access step; caption-obscured exact layout inferred',center=(0,0),a0=math.radians(235),a1=math.radians(305),n=40)
for side,a0,a1 in [('L',math.radians(145),math.radians(235)),('R',math.radians(305),math.radians(395))]:
    annulus('OUTER_WING_'+side,7.1,8.1,0,.22,'side lower wing; partial silhouette inferred',center=(0,0),a0=a0,a1=a1,n=64)
curve_support('FRAME_L',-1);curve_support('FRAME_R',1)
lathe('CROWN_SAUCER',[(.20,4.5),(1.50,4.5),(1.85,4.56),(2.55,4.76),(2.65,4.92),(2.58,5.03),(.20,5.03)],'solid shallow annular canopy; central hidden opening inferred')
annulus('CROWN_LOWER_LIP',1.50,1.59,4.48,4.5,'lower recessed lip')
annulus('CROWN_EDGE_TRIM',2.65,2.69,4.87,4.93,'canopy outer trim')
annulus('CROWN_MID_DISPLAY_RING',2.94,3.04,5.25,5.48,'middle narrow display ring')
annulus('CROWN_OUTER_DISPLAY_RING',4.22,4.32,5.84,6.06,'large outer open display ring')
annulus('CROWN_TOP_DISPLAY_DRUM',2.15,2.25,6.42,7.12,'upper circular display band')
# Observed thin vertical central bars. Exact count and connections are not source-confirmed.
for i in range(24):
    a=math.tau*i/24;r=.67
    rod('CROWN_CENTRAL_BAR_%02d'%i,(r*math.cos(a),1+r*math.sin(a),5.03),(r*math.cos(a),1+r*math.sin(a),6.42),.018,'central vertical bar, instance count inferred',8)
# Explicit inferred structural ties, distinct from observed lighting elements.
for level,r,z in [('MID',2.94,5.35),('OUTER',4.22,5.95),('TOP',2.15,6.55)]:
    for i in range(4):
        a=math.pi/4+i*math.pi/2
        rod('INFERRED_TIE_%s_%d'%(level,i),(.67*math.cos(a),1+.67*math.sin(a),z),(r*math.cos(a),1+r*math.sin(a),z),.022,'inferred hidden radial tie; not source confirmed',8)
for side,sign in [('L',-1),('R',1)]:
    for i in range(3):
        x=sign*(3.12+i*.88);y=2.18+i*.28
        chevron('CHEVRON_%s_%02d'%(side,i+1),x,y,sign)
        for j,dx in enumerate([-.22,.22]):
            rod('INFERRED_CHEVRON_STAND_%s_%02d_%d'%(side,i+1,j),(x+dx,y,.75),(x+dx,y,.87),.035,'chevron foot/stand inferred',8)
# Visible perimeter rail behind performance region; gap at front preserved.
annulus('BACK_DISPLAY_RAIL',6.30,6.39,1.15,1.32,'back circular display rail',center=(0,0),a0=math.radians(0),a1=math.radians(180),n=100)
for i in range(17):
    a=math.pi*i/16;r=6.34
    rod('BACK_RAIL_POST_%02d'%i,(r*math.cos(a),r*math.sin(a),.75),(r*math.cos(a),r*math.sin(a),1.15),.026,'rear rail post; exact count inferred',8)
def camera(name,loc,target,lens=35):
    da=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,da);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();da.lens=lens;da.clip_end=300;return ob
camera('SOURCE_AUG24_FRONT_CONDITIONAL',(0,-12.7,2.5),(0,1.0,3.1),35)
camera('SOURCE_PREVIEW_FRONT_CONDITIONAL',(0,-21,5.8),(0,.6,3.4),37)
camera('SOURCE_PREVIEW_HIGH_CONDITIONAL',(0,-10.8,9.2),(0,.7,3.1),29)
camera('SOURCE_PREVIEW_WIDE_CONDITIONAL',(-10,-16,11),(0,0,3.0),34)
camera('SOURCE_PREVIEW_LOW_CONDITIONAL',(0,-8.2,1.4),(0,1,4.2),26)
for i in range(8):
    a=math.radians(-90+i*45)
    camera('CHECK_%02d_%03d'%(i+1,i*45),(19*math.cos(a),19*math.sin(a),10),(0,0,3.0),38)
camera('CHECK_TOP_DIAGNOSTIC',(0,0,24),(0,0,0),42)
sc.camera=bpy.data.objects['CHECK_02_045'];sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=16;sc.cycles.use_denoising=True
sc.render.resolution_x=640;sc.render.resolution_y=400;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('diagnostic_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.09,.12,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('KEY',(-7,-8,13),2000,8),('FILL',(9,-3,9),1400,7),('RIM',(0,8,11),2200,6)]:
    da=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,da);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler();da.energy=power;da.shape='DISK';da.size=size
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
meshes=[o for o in sc.objects if o.type=='MESH']
inventory=[{'id':o.name,'role':o.get('role'),'evidence':o.get('evidence'),'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in meshes]
(OUT/'object-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'harbor-core-r01-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'harbor-core-r01-white.glb'),export_format='GLB',export_cameras=True,export_lights=False,export_extras=True)
(OUT/'build-summary.json').write_text(json.dumps({'status':sc['status'],'mesh_objects':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'faces':sum(len(o.data.polygons) for o in meshes),'model_units':True,'back_support_count':'unknown; no third/fourth curved leg modeled','source_camera_alignment':'provisional, uncalibrated'},indent=2))
print('CORE_CHECKPOINT_READY',OUT,len(meshes))
