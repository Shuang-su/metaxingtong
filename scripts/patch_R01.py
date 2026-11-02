import bpy,math,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_remake_R00_material.blend'));s=bpy.context.scene
baseline={o.name:{'vertices':[list(v.co) for v in o.data.vertices],'matrix':[list(v) for v in o.matrix_world]} for o in s.objects if o.type=='MESH'}
added=[]; removed=[]
def sheet(n,pts,m):
 me=bpy.data.meshes.new(n);me.from_pydata(pts,[],[list(range(len(pts)))]);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);o.data.materials.append(m);o['validation_class']='printed_sheet';o['evidence']='Visible source2560 flat graphic; working proportions, no metric claim';added.append(n);return o
def band(n,pts,width,m):
 for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):
  a=list(a);b=list(b)
  if abs(a[2]-b[2])<1e-7 and n.find('PAD')>=0: ax1,ax2=0,1
  else:ax1,ax2=0,2
  dx=b[ax1]-a[ax1];dy=b[ax2]-a[ax2];L=math.hypot(dx,dy);off=[0,0,0];off[ax1]=-dy/L*width/2;off[ax2]=dx/L*width/2
  sheet(n+'_'+str(i),[[p[j]+sg*off[j]for j in range(3)]for p,sg in [(a,1),(b,1),(b,-1),(a,-1)]],m)
def ring(n,c,r,m,plane='xz',w=.009):
 for k in range(48):
  pts=[]
  for rad,t in [(r,k),(r,k+1),(r-w,k+1),(r-w,k)]:
   p=list(c);p[0]+=rad*math.cos(t*2*math.pi/48);p[2 if plane=='xz' else 1]+=rad*math.sin(t*2*math.pi/48);pts.append(p)
  sheet(n+'_'+str(k),pts,m)
g=bpy.data.materials['observed gold markings'];w=bpy.data.materials['white LED'];r=bpy.data.materials['red cabinet observed']
for i,cx in enumerate([-3.5,0,3.5],1):
 p=f'M{i:02d}'
 for j in range(4):
  o=bpy.data.objects[p+'_PAD_arrow_'+str(j)];removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 for j,(dx,dy) in enumerate([(-.75,0),(.75,0),(0,-.65),(0,.65)]):
  L=math.hypot(dx,dy);ux,uy=dx/L,dy/L;vx,vy=-uy,ux
  for k in range(3):
   pts=[(cx+dx+ux*(a-k*.07)+vx*b,-1.65+dy+uy*(a-k*.07)+vy*b,.204)for a,b in [(-.09,.13),(.10,0),(-.09,-.13)]]
   band(p+f'_PAD_cardinal_{j}_{k}',pts,.024,w)
 for j,(dx,dy)in enumerate([(-.9,-.58),(.9,-.58),(-.9,.58),(.9,.58)]):ring(p+f'_PAD_inner_{j}',(cx+dx,-1.65+dy,.204),.11,w,'xy',.005)
 # Flat lower graphics, visibly present in source; intentionally no invented tiny labels.
 for side in [-1,1]:
  for k in range(4):
   rr=.024+k*.014;x=cx+side*(.64-.025*k);z=.78-k*.14
   sheet(p+f'_LOW_dot_{side}_{k}',[(x+rr*math.cos(t*2*math.pi/32),-.086,z+rr*math.sin(t*2*math.pi/32))for t in range(32)],g)
 for col,xx in enumerate([-.19,.24]):
  for k in range(4):
   zz=.76-k*.14;sg=-1 if col==0 else 1
   band(p+f'_LOW_chevron_{col}_{k}',[(cx+xx-.08,-.087,zz-sg*.04),(cx+xx,-.087,zz+sg*.04),(cx+xx+.08,-.087,zz-sg*.04)],.025,g)
 for rad in [.15,.105]:ring(p+'_LOW_ring_'+str(rad),(cx+.50,-.088,.22),rad,g,w=.012)
 # Observed fourfold pinwheel-like gold symbol, approximate flat silhouette explicitly labeled.
 for j in range(4):
  ang=j*math.pi/2;pts=[]
  for x,z in [(.03,.02),(.14,.11),(.08,-.035)]:pts.append((cx-.43+x*math.cos(ang)-z*math.sin(ang),-.088,.66+x*math.sin(ang)+z*math.cos(ang)))
  sheet(p+'_LOW_pinwheel_'+str(j),pts,g)
 for side in [-1,1]:
  sheet(p+'_BUTTON_red_inset_'+str(side),[(cx+side*1.03+x,-.293,1.43+z)for x,z in [(-.08,-.07),(.08,-.07),(.08,.07),(-.08,.07)]],r)
# All geometry outside named local printed additions and 12 removed arrows must remain bytewise identical.
after={o.name:{'vertices':[list(v.co) for v in o.data.vertices],'matrix':[list(v) for v in o.matrix_world]}for o in s.objects if o.type=='MESH'}
changed=[n for n in baseline if n not in removed and baseline[n]!=after[n]];assert not changed
s['status']='R01 local printed graphics correction only; source FAIL; camera uncalibrated'
(D/'qa/R01_scope.json').write_text(json.dumps({'added':added,'removed':removed,'unexpected_existing_mesh_changes':changed,'cameras_lights_unchanged':True,'source':'2560.58535 original; not highest bitrate','limitations':'Working print proportions; not exact UV/albedo. Cabinet/source framing still FAIL.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_remake_R01_material.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_remake_R01_material.glb'),export_format='GLB',export_cameras=True,export_lights=True)
white=bpy.data.materials.new('R01 persistent shared white');white.diffuse_color=(.62,.62,.62,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/arcade_remake_R01_white.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/arcade_remake_R01_white.glb'),export_format='GLB',export_cameras=True,export_lights=True)
