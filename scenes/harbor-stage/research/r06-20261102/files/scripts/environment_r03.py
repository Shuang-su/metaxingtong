# Executed inside build_core_r02 globals. Native mesh additions, not a generated image.
import random
random.seed(20261102)
def tag(ob,surface,scope='visible harbor accessory; position/back/scale inferred'):
    ob['surface']=surface;ob['environment_scope']=scope;return ob
def cube(name,loc,scale,surface,role):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(white);ob['stable_id']=name;ob['role']=role;ob['evidence']='visible appearance, hidden volume and placement inferred';return tag(ob,surface)
def sphere(name,loc,scale,surface,role,seg=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=loc);ob=bpy.context.object;ob.name=name;ob.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(white);ob['stable_id']=name;ob['role']=role;ob['evidence']='coarse visible silhouette, hidden geometry/placement inferred';return tag(ob,surface)
def poly_tube(name,points,radius,surface,role,n=8):
    vv=[];ff=[]
    for i,p in enumerate(points):
        p=Vector(p);d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)]);d.normalize();u=d.cross(Vector((0,0,1)))
        if u.length<.01:u=d.cross(Vector((0,1,0)))
        u.normalize();v=d.cross(u).normalized()
        for j in range(n):vv.append(p+radius*(math.cos(math.tau*j/n)*u+math.sin(math.tau*j/n)*v))
    ff=[tuple(reversed(range(n))),tuple(range((len(points)-1)*n,len(points)*n))]
    for i in range(len(points)-1):
        for j in range(n):k=(j+1)%n;ff.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    return tag(mesh(name,vv,ff,role),'%s'%surface)
def torus(name,loc,major,minor,surface,role,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=48,minor_segments=8,location=loc,rotation=rot);ob=bpy.context.object;ob.name=name;ob.data.materials.append(white);ob['stable_id']=name;ob['role']=role;ob['evidence']='visible circle; exact radius/section inferred';return tag(ob,surface)
# Flat, finite open-air ground/water; no invented walls or enclosed room.
shore=[(-20,-11),(20,-11),(19,6),(12,10),(7,11),(-9,11),(-18,7)]
sv=[(x,y,z) for z in (-.35,0) for x,y in shore];sn=len(shore);sf=[tuple(reversed(range(sn))),tuple(range(sn,2*sn))]+[(i,(i+1)%sn,(i+1)%sn+sn,i+sn) for i in range(sn)]
tag(mesh('ENV_SAND_ISLAND',sv,sf,'finite shoreline substrate; working outline inferred; rear boats excluded from land'),'sand')
tag(cylinder('ENV_SEA',120,-.55,-.36,'finite sea disk, displayed as ocean; extent is rendering bound',center=(0,20),n=128),'water')
tag(sphere('ENV_REAR_HILL',(24,37,2.0),(16,22,6.2),'hill','distant planted hill; coarse unmeasured envelope',48,20),'hill')
def palm(pid,x,y,h,leanx,leany,phase):
    # One closed continuous bent trunk, not stacked floating pieces.
    vv=[];ff=[];n=14;steps=18
    for i in range(steps+1):
        t=i/steps;r=.24*(1-.43*t);cx=x+leanx*t*t;cy=y+leany*t*t
        for j in range(n):a=math.tau*j/n;vv.append((cx+r*math.cos(a),cy+r*math.sin(a),h*t))
    ff=[tuple(reversed(range(n))),tuple(range(steps*n,(steps+1)*n))]
    for i in range(steps):
        for j in range(n):k=(j+1)%n;ff.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    tag(mesh(pid+'_TRUNK',vv,ff,'bent palm trunk; trunk count selected from visible foreground cluster'),'bark')
    top=Vector((x+leanx,y+leany,h));
    for leaf in range(9):
        a=phase+math.tau*leaf/9;direction=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0));L=2.3+.5*math.sin(leaf*2.1);verts=[];faces=[];N=18
        for i in range(N+1):
            t=i/N;c=top+direction*(L*t)+Vector((0,0,.62*math.sin(math.pi*t)-1.4*t*t));w=max(.008,.63*math.sin(math.pi*t)**.65*(.88+.12*math.cos(14*math.pi*t)))
            for dz,sgn in [(-.015,-1),(-.015,1),(.015,-1),(.015,1)]:verts.append(c+side*(w*sgn)+Vector((0,0,dz)))
        faces=[(0,2,3,1),(4*N,4*N+1,4*N+3,4*N+2)]
        for i in range(N):a0=i*4;b=a0+4;faces.extend([(a0,b,b+1,a0+1),(a0+2,a0+3,b+3,b+2),(a0,a0+2,b+2,b),(a0+1,b+1,b+3,a0+3)])
        tag(mesh(pid+'_LEAF_%02d'%leaf,verts,faces,'solid stylized palm leaf; exact frond count inferred'),'leaf')
    for i in range(3):
        a=phase+i*2.1;sphere(pid+'_COCONUT_%d'%i,top+Vector((.2*math.cos(a),.2*math.sin(a),-.18)),(.22,.22,.27),'bark','coconut/branch joint; biological intersection intentional',16,8)
for p in [('PALM_L1',-10,2,7.1,1.2,.2,.2),('PALM_L2',-11.7,6,6.2,.6,.5,1.0),('PALM_L3',-7,9,6.9,-1.4,-.3,.5),('PALM_R1',10,2.6,7.3,-1.3,.2,1.2),('PALM_R2',8.2,8.7,6.1,.9,-.4,.7),('PALM_R3',12,6.5,4.3,-.5,0,2.0)]:palm(*p)
# Lighthouse on a separate rear island, geometry inferred from preview silhouette.
tag(cylinder('LIGHTHOUSE_ISLET',3.4,-.36,0,'lighthouse ground',center=(13,25),n=48),'sand')
tag(cylinder('LIGHTHOUSE_TOWER',.75,0,11.8,'lighthouse tower envelope; no unseen interior modeled',center=(13,25),n=64),'tower')
for i,z in enumerate([2.7,6.1,9.5]):tag(annulus('LIGHTHOUSE_DARK_BAND_%d'%i,.75,.755,z,z+1.2,'surface stripe, not a void',center=(13,25),n=64),'navy')
tag(annulus('LIGHTHOUSE_GALLERY',.74,1.12,11.8,11.95,'lighthouse balcony platform',center=(13,25),n=64),'metal')
tag(cylinder('LIGHTHOUSE_LANTERN_BASE',.66,11.95,12.05,'lantern base',center=(13,25),n=32),'navy')
tag(annulus('LIGHTHOUSE_GLASS',.61,.66,12.05,13.05,'finite-thickness lantern glazing',center=(13,25),n=32),'glass')
tag(lathe('LIGHTHOUSE_ROOF',[(.01,13.45),(.82,13.08),(.82,13.02),(.01,13.02)],'lantern roof',center=(13,25),n=32),'navy')
for i in range(16):
    a=math.tau*i/16;tag(rod('LIGHTHOUSE_RAIL_POST_%02d'%i,(13+1.04*math.cos(a),25+1.04*math.sin(a),11.95),(13+1.04*math.cos(a),25+1.04*math.sin(a),12.5),.02,'balcony rail post'),'metal')
tag(torus('LIGHTHOUSE_HANDRAIL',(13,25,12.5),1.04,.023,'metal','balcony handrail'),'metal')
def hull(name,cx,cy,L,W):
    poly=[(-L*.5,0),(-L*.34,-W*.5),(L*.32,-W*.5),(L*.5,0),(L*.32,W*.5),(-L*.34,W*.5)]
    vv=[(cx+x*s,cy+y*s,z) for s,z in [(.72,-.48),(1,.38)] for x,y in poly];ff=[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)];return tag(mesh(name,vv,ff,'background boat hull; volume/position inferred'),'boat')
hull('YACHT_HULL',-5.2,17,7.0,2.0)
cube('YACHT_CABIN',(-5.5,17,.85),(4.2,1.5,.95),'boat','yacht cabin outer envelope')
cube('YACHT_WINDOW_FRONT',(-5.5,16.237,1.0),(3.8,.026,.5),'glass','glazing panel; not a painted opening')
cube('YACHT_ROOF',(-5.55,17,1.37),(4.6,1.7,.12),'boat','yacht roof')
tag(rod('YACHT_ANTENNA',(-4.4,17,1.43),(-4.4,17,2.5),.025,'antenna'),'metal')
hull('SAILBOAT_HULL',4.1,19,4.1,1.4)
tag(rod('SAILBOAT_MAST',(4.1,19,.38),(4.1,19,7.7),.045,'sailboat mast'),'metal')
vv=[(x,y,z) for y in (18.98,19.02) for x,z in [(4.15,.65),(4.15,7.5),(6.85,.65)]]
tag(mesh('SAILBOAT_MAINSAIL',vv,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'finite-thickness triangular sail; shape inferred from visible silhouette'),'sail')
def umbrella(uid,x,y,surface):
    tag(rod(uid+'_POLE',(x,y,0),(x,y,3.2),.04,'beach parasol pole'),'metal')
    vv=[];n=32
    for r,z in [(.015,3.3),(1.35,2.75),(1.35,2.71),(.015,3.26)]:
        for i in range(n):a=math.tau*i/n;vv.append((x+r*math.cos(a),y+r*math.sin(a),z+.07*math.cos(a*8)*(r/1.35)))
    ff=[]
    for j in range(4):
        for i in range(n):k=(i+1)%n;ff.append((j*n+i,j*n+k,((j+1)%4)*n+k,((j+1)%4)*n+i))
    ob=tag(mesh(uid+'_CANOPY',vv,ff,'closed parasol canopy, alternating material sectors'),'umbrella_'+surface)
umbrella('UMBRELLA_L',-6.7,8,'purple');umbrella('UMBRELLA_R',6.9,8,'pink')
# Foreground platform lights and the circle pads visible in preview.
for side,sign in [('L',-1),('R',1)]:
    tag(cylinder('CIRCLE_PAD_'+side,.70,.75,.84,'circular stage emitter base',center=(sign*5.5,-2.2),n=48),'metal')
    torus('CIRCLE_PAD_LIGHT_'+side,(sign*5.5,-2.2,.855),.55,.022,'emission','circular pad rim')
for i in range(40):
    a=math.tau*i/40;r=6.55;x,y=r*math.cos(a),r*math.sin(a)
    tag(cylinder('STAGE_SPOT_BASE_%02d'%i,.09,.75,.84,'perimeter stage spotlight base; exact count inferred',center=(x,y),n=12),'navy')
    tag(cylinder('STAGE_SPOT_BODY_%02d'%i,.065,.84,1.04,'spotlight body simplified, exact yoke pending',center=(x,y),n=12),'metal')
    tag(cylinder('STAGE_SPOT_LENS_%02d'%i,.052,1.04,1.045,'spotlight lens',center=(x,y),n=12),'emission')
for i in range(40):
    a=math.tau*i/40;r=4.26;x,y=r*math.cos(a),1+r*math.sin(a)
    tag(cylinder('OVERHEAD_SPOT_%02d'%i,.035,5.70,5.84,'hanging ring light, count inferred',center=(x,y),n=8),'navy')
# Continuous front edge LEDs and true internal chevron light tubes.
for side in ['L','R']:
    ob=bpy.data.objects['FRAME_'+side]
    for edge,idx in [('INNER',0),('OUTER',1)]:
        pts=[(ob.data.vertices[i*4+idx].co.x,.425,ob.data.vertices[i*4+idx].co.z) for i in range(65)]
        poly_tube('FRAME_%s_EDGE_%s'%(side,edge),pts,.025,'emission','edge light bonded to band front face')
for side,sign in [('L',-1),('R',1)]:
    for i in range(3):
        x=sign*(3.12+i*.88);y=2.18+i*.28
        poly_tube('CHEVRON_LIGHT_%s_%02d'%(side,i+1),[(x-sign*.14,y,2.245),(x+sign*.45,y,1.65),(x-sign*.14,y,1.055)],.045,'emission','internal chevron luminous tube; top/bottom attached to frame')
        torus('CHEVRON_RING_%s_%02d'%(side,i+1),(x,y+.13,2.7),.19,.025,'chrome','visible circular insert / effect, support uncertain',rot=(math.pi/2,0,0))
# Surfboards and right-side neon jukebox-like silhouettes: observed in actual4K companion.
for i,(x,y,c) in enumerate([(-10,7,'teal'),(-9.1,7.8,'purple'),(11,9,'pink')]):
    ob=sphere('SURFBOARD_%d'%i,(x,y,1.35),(.36,.07,1.35),c,'beach surfboard, placement inferred',32,16);ob.rotation_euler[1]=.18
for i,(x,y,h) in enumerate([(10.4,5.7,2.6),(12.2,6.1,1.9)]):
    cube('NEON_PROP_BODY_%d'%i,(x,y,h*.43),(.95,.35,h*.86),'navy','jukebox-like prop body, exact controls unknown')
    pts=[(x-.52,y-.20,0),(x-.52,y-.20,h-.52)]+[(x+.52*math.cos(math.pi-j*math.pi/16),y-.20,h-.52+.52*math.sin(math.pi-j*math.pi/16)) for j in range(17)]+[(x+.52,y-.20,0)]
    poly_tube('NEON_PROP_ARCH_%d'%i,pts,.028,'pink_emission','neon arched outline seen in companion actual4K')
