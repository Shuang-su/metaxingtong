"""Finite campus courtyard; all cameras share this mesh/state. Blender 4.3.
No camera-dependent object visibility, geometry deformation or scene photograph.
Model units only. Parts and hidden extensions remain provisional.
"""
import bpy, math, json, random, sys, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
stage=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'blockout'
OUT=R/('stage-01-blockout' if stage=='blockout' else 'stage-02-material-candidate')
OUT.mkdir(exist_ok=True)
random.seed(42)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
M=[]
def material(name,color,rough=.65,metal=0,texture=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if texture:
        n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(R/'textures'/texture));n.image.pack();m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
    M.append(m);return len(M)-1
plaster=material('Plaster warm cool grey',(.67,.69,.68))
trim=material('Concrete limestone curb',(.54,.56,.55))
glass=material('Blue grey glazing opaque environment approximation',(.12,.22,.29),.28,.15)
frame=material('Bronze brown window frames',(.25,.17,.105),.5,.25)
dark=material('Recess dark interior inferred',(.08,.10,.10))
red=material('Terracotta track rubber',(.52,.105,.055),.88)
line=material('Warm white sport markings',(.84,.84,.73))
green=material('Green playing surface',(.035,.35,.19),.88)
cyan=material('Blue green court',(.04,.44,.43),.8)
metal=material('Dark painted metal',(.065,.075,.07),.4,.65)
rust=material('Stair warm brown painted steel',(.35,.15,.065),.48,.5)
wood=material('Bench slat orange timber',(.48,.22,.065),.55)
net=material('Net cord ivory',(.67,.70,.62))
soil=material('Soil',(.09,.065,.035))
grass=material('Lawn',(.13,.23,.045))
bark=material('Tree bark',(.23,.16,.10),.9,texture='bark.png' if stage!='blockout' else None)
leafs=[material('Foliage '+str(i),c) for i,c in enumerate([(.12,.25,.045),(.23,.33,.065),(.32,.38,.08),(.11,.22,.07),(.46,.24,.13)])]
flower=material('Flower muted coral',(.65,.20,.22))
ball=material('Basketball orange',(.60,.15,.035),.7)
paving=material('Paver grid UV tile',(.53,.55,.56),.85,texture='pavers.png' if stage!='blockout' else None)
white=material('Diagnostic neutral clay',(.68,.70,.72),.8)
lampmat=material('Lamp diffuser',(.95,.92,.70),.4)
p=M[lampmat].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.8,.48,1);p.inputs['Emission Strength'].default_value=.7

class Assembly:
    def __init__(self,id,kind,sources,observed,inferred):
        self.id=id;self.kind=kind;self.sources=sources;self.observed=observed;self.inferred=inferred;self.v=[];self.f=[];self.mi=[];self.smooth=[]
    def geom(self,verts,faces,mat,smooth=False):
        n=len(self.v);self.v.extend(verts);self.f.extend([tuple(n+i for i in f) for f in faces]);self.mi.extend([mat]*len(faces));self.smooth.extend([smooth]*len(faces))
    def box(self,c,d,mat,rot=0):
        co=math.cos(rot);si=math.sin(rot);vs=[]
        for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            x*=d[0]/2;y*=d[1]/2;vs.append((c[0]+x*co-y*si,c[1]+x*si+y*co,c[2]+z*d[2]/2))
        self.geom(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
    def tube(self,a,b,r,mat,r2=None,n=10):
        a=Vector(a);b=Vector(b);w=(b-a).normalized();u=w.cross(Vector((0,0,1)))
        if u.length<.1:u=w.cross(Vector((1,0,0)))
        u.normalize();v=w.cross(u);r2=r if r2 is None else r2
        vs=[tuple(c+rr*(math.cos(i*2*math.pi/n)*u+math.sin(i*2*math.pi/n)*v)) for c,rr in [(a,r),(b,r2)] for i in range(n)]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        self.geom(vs,fs,mat,True)
    def path(self,pts,r,mat,n=8):
        for a,b in zip(pts,pts[1:]):self.tube(a,b,r,mat,n=n)
    def sphere(self,c,s,mat,n=8,k=5):
        vs=[(c[0],c[1],c[2]+s[2])]
        for j in range(1,k):
            t=math.pi*j/k
            for i in range(n):
                p=2*math.pi*i/n;vs.append((c[0]+s[0]*math.sin(t)*math.cos(p),c[1]+s[1]*math.sin(t)*math.sin(p),c[2]+s[2]*math.cos(t)))
        vs.append((c[0],c[1],c[2]-s[2]));bot=len(vs)-1
        fs=[(0,1+i,1+(i+1)%n) for i in range(n)]
        for j in range(k-2):
            for i in range(n):
                a=1+j*n+i;b=1+j*n+(i+1)%n;fs.append((a,a+n,b+n,b))
        fs.extend([(bot,1+(k-2)*n+(i+1)%n,1+(k-2)*n+i) for i in range(n)])
        self.geom(vs,fs,mat,True)
    def ring(self,c,ro,ri,h,mat,n=64):
        vs=[(c[0]+r*math.cos(i*2*math.pi/n),c[1]+r*math.sin(i*2*math.pi/n),c[2]+z) for z in [0,h] for r in [ro,ri] for i in range(n)]
        fs=[]
        for i in range(n):
            j=(i+1)%n;fs += [(i,j,j+2*n,i+2*n),(n+j,n+i,n+i+2*n,n+j+2*n),(i+2*n,j+2*n,j+3*n,i+3*n),(j,i,i+n,j+n)]
        self.geom(vs,fs,mat)
    def finish(self):
        mesh=bpy.data.meshes.new(self.id);mesh.from_pydata(self.v,[],self.f);mesh.update()
        for m in M:mesh.materials.append(m)
        for p,mi,sm in zip(mesh.polygons,self.mi,self.smooth):p.material_index=mi;p.use_smooth=sm
        uv=mesh.uv_layers.new(name='UVMap')
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                v=mesh.vertices[mesh.loops[li].vertex_index].co
                uv.data[li].uv=(v.x/1.2,v.y/1.2) if abs(poly.normal.z)>.6 else (v.x+v.y,v.z)
        obj=bpy.data.objects.new(self.id,mesh);bpy.context.collection.objects.link(obj)
        obj['stable_id']=self.id;obj['category']=self.kind;obj['source_ids']=self.sources;obj['observed']=self.observed;obj['inferred']=self.inferred;obj['units']='model units, no real scale calibration'
        return obj

def A(id,kind,src='SRC01,SRC02,SRC03',obs='visible class and approximate relation',inf='all metric dimensions, hidden surfaces and structural details'):
    return Assembly(id,kind,src,obs,inf)

# Finite courtyard slab and paths. Real thickness, no extended entire campus.
a=A('SITE-PAVERS','ground');a.box((-2,6,-.20),(66,52,.4),paving);a.finish()
a=A('LAWN-L','lawn','SRC01','left green ground beyond track','exact border and hidden extension');a.box((-18,11,.055),(26,32,.11),grass);a.finish()

def catmull(points):
    result=[];pts=[points[0]]+points+[points[-1]]
    for i in range(1,len(pts)-2):
        p0,p1,p2,p3=map(Vector,pts[i-1:i+3])
        for j in range(15):
            t=j/15;result.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    result.append(Vector(points[-1]));return result
track=catmull([(-31,-18),(-19,-15),(-10,-12),(-4,-7),(-2.5,2),(-2.5,19)])
def ribbon(a,points,left,right,z,h,mat):
    vs=[]
    for i,p in enumerate(points):
        t=points[min(i+1,len(points)-1)]-points[max(i-1,0)];t.normalize();n=Vector((-t.y,t.x))
        for zz in [z,z+h]:
            for off in [left,right]:q=p+n*off;vs.append((q.x,q.y,zz))
    fs=[(0,2,3,1)]
    for i in range(len(points)-1):
        x=4*i;fs.extend([(x+2,x+6,x+7,x+3),(x+4,x,x+1,x+5),(x,x+4,x+6,x+2),(x+1,x+3,x+7,x+5)])
    n=len(vs);fs.append((n-4,n-3,n-1,n-2));a.geom(vs,fs,mat)
a=A('TRACK-ARC','partial curved track','SRC01,SRC02','red curved band with parallel white markings','path curvature, lane count beyond occlusion; not a 400m circuit');ribbon(a,track,-3.6,3.6,.015,.035,red)
for off in [-3.52,-1.75,0,1.75,3.52]:ribbon(a,track,off-.035,off+.035,.051,.004,line)
a.finish()
for id,c,d,mat in [('COURT-NE',(10.5,16,.07),(18,13,.08),cyan),('COURT-E',(13.5,-7.5,.04),(12,21,.04),red),('COURT-E-IN',(13.5,-7.5,.065),(10.7,18,.01),green)]:
    a=A(id,'partial sports surface','SRC01,SRC02,SRC03','finite cyan/green/red sport surface edges','exact dimensions, standard sport specification unproven');a.box(c,d,mat);a.finish()
a=A('COURT-MARKINGS','court lines');
for x in [2,9,19]:a.box((x,16,.118),(.045,12,.008),line)
for y in [10,16,22]:a.box((10.5,y,.118),(17,.045,.008),line)
for y in [-16.35,1.35]:a.box((13.5,y,.077),(10.5,.045,.008),line)
a.box((8.25,-7.5,.077),(.045,17.7,.008),line)
pts=[(14.4+2.5*math.cos(t*math.pi/48),-7.5+2.5*math.sin(t*math.pi/48),.078) for t in range(97)]
a.path(pts,.024,line,6);a.finish()

# L-shaped finite buildings. Actual apertures: pier/spandrel assembly, no solid slab behind glass.
def facade(prefix,origin,axis,bays,pitch,levels,door_bay=None):
    ox,oy=origin;dx,dy=axis;nx,ny=-dy,dx # recess toward inside
    def pos(u,v,z):return (ox+u*dx+v*nx,oy+u*dy+v*ny,z)
    rot=math.atan2(dy,dx);width=bays*pitch;w=pitch-.55;floor=3.18;sill=.52;wh=2.10
    wall=A(prefix+'-SHELL','facade shell','SRC01,SRC02,SRC03','four visible window rows; pale wall and repeats','finite rear shell, depths, omitted off-frame extensions')
    for c in range(bays+1):wall.box(pos(c*pitch,.18,6.36),(.55,.36,12.72),plaster,rot)
    for row in range(levels):
        z=row*floor
        for c in range(bays):
            if row==0 and c==door_bay:continue
            wall.box(pos((c+.5)*pitch,.18,z+sill/2),(w,.36,sill),plaster,rot)
        for c in range(bays):
            wall.box(pos((c+.5)*pitch,.18,z+sill+wh+(floor-sill-wh)/2),(w,.36,floor-sill-wh),plaster,rot)
    wall.box(pos(width/2,.15,12.85),(width+.6,.8,.26),trim,rot)
    # finite rear and roof, explicitly inferred. Visible window recesses remain empty until pane.
    wall.box(pos(width/2,3.8,6.36),(width,.25,12.72),plaster,rot)
    for u in [0,width]:wall.box(pos(u,2,6.36),(.30,3.8,12.72),plaster,rot)
    wall.box(pos(width/2,2,12.7),(width,3.8,.2),trim,rot)
    for z in [3.18,6.36,9.54]:wall.box(pos(width/2,2,z),(width,3.5,.16),dark,rot)
    wall.finish()
    for row in range(levels):
      for c in range(bays):
        door=(row==0 and c==door_bay);bot=.40 if door else row*floor+sill;h=2.20 if door else wh;u=(c+.5)*pitch
        a=A(f'{prefix}-'+('DOOR' if door else f'W-r{row+1:02d}-c{c+1:02d}'),'door' if door else 'window','SRC01,SRC02,SRC03','rectangular opening, brown mullions and blue/dark panes','instance correspondence/corner occlusion provisional; glazing optical values and recess depth')
        for side in [-1,1]:a.box(pos(u+side*w/2,.14,bot+h/2),(.085,.30,h+.10),trim,rot)
        for z in [bot,bot+h]:a.box(pos(u,.14,z),(w+.08,.30,.085),trim,rot)
        a.box(pos(u,.27,bot+h/2),(w-.12,.035,h-.10),glass,rot)
        for off in [-w/2+.09,-w/6,w/6,w/2-.09]:a.box(pos(u+off,-.01,bot+h/2),(.065,.13,h),frame,rot)
        for z in [bot+.06,bot+h*.73,bot+h-.06]:a.box(pos(u,-.01,z),(w,.13,.065),frame,rot)
        if door:
            for du in [-.10,.10]:a.tube(pos(u+du,-.1,1.1),pos(u+du,-.1,1.5),.025,metal)
        a.finish()
    a=A(prefix+'-ROOF-RAIL','roof rail','SRC01','thin railing along upper edge','hidden continuation and attachment')
    for u in [i*1.2 for i in range(int(width/1.2)+1)]:a.tube(pos(u,0,12.98),pos(u,0,13.7),.025,metal)
    for z in [13.15,13.7]:a.tube(pos(0,0,z),pos(width,0,z),.025,metal)
    a.finish()

facade('BLD-A',(-5.6,28),(1,0),7,3.65,4)
facade('BLD-B',(20,28),(0,-1),12,3.8,4,6)
a=A('BACKDROP-WEST-FRAGMENT','finite background wall','SRC01','dark wall-like patch behind left tree and goals','identity, depth and hidden extent unresolved')
a.box((-15.3,29,4.2),(19,.35,8.4),dark);a.finish()
# Entrance raised landing and continuous real steps, observed in SRC02/03.
a=A('ENTRY-STEPS','entrance steps','SRC02,SRC03','low stepped rise along east facade, door/planter adjacency','rise/run and length not calibrated')
for i in range(3):a.box((19.25-i*.32,3.8,(3-i)*.065),(.64+2*i*.32,17,(3-i)*.13),trim)
a.box((19.7,3.8,.195),(.6,17,.39),trim)
a.finish()
a=A('BLD-B-DRAIN','rain pipe','SRC02,SRC03','vertical light drain pipe near corner, curved foot','diameter and joints')
a.path([(19.7,9.1,12.6),(19.7,9.1,1),(19.45,9.1,.8),(19.45,9.1,.5)],.075,trim);a.finish()

def tree(id,x,y,r,h,pink=False):
    a=A(id,'volumetric tree','SRC01,SRC02,SRC03','trunk/canopy silhouette and approximate shared location','all branching topology, hidden roots, leaf distribution')
    a.tube((x,y,0),(x+.12,y,h*.5),r,bark,r*.56,16)
    for k in range(9):
        ang=k*2.399+random.uniform(-.2,.2);z=h*(.30+.036*k)
        start=Vector((x+.08,y,z));end=Vector((x+math.cos(ang)*h*.25,y+math.sin(ang)*h*.25,h*(.66+random.random()*.17)))
        a.tube(start,end,r*.30,bark,r*.07,10)
        for j in range(6):
            p=start.lerp(end,.50+j*.10)+Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(0,1.4)))
            q=p+Vector((random.uniform(-1.4,1.4),random.uniform(-1.4,1.4),random.uniform(.3,1.8)))
            a.tube(p,q,r*.045,bark,.015,6)
            for l in range(15):
                c=q+Vector((random.uniform(-1.1,1.1),random.uniform(-1.1,1.1),random.uniform(-.65,.65)))
                s=random.uniform(.16,.38);a.sphere(c,(s*1.5,s,s*.45),leafs[4] if pink else random.choice(leafs[:4]),6,3)
    a.finish()
def treebed(id,x,y,r):
    a=A(id,'tree bed','SRC01,SRC02','circular low concrete rim and soil inside','exact section and buried foundation');a.ring((x,y,0),r,r-.16,.39,trim);a.tube((x,y,0),(x,y,.19),r-.16,soil,n=64);a.finish()
treebed('TREEBED-01',3.9,-3.1,2.24);tree('TREE-01',3.9,-3.1,.68,16)
tree('TREE-02',-12,16,.45,12)
tree('TREE-03',13,24,.36,11)
tree('TREE-04',15,6,.32,12,True)
tree('TREE-05',17.8,-8.5,.36,15)
treebed('TREEBED-05',17.8,-8.5,.9)
tree('TREE-06',-24,20,.45,13)
tree('TREE-07',8,24,.25,10)

def planter(id,x,y,w,d):
    a=A(id,'flower bed','SRC01,SRC02,SRC03','low light rim, green leaves and small flowers','section, plant species and hidden substrate')
    for xx in [-w/2,w/2]:a.box((x+xx,y,.23),(.12,d,.46),trim)
    for yy in [-d/2,d/2]:a.box((x,y+yy,.23),(w,.12,.46),trim)
    a.box((x,y,.26),(w-.12,d-.12,.12),soil)
    for k in range(int(w*d*6)):
        xx=x+random.uniform(-w*.46,w*.46);yy=y+random.uniform(-d*.43,d*.43);a.sphere((xx,yy,.55),(.23,.23,.28),leafs[k%4],6,3)
        if k%2==0:a.sphere((xx,yy,.82),(.09,.09,.06),flower,6,3)
    a.finish()
planter('FLOWERBED-01',12,7,6,1.6);planter('FLOWERBED-02',17,4,3.5,1.4);planter('FLOWERBED-03',16,18,5.5,1.5)
# modest shrubs along rear; distributions uncertain, evidence category retained.
for i,x in enumerate([-3,1,5,9,13,17]):
    a=A(f'SHRUB-{i+1:02}','shrub','SRC01,SRC02','low green shrub line against rear facade','individual shape and distribution');a.sphere((x,26,.65),(1.2,.8,.8),leafs[0],10,6);a.finish()

def lamp(id,x,y,h,reach=1.5):
    a=A(id,'curved lamp','SRC01,SRC02,SRC03','tall curved grey post and pale horizontal head','curve dimensions, bases, electrical internals')
    a.tube((x,y,.05),(x,y,h-1.35),.07,metal,n=12)
    pts=[(x+reach*(1-math.cos(t*math.pi/2)),y,h-1.35+1.35*math.sin(t*math.pi/2)) for t in [i/16 for i in range(17)]]
    a.path(pts,.065,metal,10);a.box((x+reach+.2,y,h),(.65,.27,.14),metal);a.box((x+reach+.2,y,h-.08),(.53,.24,.04),lampmat);a.box((x,y,.06),(.25,.25,.12),metal);a.finish()
lamp('LAMP-01',3.3,13.5,10.2,1.6);lamp('LAMP-02',.2,20,8.4,2.9);lamp('LAMP-03',-.65,24,6.7,2.6);lamp('LAMP-04',13.5,5,10.8,-1.5)

def bench(id,x,y,rot=0):
    a=A(id,'bench','SRC01,SRC02','orange horizontal slats, dark curved legs and back','fasteners, hidden backs and exact count');co=math.cos(rot);si=math.sin(rot)
    def p(u,v,z):return(x+u*co-v*si,y+u*si+v*co,z)
    for v in [-.26,-.09,.08,.25]:a.box(p(0,v,.57),(2.35,.14,.10),wood,rot)
    for z in [.83,1.03,1.23]:a.box(p(0,.36+(z-.8)*.2,z),(2.35,.11,.15),wood,rot)
    for u in [-.88,.88]:
        a.path([p(u,-.36,.025),p(u,-.24,.48),p(u,.23,.55),p(u,.38,.025)],.045,metal)
        a.path([p(u,.23,.48),p(u,.33,.85),p(u,.45,1.34)],.035,metal)
    a.finish()
bench('BENCH-01',3.6,8.8);bench('BENCH-02',-7.8,18);bench('BENCH-03',-13,21);bench('BENCH-04',13,23.4)
for id,x,y in [('BIN-01',5.4,6.9),('BIN-02',6.6,6.9)]:
    a=A(id,'bin','SRC02','small paired rectangular bins by bench','underside/opening hidden');a.box((x,y,.49),(.7,.72,.98),wood);a.box((x,y,.99),(.75,.77,.08),metal);a.finish()

def goal(id,x,y,w,h,d):
    a=A(id,'goal','SRC01','white rectangular goal frame with mesh behind','depth and exact mesh spacing')
    for xx in [x-w/2,x+w/2]:
        a.path([(xx,y,.06),(xx,y,h),(xx,y+d,h*.75),(xx,y+d,.06),(xx,y,.06)],.045,line)
    for z,yy in [(h,y),(h*.75,y+d),(.06,y+d)]:a.tube((x-w/2,yy,z),(x+w/2,yy,z),.045,line)
    for i in range(21):
        xx=x-w/2+w*i/20;a.path([(xx,y,h),(xx,y+d,h*.75),(xx,y+d,.06)],.009,net,5)
    for j in range(11):
        z=.06+(h*.75-.06)*j/10;a.tube((x-w/2,y+d,z),(x+w/2,y+d,z),.009,net,n=5)
    a.finish()
goal('GOAL-01',-8.1,5.3,1.6,2.2,1.0);goal('GOAL-02',-6.5,12.8,1.4,1.65,.75);goal('GOAL-03',-23,18,5,2.4,1.3)
a=A('SPORT-NET-01','court net','SRC01,SRC02','horizontal cord net across blue court','mesh spacing and anchors')
for x in [5.8,18.2]:a.tube((x,18,.1),(x,18,2.0),.035,metal)
for z in [1.1,1.22,1.34,1.46,1.58,1.7,1.82]:a.tube((5.8,18,z),(18.2,18,z),.009,net,n=5)
for i in range(101):x=5.8+12.4*i/100;a.tube((x,18,1.1),(x,18,1.82),.006,net,n=5)
a.finish()

def hoop(id,x,y,z,rot=0):
    a=A(id,'basketball stand','SRC01,SRC02,SRC03','black post, angled brace, rectangular board and rim/net','base plate/anchors and hidden support sections')
    co=math.cos(rot);si=math.sin(rot)
    def p(u,v,zz):return(x+u*co-v*si,y+u*si+v*co,zz)
    a.box(p(0,.9,.075),(.65,.65,.15),metal,rot);a.box(p(0,.9,z*.36),(.23,.23,z*.72),metal,rot)
    for u in [-.17,.17]:a.tube(p(u,.9,z*.65),p(u,0,z),.07,metal)
    a.box(p(0,0,z+.36),(1.9,.13,1.25),metal,rot);a.box(p(0,-.075,z+.36),(1.77,.018,1.12),plaster,rot)
    for u in [-.36,.36]:a.box(p(u,-.095,z+.23),(.03,.02,.49),metal,rot)
    for zz in [z-.015,z+.475]:a.box(p(0,-.095,zz),(.74,.02,.03),metal,rot)
    pts=[p(.31*math.cos(t*2*math.pi/36),-.42+.31*math.sin(t*2*math.pi/36),z-.1) for t in range(37)];a.path(pts,.022,ball)
    for i in range(12):
        t=i*2*math.pi/12;a.tube(p(.31*math.cos(t),-.42+.31*math.sin(t),z-.1),p(.17*math.cos(t+.35),-.42+.17*math.sin(t+.35),z-.53),.008,net,n=5)
    a.finish()
hoop('HOOP-01',4.7,24,3.5);hoop('HOOP-02',6.6,14,4.4);hoop('HOOP-03',17,-6,7.0,0)
a=A('BALL-RACK-01','ball rack','SRC01,SRC02,SRC03','brown open rack with three orange balls near east entrance','underside joinery, exact tube/wood material')
for x in [13.2,15.4]:
    for y in [1.8,2.4]:a.box((x,y,.70),(.055,.055,1.4),wood)
for z in [.10,.75,1.30]:
    for y in [1.8,2.4]:a.box((14.3,y,z),(2.25,.065,.12),wood)
for x in [13.6,14.3,15]:a.sphere((x,2.1,1.43),(.23,.23,.23),ball,16,10)
a.finish()

# Exterior switchback stair attached to east wing. Steps, two stringers, balustrades, landings.
# Number of unseen flights and structural arrangement explicitly inferred.
a=A('STAIR-01','exterior switchback steel stair','SRC03','brown open treads, zigzag flights, posts and vertical railing','rise/run, attachment, upper/back flights and structural design; not engineering certified')
for x in [16.3,19.25]:
    for y in [-10,-3.5]:a.box((x,y,6.35),(.16,.16,12.7),rust)
for floor in range(4):
    base=floor*3.18;direction=1 if floor%2==0 else -1;x=17.0 if floor%2==0 else 18.55;y0=-9.7 if direction==1 else -3.9
    for k in range(18):
        yy=y0+direction*k*.32;zz=base+(k+1)*3.18/18
        a.box((x,yy,zz-.035),(1.35,.32,.07),rust)
        for side in [-1,1]:
            a.tube((x+side*.67,yy,zz),(x+side*.67,yy,zz+.95),.018,metal,n=6)
    endy=y0+direction*17*.32
    for side in [-1,1]:
        xx=x+side*.67;a.tube((xx,y0,base+.04),(xx,endy,base+3.18),.075,rust,n=6)
        a.tube((xx,y0,base+.95),(xx,endy,base+4.13),.025,metal,n=8)
    a.box((17.8,endy+direction*.40,base+3.18-.06),(3.05,1.05,.12),rust)
    for xx in [16.3,17.3,18.3,19.25]:a.tube((xx,endy+direction*.85,base+3.18),(xx,endy+direction*.85,base+4.13),.025,metal)
    a.tube((16.3,endy+direction*.85,base+4.13),(19.25,endy+direction*.85,base+4.13),.035,metal)
a.finish().location.y=-7

a=A('STAIR-GUARD-CONNECTIONS','stair landing rail returns','SRC03','continuous rail system required by visible stair','hidden corner routing and exact joints inferred')
for floor in range(4):
    di=1 if floor%2==0 else -1;y0=-9.7 if di==1 else -3.9;ey=y0+di*17*.32-7;z=(floor+1)*3.18+.95
    for xx in [16.3,19.25]:a.tube((xx,ey,z),(xx,ey+di*.85,z),.035,metal)
    if floor<3:
        x1=17.67 if di==1 else 17.88;x2=17.88 if di==1 else 17.67;ny=(-3.9 if di==1 else -9.7)-7
        a.path([(x1,ey,z),(x1,ey+di*.25,z),(x2,ny,z)],.028,metal)
a.finish()

scene=bpy.context.scene
scene.unit_settings.system='NONE'
world=bpy.data.worlds.new('Courtyard shared daylight');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.63,.78,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
data=bpy.data.lights.new('SUN-shared','SUN');o=bpy.data.objects.new('SUN-shared',data);scene.collection.objects.link(o);data.energy=3.0;data.angle=.06;o.rotation_euler=(math.radians(66),math.radians(-24),math.radians(-42))
CAMERAS={
 'SRC01':((0,-28,3.0),(0,28,.9),45),
 'SRC02':((-12.676153,-34.781917,6.0),(14.608152,6.668716,-.116511),62.139896),
 'SRC03':((-8,-20,2.4),(20,-7.5,7.0),42),
 'SRC04':((-5.782931,-29.897674,6.0),(21.804981,10.666869,-3.66566),35.0),
 'MAIN':((-18,-28,17),(2,7,3.5),42),
 'CHECK01-front':((0,-37,13),(0,9,3),38),
 'CHECK02-left':((-35,-18,17),(0,9,3),38),
 'CHECK03-west':((-37,15,15),(1,10,3),35),
 'CHECK04-north':((-12,42,22),(1,10,3),34),
 'CHECK05-east':((35,28,21),(4,8,3),34),
 'CHECK06-south-east':((31,-23,15),(4,8,3),38),
 'CHECK07-overhead':((1,4,65),(1,4,0),38),
 'CHECK08-stair':((6,-25,9),(18,-12,6),42),
}
for name,(loc,target,lens) in CAMERAS.items():
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=250;o['role']='conditional source fit' if name.startswith('SRC') else 'internal inspection, not a source baseline'
scene.camera=bpy.data.objects['SRC01']
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=50
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene['source_acceptance']='NOT PASSED: provisional cameras and missing later-replay source validation'
scene['shared_state']='one unchanged geometry, material and lighting state for all source cameras'
scene['model_units']='arbitrary; not scaled from character'
if stage=='blockout':
    for obj in scene.objects:
        if obj.type=='MESH':
            for p in obj.data.polygons:p.material_index=white
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'campus-courtyard_blockout.blend'))
    scene.render.filepath=str(OUT/'SRC01_white_initial.png');bpy.ops.render.render(write_still=True)
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'campus-courtyard_material.blend'))
    bpy.ops.export_scene.gltf(filepath=str(OUT/'campus-courtyard.glb'),export_format='GLB',export_cameras=False,export_lights=False)
    for obj in scene.objects:
        if obj.type=='MESH':
            for p in obj.data.polygons:p.material_index=white
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'campus-courtyard_white.blend'))
manifest=[]
for o in scene.objects:
    if o.type=='MESH':
        manifest.append({'id':o.name,'category':o.get('category'),'sources':o.get('source_ids'),'observed':o.get('observed'),'inferred':o.get('inferred'),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'world_bounds':[list(map(float,o.matrix_world@Vector(v))) for v in o.bound_box]})
(OUT/'object_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'camera_parameters.json').write_text(json.dumps({k:{'location':v[0],'target':v[1],'lens_mm':v[2],'sensor_width_mm':36,'calibrated':False,'role':'conditional source' if k.startswith('SRC') else 'internal inspection'} for k,v in CAMERAS.items()},indent=2))
print('BUILD_COMPLETE',stage,len(manifest))
