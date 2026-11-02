import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/C01_remade_materials.blend'));s=bpy.context.scene;changes=[]
for o in list(s.objects):
 if o.name.startswith('B01_'):o.location.y+=.25
body=bpy.data.objects['B01_body'];body.dimensions.z=.456;body.location.z=.228;changes.append('B01 centreY +.25 historical working-box origin correction; body top .456 meets lid base, no sourcecam change')
# Weld coincident roof apex vertices before Solidify, no new cap/hidden surface.
for o in s.objects:
 if o.name.startswith('T01_roof_') and o.type=='MESH' and not 'hem' in o.name:
  bm=bmesh.new();bm.from_mesh(o.data);before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);changes.append({'object':o.name,'apex_vertices_before':before,'after':len(bm.verts)});bm.free()
for o in list(s.objects):
 if o.type=='CURVE' and not o.data.splines[0].use_cyclic_u:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();changes.append({'object':o.name,'fix':'weld existing cap rings; no holes filled'})
# Roll assembly shifts together until actual evaluated cylinder touches ground.
o=bpy.data.objects['P01_roll'];zmin=min((o.matrix_world@v.co).z for v in o.data.vertices)
for ob in s.objects:
 if ob.name.startswith('P01_'):ob.location.z-=zmin
changes.append({'assembly':'P01','old_min_z':zmin,'shift_z':-zmin})
# Tilted cylindrical feet: solve lower cap contact while retaining upper attachment endpoint.
for o in s.objects:
 if not o.name.startswith(('C01_cross_A','C01_cross_B')):continue
 zs=[v.co.z for v in o.data.vertices];oldlen=max(zs)-min(zs);a=o.matrix_world@Vector((0,0,min(zs)));b=o.matrix_world@Vector((0,0,max(zs)));dxy=Vector((b.x-a.x,b.y-a.y,0)).length;z=a.z
 for k in range(30):z=.025*dxy/math.sqrt(dxy*dxy+(b.z-z)**2)
 a.z=z;newlen=(b-a).length;o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.scale.z=newlen/oldlen;changes.append({'object':o.name,'lower_cap_centre_z':z,'upper_endpoint_unchanged':list(b)})
bpy.context.preferences.filepaths.save_version=0;s.camera=bpy.data.objects['CHECK_MAIN'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C02_repaired_materials.blend'));white=bpy.data.materials.get('WHITE_GEOMETRY_PERSISTENT')
if white is None:
 white=bpy.data.materials.new('WHITE_GEOMETRY_PERSISTENT');white.use_nodes=True;white.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.7,.7,.7,1)
white.use_fake_user=True
for o in s.objects:
 if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C02_repaired_white.blend'));(R/'qa/C02_changes.json').write_text(json.dumps({'stage':'new remake C02, C01 failures retained','changes':changes,'source_cameras':'unchanged','source_acceptance':'FAIL/PENDING'},indent=2))
for cam in ['SOURCE_CONDITIONAL_1','SOURCE_CONDITIONAL_2']+[f'CHECK_{i:02}' for i in range(1,9)]:
 s.camera=bpy.data.objects[cam];s.cycles.samples=8;s.render.threads=2;s.render.filepath=str(R/f'renders/C02_{cam}_white.png');bpy.ops.render.render(write_still=True)
print('C02_DONE')
