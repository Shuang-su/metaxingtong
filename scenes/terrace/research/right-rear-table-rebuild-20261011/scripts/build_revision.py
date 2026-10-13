import bpy,math,json,hashlib,pathlib,bmesh
from mathutils import Vector,Matrix
P=pathlib.Path(__file__).resolve().parent;D=P/'delivery';D.mkdir(exist_ok=True)
col=bpy.data.collections['07_Moon_Side_Table']; names={o.name for o in col.all_objects}
def snapshot():
 out={}
 for o in bpy.data.objects:
  if o.name in names:continue
  d={'type':o.type,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}
  if o.type=='MESH':d['mesh']=hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
  if o.type in ['CAMERA','LIGHT']:d['data']={p.identifier:str(getattr(o.data,p.identifier)) for p in o.data.bl_rna.properties if p.type in ['FLOAT','INT','BOOLEAN','ENUM','STRING'] and p.identifier!='name'}
  out[o.name]=d
 return out
before=snapshot(); (D/'unrelated_before.json').write_text(json.dumps(before))
cx,cy=3.52,2.8902972
black=bpy.data.objects['Side_table_round_top'].data.materials[0]
def replace(o,vs,fs):
 mesh=bpy.data.meshes.new(o.name+'_revised');mesh.from_pydata(vs,[],fs);mesh.update();mesh.materials.append(black);o.data=mesh;o.matrix_world=Matrix.Identity(4)
 for p in mesh.polygons:p.use_smooth=False
# Lathe closed shallow tray: broad recessed face, raised thin lip. zmax .744, supported props retain old .83 contact minus .10.
profile=[(0,.719),(.411,.719),(.433,.724),(.437,.741),(.426,.746),(.413,.734),(0,.734)]
vs=[(cx,cy,profile[0][1])];fs=[];N=128
for r,z in profile[1:-1]:
 for j in range(N):a=2*math.pi*j/N;vs.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
for j in range(N):fs.append((0,1+(j+1)%N,1+j))
for k in range(len(profile)-3):
 for j in range(N):a=1+k*N+j;b=1+k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
top=len(vs);vs.append((cx,cy,profile[-1][1]));last=1+(len(profile)-3)*N
for j in range(N):fs.append((last+j,last+(j+1)%N,top))
replace(bpy.data.objects['Side_table_round_top'],vs,fs)
# White inner object remains explicitly unidentified. Ellipsoid: width .64, height .39.
o=bpy.data.objects['White_sphere_under_table'];w=[o.matrix_world@v.co for v in o.data.vertices]
inv=o.matrix_world.inverted()
for v,p in zip(o.data.vertices,w):v.co=inv@Vector((cx+(p.x-cx)*(.32/.26),cy+(p.y-cy)*(.32/.26),.25+(p.z-.29)*(.195/.26)))
# Continuous broad rectangular strips, radial thickness .014, tangential width .040.
# Lower bowl follows a larger enclosing ellipse; top rises continuously to shallow tray underside.
def radius(z):
 if z<=.25:return .32*math.sqrt(max(0,1-((z-.25)/.225)**2))+.030
 t=(z-.25)/(.724-.25);return .35+(.416-.35)*(t*t*(3-2*t))
legs=sorted([o for o in col.objects if o.name.startswith('Side_table_curved_cage_leg')],key=lambda o:o.name)
for o in legs:bpy.data.objects.remove(o,do_unlink=True)
for k in range(10):
 a=-math.pi/2+k*2*math.pi/10;rad=Vector((math.cos(a),math.sin(a),0));tan=Vector((-math.sin(a),math.cos(a),0));vs=[];fs=[]
 for j in range(101):
  z=.035+(.725-.035)*j/100;r=radius(z);c=Vector((cx,cy,z))+r*rad
  # plane normal follows curve so ribbon thickness stays constant on lower arc
  dz=.00001;dr=(radius(min(.725,z+dz))-radius(max(.035,z-dz)))/(min(.725,z+dz)-max(.035,z-dz));n=(rad-Vector((0,0,dr))).normalized()
  for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]:vs.append(tuple(c+s*.020*tan+t*.007*n))
 for j in range(100):
  for q in range(4):fs.append((4*j+q,4*j+(q+1)%4,4*(j+1)+(q+1)%4,4*(j+1)+q))
 fs.extend([(3,2,1,0),(400,401,402,403)])
 mesh=bpy.data.meshes.new('Cage_flat_ribbon');mesh.from_pydata(vs,[],fs);mesh.materials.append(black);mesh.update();ob=bpy.data.objects.new('Side_table_flat_rib_%02d'%k,mesh);col.objects.link(ob)
# Lower thin foot ring inferred, visible source foot contour.
vs=[];fs=[]
for r,z in [(0.10,.026),(.14,.026),(.14,.037),(.10,.037)]:
 for j in range(96):a=2*math.pi*j/96;vs.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
for k in range(4):
 for j in range(96):fs.append((k*96+j,k*96+(j+1)%96,((k+1)%4)*96+(j+1)%96,((k+1)%4)*96+j))
mesh=bpy.data.meshes.new('Cage_lower_ring');mesh.from_pydata(vs,[],fs);mesh.materials.append(black);ob=bpy.data.objects.new('Side_table_lower_ring_INFERRED',mesh);col.objects.link(ob)
# Preserve accessory geometry/materials; only seat existing approximations on lower tray.
for o in col.objects:
 if o.name not in ['Side_table_round_top','White_sphere_under_table'] and not o.name.startswith('Side_table_'):o.location.z-=.096
# Collapse axis duplicates to true closed tray fans and orient revised closed surfaces outwards.
for ob in col.objects:
 if ob.name.startswith('Side_table_'):
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
bpy.context.view_layer.update();names.update(o.name for o in col.all_objects)
after=snapshot();assert before==after
(D/'unrelated_freeze_validation.json').write_text(json.dumps({'passed':before==after,'unrelated_objects':len(before),'scope':'geometry, materials slots, world transforms, visibility, cameras and lamps','table_object_names':sorted(names)},indent=2))
(D/'table_names.json').write_text(json.dumps(sorted(names)))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'Terrace_RightRearTable_Rebuilt_20261011.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in col.all_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'Terrace_RightRearTable_Only.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
print('BUILD_DONE')
