# New full-scene-scope remake. No lost R06 model dependency or old-history restoration.
import bpy,math,json,hashlib
from mathutils import Vector
from pathlib import Path
D=Path(__file__).resolve().parents[1];P=json.load(open(D/'parameters.json'));bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.cycles.use_denoising=False;s.world=bpy.data.worlds.new('Working neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.12,.16,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.view_settings.view_transform='Standard';inventory=[]
def mat(n,c,metal=0,em=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;q=m.node_tree.nodes['Principled BSDF'];q.inputs['Base Color'].default_value=(*c,1);q.inputs['Metallic'].default_value=metal;q.inputs['Roughness'].default_value=.48;q.inputs['Emission Color'].default_value=(*c,1);q.inputs['Emission Strength'].default_value=em;return m
M={'floor':mat('walkway_work_approx',(.22,.18,.16)),'stone':mat('pale_column_work_approx',(.48,.39,.32)),'red':mat('red_column_work_approx',(.23,.045,.03)),'roof':mat('gray_tiles_work_approx',(.16,.18,.2)),'gold':mat('bronze_work_approx',(.4,.22,.055),.65),'water':mat('reflective_pool_proxy_not_water_validation',(.06,.085,.11),.7),'stage':mat('flower_disc_plain_proxy_NO_photo',(.27,.035,.06),.4),'paper':mat('warm_paper_work_approx',(.8,.45,.16),0,.8),'lamp':mat('red_paper_work_approx',(.65,.08,.025),0,.35),'rib':mat('lamp_dark_ribs',(.15,.025,.012)),'white':mat('WHITE_SHARED',(.65,.65,.65))}
def finish(o,n,k,grade='B-visible-kind; dimensions/placement conditional'):
 o.name=n;o.data.materials.append(M[k]);o['evidence_grade']=grade;inventory.append({'name':n,'material':k,'evidence_grade':grade});return o
def mesh(n,v,f,k,grade='B-visible-kind; dimensions/placement conditional'):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);return finish(o,n,k,grade)
def cube(n,loc,dim,k):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,k)
def cyl(n,loc,r,h,k,N=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=h,location=loc);return finish(bpy.context.object,n,k)
def rod(n,a,b,r,k):
 a=Vector(a);b=Vector(b);o=cyl(n,(a+b)/2,r,(b-a).length,k,8);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def ring(n,r0,r1,z0,z1,k,N=128):
 v=[(r*math.cos(t*2*math.pi/N),r*math.sin(t*2*math.pi/N),z) for r,z in [(r0,z0),(r1,z0),(r1,z1),(r0,z1)] for t in range(N)];f=[]
 for j in range(4):
  for t in range(N):f.append((j*N+t,j*N+(t+1)%N,((j+1)%4)*N+(t+1)%N,((j+1)%4)*N+t))
 return mesh(n,v,f,k)
def xyz(r,a,z):return (r*math.cos(math.radians(a)),r*math.sin(math.radians(a)),z)
def sector(n,r0,r1,a0,a1,zfun,thick,k,N=40,W=8):
 v=[]
 for layer in [0,1]:
  for i in range(N+1):
   a=a0+(a1-a0)*i/N
   for j in range(W+1):r=r0+(r1-r0)*j/W;v.append(xyz(r,a,zfun(j/W)-layer*thick))
 f=[];K=(N+1)*(W+1)
 for layer in [0,1]:
  for i in range(N):
   for j in range(W):q=layer*K+i*(W+1)+j;face=(q,q+1,q+W+2,q+W+1);f.append(face if layer==0 else tuple(reversed(face)))
 boundary=list(range(W+1))+[i*(W+1)+W for i in range(1,N+1)]+[N*(W+1)+j for j in range(W-1,-1,-1)]+[i*(W+1) for i in range(N-1,0,-1)]
 for i,q in enumerate(boundary):u=boundary[(i+1)%len(boundary)];f.append((q,u,u+K,q+K))
 return mesh(n,v,f,k)
def lathe(n,xy,profile,k,N=32):
 v=[(xy[0]+r*math.cos(j*2*math.pi/N),xy[1]+r*math.sin(j*2*math.pi/N),z) for z,r in profile for j in range(N)];f=[]
 for i in range(len(profile)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
 f.extend([tuple(reversed(range(N))),tuple((len(profile)-1)*N+j for j in range(N))]);return mesh(n,v,f,k)
# Continuous support excludes the real pool opening. No solid ground hiding the water opening.
ring('WALKWAY_annular_solid_support',6.5,10.8,-.25,0,'floor');cyl('POOL_closed_basin_bottom',(0,0,-.32),6.5,.16,'stone',128);ring('POOL_retaining_wall',6.4,6.5,-.32,.04,'gold');ring('POOL_water_proxy',5.18,6.4,-.1,-.08,'water');cyl('STAGE_solid_core',(0,0,.035),5,.57,'stage',128)
for eid,r,z in [('UPPER_LIP',5,.34),('MIDDLE_STEP',5.08,.23),('LOWER_LIP',5.15,.1)]:ring('STAGE_'+eid,r-.035,r+.035,z-.025,z+.025,'gold')
ring('STAGE_step_body',5,5.18,-.23,.075,'stone');ring('WALKWAY_pool_edge_band',6.43,6.55,.0,.045,'gold')
# New curved colonnade topology; NOT previous four-row straight corridor.
for side,angles in [('R',P['right_roof_angles_degrees']),('L',P['left_roof_angles_degrees'])]:
 a0,a1=angles;zfun=lambda t:4.4+.45*math.sin(math.pi*t)
 sector('ROOF_'+side+'_thick_curved_solid',6.95,9.8,a0,a1,zfun,.14,'roof')
 for tag,r0,r1 in [('inner',6.92,7.05),('outer',9.7,9.84)]:sector('EAVE_'+side+'_'+tag,r0,r1,a0,a1,lambda t:4.42,.22,'gold',40,1)
 for i in range(62):
  a=a0+(a1-a0)*i/61
  pts=[xyz(6.95+(9.8-6.95)*j/6,a,zfun(j/6)+.025) for j in range(7)]
  for j in range(6):rod(f'TILE_{side}_{i}_{j}',pts[j],pts[j+1],.045,'roof')
 for j,aR in enumerate(P['column_right_angles_degrees']):
  a=aR if side=='R' else 180-aR
  for row,r in [('IN',7.3),('OUT',9.2)]:
   x,y,_=xyz(r,a,0);name=f'COL_{side}_{row}_{j}';key='stone' if j in [0,1] else 'red'
   cube(name+'_base',(x,y,.12),(.68,.68,.24),'gold');cube(name+'_shaft',(x,y,2.16),(.4,.4,3.84),key);cube(name+'_cap',(x,y,4.19),(.65,.65,.22),'gold');cube(name+'_roof_support',(x,y,4.32),(.3,.3,.1),'red')
  rod(f'BEAM_{side}_{j}_cross',xyz(7.1,a,4.13),xyz(9.45,a,4.13),.16,'red')
 # Continuous inner beam finite thickness under roof, no guessed full hidden building.
 sector('BEAM_'+side+'_inner_curved',7.12,7.42,a0,a1,lambda t:4.3,.27,'red',40,1)
# Local detailed round lamps: body and continuous parallel-transport rib tubes, counts inferred.
def tube(n,points,r,k):
 pts=[Vector(p) for p in points];v=[];f=[];u=None;N=6
 for i,p in enumerate(pts):
  t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
  if u is None:u=t.cross(Vector((0,0,1)) if abs(t.z)<.9 else Vector((1,0,0))).normalized()
  else:u=(u-t*u.dot(t)).normalized()
  w=t.cross(u);v.extend(tuple(p+r*(u*math.cos(j*2*math.pi/N)+w*math.sin(j*2*math.pi/N))) for j in range(N))
 for i in range(len(pts)-1):
  for j in range(N):q=i*N+j;u0=i*N+(j+1)%N;f.append((q,u0,u0+N,q+N))
 f.extend([tuple(reversed(range(N))),tuple((len(pts)-1)*N+j for j in range(N))]);return mesh(n,v,f,k,'C-local rib/back/repetition hypothesis; known continuous-section technique')
def roundlamp(n,x,y,z):
 h=.6;rx=.54;prof=[(z+h*(i/16-.5),rx*(.3+.7*math.sin(math.pi*i/16)**.48)) for i in range(17)];lathe(n+'_paper',(x,y),prof,'lamp')
 for j in range(12):
  a=j*math.pi/6;tube(n+f'_rib{j}',[(x+r*math.cos(a),y+r*math.sin(a),zz) for zz,r in prof],.009,'rib')
 for k in [0,16]:zz,r=prof[k];tube(n+f'_collar{k}',[(x+r*math.cos(j*math.pi/16),y+r*math.sin(j*math.pi/16),zz) for j in range(33)],.018,'rib')
 rod(n+'_hang',(x,y,z+.3),(x,y,4.26),.012,'gold');rod(n+'_tassel',(x,y,z-.3),(x,y,z-.62),.018,'rib')
for side in ['R','L']:
 for j,aR in enumerate(P['column_right_angles_degrees']):
  a=aR if side=='R' else 180-aR;x,y,_=xyz(6.9,a,0);roundlamp(f'ROUND_{side}_{j}',x,y,3.72)
  # Bronze silhouette, no invented filigree: explicitly coarse shell.
  if j in [0,1,3]:
   x,y,_=xyz(6.82,a-5 if side=='R' else a+5,0);lathe(f'URN_{side}_{j}_solid_profile_PROXY',(x,y),[(0,.26),(.12,.28),(.25,.15),(.5,.12),(.65,.25),(.9,.36),(1.2,.34),(1.35,.23),(1.4,.42),(1.5,.28),(1.7,.1),(1.8,.04)],'gold')
for row,(angle,count) in enumerate(zip(P['cross_string_angles_degrees'],P['cross_string_counts'])):
 xx,yy,_=xyz(6.95,angle,0);points=[]
 for j in range(count):
  x=-xx+2*xx*j/(count-1);z=4.12-.35*(1-(x/xx)**2);points.append((x,yy,z));lathe(f'LONG_row{row}_{j}_paper',(x,yy),[(z-.5,.08),(z-.46,.12),(z-.12,.12),(z-.08,.08)],'paper',16);rod(f'LONG_row{row}_{j}_hanger',(x,yy,z-.08),(x,yy,z),.009,'gold')
  if j:rod(f'STRING_row{row}_{j}',points[j-1],points[j],.008,'rib')
# No actor/flower photo boards, no invented distant mountain building.
for i in range(8):
 a=i*math.pi/4;c=bpy.data.cameras.new('CHECK'+str(i));o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=(20*math.sin(a),-20*math.cos(a),14);o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler();c.lens=28
for n,loc,pow in [('KEY',(0,-8,16),3500),('FILL',(0,8,12),2200)]:
 l=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=loc;l.energy=pow;l.shape='DISK';l.size=12
s.camera=bpy.data.objects['CHECK0'];report={'status':'NEW full-scene-scope first checkpoint, not accepted; missing fine objects/entrance connectivity listed','mesh_count':len(inventory),'objects':inventory,'not_included':['precise entrance roof turn: visible but not yet modelled','full open-work urn filigree','decorative lattice/knee brackets and outside railings','flower geometry/backgrounds and petal scatter','exact lamp repetitions/cross-date instance matches','source calibrated cameras and direct overlays'],'all_scales_conditional':True,'no_old_R06_R07_history_recovered':True};(D/'qa/FR01-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for typ in ['material','white']:
 if typ=='white':
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(M['white'])
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/FR01_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/FR01_{typ}.glb'),export_format='GLB')
files=[]
for f in sorted((D/'models').glob('*')):files.append({'file':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(D/'qa/FR01-checkpoint-files.json').write_text(json.dumps(files,indent=2));print('FIRST EDITABLE CHECKPOINT SAVED BEFORE RENDER',len(inventory))
