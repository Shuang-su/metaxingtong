import bpy,pathlib,math,json
P=pathlib.Path(__file__).resolve().parents[1];records=[]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R01_{mode}.blend'))
 # Original two horizontal bars share front plane y=.27 with uprights and overlap corners.
 for o in list(bpy.data.objects):
  if o.name.startswith('MIRROR_frame_horizontal_'):
   for v in o.data.vertices:v.co.x*=2.37/2.65
   o.location.z=.835 if o.location.z<1 else 2.305
 # Same shell topology and thickness; radial octagonal profile, not source-calibrated umbrella.
 o=bpy.data.objects['UMBRELLA_finite_canopy_proxy'];N=32;rings=7
 for v in o.data.vertices:
  j=v.index%N;t=2*math.pi*j/N;d=(t+math.pi/8)%(math.pi/4)-math.pi/8;factor=math.cos(math.pi/8)/math.cos(d)
  # corner positions at j=0,4,... : rotate phase so vertices stay at original rib radii.
  d=(t%(math.pi/4))-math.pi/8;factor=math.cos(math.pi/8)/math.cos(d)
  # canopy points are stored in world-local identity coordinates; decompose its radial basis.
  from mathutils import Vector
  c=Vector((2,1.5,2.35));axis=Vector((0,-.85,-.3)).normalized();u=Vector((1,0,0));w=axis.cross(u).normalized();q=v.co-c
  v.co=c+u*(q.dot(u)*factor)+w*(q.dot(w)*factor)+axis*q.dot(axis)
 # Replace each pointed ellipsoid with a finite, flat top/bottom folded cloth strip.
 for o in list(bpy.data.objects):
  if not o.name.startswith('CURTAIN_fold_proxy_'):continue
  material=o.data.materials[0];vs=[];steps=12
  for side in [0,1]:
   for z in [-1.55,1.55]:
    for k in range(steps+1):
     x=-.11+.22*k/steps;y=-.06*math.cos(2*math.pi*k/steps)+(side*.012);vs.append((x,y,z))
  fs=[];n=steps+1
  for side in range(2):
   for k in range(steps):
    a=side*2*n+k;f=(a,a+1,a+n+1,a+n);fs.append(f if side==0 else tuple(reversed(f)))
  for zrow in [0,1]:
   for k in range(steps):
    a=zrow*n+k;f=(a,a+2*n,a+2*n+1,a+1);fs.append(f if zrow==0 else tuple(reversed(f)))
  fs += [(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)]
  d=bpy.data.meshes.new(o.name+'_R02_mesh');d.from_pydata(vs,[],fs);d.update();o.data=d;o.data.materials.append(material)
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R02_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R02_{mode}.glb'),export_format='GLB',export_cameras=True)
 records.append({'mode':mode,'changed':'two horizontal frame meshes, umbrella canopy, 28 curtain meshes','unchanged':'other objects/cameras/lights/world; no source calibration','scope':'local hypothesis, not whole room'})
(P/'qa/R02-change-record.json').write_text(json.dumps(records,indent=2))
