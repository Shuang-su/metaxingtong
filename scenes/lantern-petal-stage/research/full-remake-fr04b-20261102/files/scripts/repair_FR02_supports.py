# Technical contact repair only: preserve FR01 failed checkpoint and all layout/camera parameters.
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/FR01_material.blend'));s=bpy.context.scene;changes=[]
def rod(n,a,b,r,material):
 a=Vector(a);b=Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(material);o['evidence_grade']='C-minimal inferred technical attachment, source joinery not verified';return o
for o in list(s.objects):
 if not(o.type=='MESH' and o.name.startswith('COL_') and o.name.endswith('_roof_support')):continue
 side=o.name.split('_')[1];roof=bpy.data.objects['ROOF_'+side+'_thick_curved_solid'];x,y=o.location.x,o.location.y;ok,hit,normal,face=roof.ray_cast(Vector((x,y,4.31)),Vector((0,0,1)))
 assert ok,(o.name,'roof underside no intersection');before_top=o.location.z+o.dimensions.z/2;bottom=4.27;top=hit.z+.012;o.dimensions.z=top-bottom;o.location.z=(top+bottom)/2;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False);changes.append({'object':o.name,'old_top':before_top,'actual_mesh_roof_bottom_ray_hit':hit.z,'new_top':top,'roof_overlap_work_units':.012,'column_cap_overlap_work_units':.03})
bronze=bpy.data.materials['bronze_work_approx'];added=[]
for o in list(s.objects):
 if o.name.startswith('ROUND_') and o.name.endswith('_hang'):
  x,y=o.location.x,o.location.y;r=(x*x+y*y)**.5;a=(x,y,4.25);b=(x/r*7.28,y/r*7.28,4.25);n=o.name+'_beam_attachment';rod(n,a,b,.025,bronze);added.append(n)
# Both ends of the three crossing strings terminate below finite eaves; add explicit vertical ties.
P=json.load(open(D/'parameters.json'))
import math
for row,a in enumerate(P['cross_string_angles_degrees']):
 x=6.95*math.cos(math.radians(a));y=6.95*math.sin(math.radians(a))
 for side,sign in [('L',-1),('R',1)]:
  n=f'STRING_row{row}_{side}_eave_tie';rod(n,(sign*x,y,4.105),(sign*x,y,4.43),.012,bronze);added.append(n)
q={'scope':'technical support connectivity only, not source validation','roof_supports_changed':changes,'inferred_attachments_added':added,'layout_cameras_unchanged':True,'FR01_not_overwritten':True,'not_closed':['entrance turn module absent','full lattice/rail/urn cutouts/flowers','unique source mapping/calibration','all contacts not exhaustively checked']};(D/'qa/FR02-support-repair.json').write_text(json.dumps(q,indent=2))
for typ in ['material','white']:
 if typ=='white':
  m=bpy.data.materials.get('WHITE_SHARED') or bpy.data.materials.new('WHITE_SHARED');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/FR02_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/FR02_{typ}.glb'),export_format='GLB')
files=[]
for f in sorted((D/'models').glob('FR02*')):files.append({'file':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(D/'qa/FR02-checkpoint-files.json').write_text(json.dumps(files,indent=2));print('FR02 SAVED; no render')
