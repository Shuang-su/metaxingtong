"""Build one actual bounded profile; retain B1 frozen-camera baseline separately.
No per-view geometry, light or material switches. A-pillar bound-hit remains numeric.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];S=R.parents[1]
fit=json.loads((R/'fit_result.json').read_text());p=fit['dashboard_parameters']
bpy.ops.wm.open_mainfile(filepath=str(S/'models/car_passenger_cabin_material.blend'))
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
def digest():
 rows=[]
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  rows.append([o.name,[[float(c) for c in v.co] for v in o.data.vertices],[list(x.vertices) for x in o.data.polygons],[list(row) for row in o.matrix_world],o.hide_render])
 return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
before=digest();original={o.name:hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],[tuple(row) for row in o.matrix_world],o.hide_render)).encode()).hexdigest() for o in s.objects if o.type=='MESH'}
for id,row in fit['results'].items():
 q=row['camera'];yaw,pitch,roll=q[3:6];f=Vector((math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)));right=Vector((math.sin(yaw),-math.cos(yaw),0));up=right.cross(f);rr=right*math.cos(roll)+up*math.sin(roll);uu=-right*math.sin(roll)+up*math.cos(roll)
 c=bpy.data.objects['SRC_'+id+('_open' if id=='S02' else '_closed')];c.location=q[:3];c.rotation_euler=Matrix((rr,uu,-f)).transposed().to_euler();c.data.lens=q[6];c['calibration']='r03 frozen small yaw/pitch diagnostic; bounds hit, not accepted'
assert before==digest()
s['status']='r03 B1 original geometry, frozen r03 cameras; diagnostic only'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/B1_frozen_camera_baseline.blend'))
dy,tilt,thick,scale,h=p;F=.637+dy;TOP=1.0325;FT=TOP-thick+.0025;rot=Matrix.Rotation(tilt,3,'X');anchor=Vector((0,.637,.94));newanchor=Vector((0,F,FT))
def tr(v):return rot@(Vector(v)-anchor)+newanchor
def repair(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
def replace_box(name,loc,dim,radius):
 old=bpy.data.objects[name];metadata=dict(old.items());mats=list(old.data.materials);collection=old.users_collection[0];bpy.data.objects.remove(old,do_unlink=True)
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for k,v in metadata.items():o[k]=v
 for m in mats:o.data.materials.append(m)
 if collection not in o.users_collection:collection.objects.link(o)
 for col in list(o.users_collection):
  if col!=collection:col.objects.unlink(o)
 mod=o.modifiers.new('shared_physical_bevel','BEVEL');mod.width=radius;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 for face in o.data.polygons:face.use_smooth=True
 mod=o.modifiers.new('weighted_normals','WEIGHTED_NORMAL');mod.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
top=replace_box('D01_dashboard_top',(.38,((F-.007)+1.19)/2,TOP-thick/2),(1.30,1.19-(F-.007),thick),min(.045,thick*.49))
fas=replace_box('D02_dashboard_end_fascia',(.38,.787,.745),(1.30,.30,.39),.025)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.112*scale,depth=.7,location=(.8,.78,.77+h),rotation=(math.pi/2,0,0));cut=bpy.context.object
bpy.context.view_layer.objects.active=fas;mod=fas.modifiers.new('true_scaled_shared_vent_opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
changed=[]
for o in list(s.objects):
 if o.type!='MESH' or not o.name.startswith('D'):continue
 if o.name!='D01_dashboard_top':
  # Mesh vertices enter world space once, then one common profile transform.
  world=o.matrix_world.copy();inv=world.inverted()
  for v in o.data.vertices:
   w=world@v.co
   if o.name.startswith(('D03','D04','D05','D06')):w.x=.8+(w.x-.8)*scale;w.z=.77+(w.z-.77)*scale+h
   v.co=inv@tr(w)
 repair(o)
 if o.name in ['D01_dashboard_top','D02_dashboard_end_fascia']:
  uv=o.data.uv_layers.new(name='UV_synthetic_repeat')
  for face in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in face.loop_indices:
    co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]*4,co[axes[1]]*4)
 o['r03_shared_profile']='All sources share five bounded physical parameters; radius applies to hole/rim/wall/end/louvers, not rim alone'
 changed.append(o.name)
bpy.context.view_layer.update()
unchanged={}
for o in s.objects:
 if o.type=='MESH' and o.name not in changed:
  now=hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],[tuple(row) for row in o.matrix_world],o.hide_render)).encode()).hexdigest();unchanged[o.name]=now==original[o.name]
assert all(unchanged.values())
s['status']='r03 D1 shared dashboard/vent bounded diagnostic; not accepted; A numeric trial not applied'
s['r03_parameter_json']=json.dumps(dict(zip(fit['dashboard_parameter_names'],p)))
s['r03_A_status']='No A/window/mirror geometry edit: two-parameter A fit hits curvature bound and leaves large multiview edge error'
s.cycles.samples=32;s.cycles.use_denoising=False;s.camera=bpy.data.objects['MAIN_passenger_local'];s.frame_set(1)
bpy.ops.file.pack_all();material_digest=digest();bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/D1_shared_dashboard_material.blend'))
white=bpy.data.materials.get('WHITE_same_geometry')
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
assert digest()==material_digest
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/D1_shared_dashboard_white.blend'))
(R/'qa/build_identity.json').write_text(json.dumps({'status':'diagnostic not accepted','changed_meshes':changed,'unchanged_meshes_exact':unchanged,'all_non_dashboard_unchanged':all(unchanged.values()),'material_geometry_digest':material_digest,'white_geometry_digest':digest(),'same_geometry':True,'A_numeric_only':True,'state_mapping':{'S01':1,'S02':2,'S03':1},'parameters':dict(zip(fit['dashboard_parameter_names'],p))},indent=2)+'\n')
print('BUILT_D1',changed,'UNCHANGED',len(unchanged))
