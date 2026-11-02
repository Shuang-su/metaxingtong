import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];Q=D/'qa/R07_lantern';Q.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(D/'models/R06b_column_trial_material.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.samples=24
names=['LANTERN_round_R0','LANTERN_string0_10']
def snapshot():
 return {o.name:hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],[list(r) for r in o.matrix_world])).encode()).hexdigest() for o in s.objects if o.type=='MESH'}
before=snapshot();cams={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='CAMERA'}
def render(tag,cam='SOURCE1',crop=False):
 s.camera=bpy.data.objects[cam];s.render.resolution_x=1920 if crop else 960;s.render.resolution_y=1080 if crop else 540;s.render.resolution_percentage=100;s.render.use_border=crop;s.render.use_crop_to_border=crop
 if crop:s.render.border_min_x=1400/1920;s.render.border_max_x=1700/1920;s.render.border_min_y=1-390/1080;s.render.border_max_y=1-100/1080
 s.render.filepath=str(D/f'renders/{tag}.png');bpy.ops.render.render(write_still=True)
render('R07_before_round_SOURCE1_nativecrop',crop=True)
def mat(n,c,em=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.64;p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em;return m
red=mat('R07_red_paper_approx_not_measured',(.65,.145,.035),.45);paper=mat('R07_cream_paper_approx_not_measured',(.83,.59,.29),.6);rib=mat('R07_dark_red_frame',(.19,.035,.012));frame=mat('R07_dark_warm_frame',(.17,.09,.035))
created=[]
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);o.data.materials.append(m);created.append(n)
 for p in me.polygons:p.use_smooth=True
 return o
def tube(n,points,r,m):
 # Mesh tube with real section; closed end caps. No photo planes or texture projection.
 v=[];f=[];N=8
 for i,p in enumerate(points):
  p=Vector(p);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)]);t.normalize();ref=Vector((0,0,1)) if abs(t.z)<.9 else Vector((1,0,0));u=t.cross(ref).normalized();w=t.cross(u).normalized()
  v += [tuple(p+r*(u*math.cos(j*2*math.pi/N)+w*math.sin(j*2*math.pi/N))) for j in range(N)]
 for i in range(len(points)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;f.append((a,b,b+N,a+N))
 f += [tuple(reversed(range(N))),tuple((len(points)-1)*N+j for j in range(N))];return mesh(n,v,f,m)
for name in names:
 old=bpy.data.objects[name];vs=[old.matrix_world@v.co for v in old.data.vertices];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);c=(lo+hi)/2;rx=(hi.x-lo.x)/2;ry=(hi.y-lo.y)/2;h=hi.z-lo.z
 isround='round' in name;rows=33;N=64;v=[];faces=[]
 # Keep original world envelope/centre; geometric details only, known source placement mismatch persists.
 def point(t,a):
  z=lo.z+t*h
  scale=(.3+.7*math.sin(math.pi*t)**.48) if isround else (.70+.30*min(1,math.sin(math.pi*t)/.24))
  return (c.x+rx*scale*math.cos(a),c.y+ry*scale*math.sin(a),z)
 for i in range(rows):
  for j in range(N):v.append(point(i/(rows-1),j*2*math.pi/N))
 for i in range(rows-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;faces.append((a,b,b+N,a+N))
 faces += [tuple(reversed(range(N))),tuple((rows-1)*N+j for j in range(N))]
 bpy.data.objects.remove(old,do_unlink=True);mesh(name,v,faces,red if isround else paper)
 for j in range(12 if isround else 8):
  a=j*2*math.pi/(12 if isround else 8);tube(name+f'_rib_{j:02}',[point(i/32,a) for i in range(33)],h*.009,rib if isround else frame)
 for t in [0,1]:
  tube(name+('_lower_collar' if t==0 else '_upper_collar'),[point(t,j*2*math.pi/64) for j in range(65)],h*.018,rib if isround else frame)
 # Central neck/pendant geometry. Source supports short tip/central tassel, strands and rear are inferred.
 tube(name+'_lower_neck',[(c.x,c.y,lo.z+.01),(c.x,c.y,lo.z-.05*h)],.035*h,rib if isround else frame)
 tube(name+'_pendant',[(c.x,c.y,lo.z-.04*h),(c.x,c.y,lo.z-(.43 if isround else .14)*h)],.018*h,rib if isround else frame)
 if isround:
  for j in range(5):
   a=j*2*math.pi/5;dx=.012*h*math.cos(a);dy=.012*h*math.sin(a);tube(name+f'_tasselstrand_{j}',[(c.x+dx,c.y+dy,lo.z-.32*h),(c.x+dx*1.3,c.y+dy*1.3,lo.z-.46*h)],.0035*h,rib)
after=snapshot();unchanged={n:after.get(n)==v for n,v in before.items() if n not in names};report={'frozen_parent':'c60dd658a717e6e8554970188d7cc4023e666e43','representatives':names,'created_meshes':created,'all_unrelated_meshes_unchanged':all(unchanged.values()),'camera_matrices_unchanged':cams=={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='CAMERA'},'source_shape_not_accepted':'original envelope/centre kept; round lamp too low/small and not source-flat enough; detail trial only','inferred':['backside repetition','12 round and 8 long complete rib count','tassel strands and material values'],'no_new_lamp_instances':True}
s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R07_lantern_trial_material.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/R07_lantern_trial_material.glb'),export_format='GLB');(Q/'construction.json').write_text(json.dumps(report,indent=2))
render('R07_after_round_SOURCE1_nativecrop',crop=True)
for cam in ['SOURCE1','SOURCE2_WORK','SOURCE3_TRAIN']:render('R07_'+cam+'_material960',cam)
white=mat('WHITE_R07_EXPLICIT',(.65,.65,.65))
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R07_lantern_trial_white.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'models/R07_lantern_trial_white.glb'),export_format='GLB');render('R07_white_round_SOURCE1_nativecrop',crop=True)
for cam in ['SOURCE1','SOURCE2_WORK','SOURCE3_TRAIN']:render('R07_'+cam+'_white960',cam)
