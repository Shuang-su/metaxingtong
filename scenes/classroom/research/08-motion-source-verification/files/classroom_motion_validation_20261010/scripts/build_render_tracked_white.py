import bpy,json,re,math
from pathlib import Path
from mathutils import Vector
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010');q=p/'tracked_desks_white';j=json.load(open(q/'qa/two_rectangle_fits.json'));s=bpy.context.scene;removed=[]
for o in list(bpy.data.objects):
 if re.match(r'^(R[1-4]C[1-4]\b|V4 R[2-4]Outer[LR]\b|V4 ObservedRearD\d+\b)',o.name) or o.name.startswith(('Desk front empty label mount','Desk perforated ochre front rail')):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
clay=bpy.data.materials.new('Observed constraint clay');clay.diffuse_color=(.65,.68,.71,1);clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.65,.68,.71,1);bs.inputs['Roughness'].default_value=.65
for o in bpy.data.objects:
 if o.type!='MESH':continue
 transparent=False
 for m in o.data.materials:
  if m and m.use_nodes:
   for node in m.node_tree.nodes:
    if node.type=='BSDF_PRINCIPLED' and node.inputs.get('Transmission Weight') and node.inputs['Transmission Weight'].default_value>.5:transparent=True
 if not transparent:o.data.materials.clear();o.data.materials.append(clay)
colors=[(.18,.5,.7,1),(.75,.4,.12,1)]
def box(name,loc,dim,angle,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;o.rotation_euler.z=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
for desk,color in zip(j['desks'],colors):
 cx,cy,w,d,t=desk['rectangle_parameters_cx_cy_width_depth_angle'];z=desk['tabletop_z'];mat=bpy.data.materials.new(desk['source_id']+' evidence color');mat.use_nodes=True;mat.diffuse_color=color;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color
 box(desk['source_id']+' observed rectangular top',(cx,cy,z-.012),(w,d,.024),t,mat)
 # Legs are a generic support hypothesis, not measured feet. No unobserved chairs or additional tables.
 for a in [-1,1]:
  for b in [-1,1]:
   dx=a*(w/2-.04);dy=b*(d/2-.04);x=cx+math.cos(t)*dx-math.sin(t)*dy;y=cy+math.sin(t)*dx+math.cos(t)*dy;box(desk['source_id']+' inferred support '+str(a)+str(b),(x,y,(z-.024)/2),(.018,.018,z-.024),t,clay)
for c in j['cameras']:
 data=bpy.data.cameras.new('JOINT_'+c['name']);o=bpy.data.objects.new(data.name,data);s.collection.objects.link(o);o.location=c['location'];o.rotation_euler=c['rotation_xyz'];data.lens=c['lens_mm'];data.sensor_width=36
s['status']='Two observed desks constraint whitebox; NOT complete furniture; other source tables unresolved, not asserted absent';s['window_geometry']='Six-bay trial retains old pitch; metric window size unresolved';s.camera=bpy.data.objects['JOINT_F_path_073'];bpy.ops.wm.save_as_mainfile(filepath=str(q/'Classroom_TwoTrackedDesks_WHITE_CANDIDATE.blend'),compress=True)
(q/'qa/white_model_scope.json').write_text(json.dumps({'removed_old_unverified_student_group_objects':removed,'desk_count_modelled':2,'desk_count_of_room':None,'other_visible_tables':'Unmodelled constraints, not claimed absent','generic_legs':'Inferred supports only, not verified foot correspondence','frozen_original_modified':False},indent=2))
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=False;s.cycles.samples=16;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for n in ['F_path_073']:
 s.camera=bpy.data.objects['JOINT_'+n];s.render.filepath=str(q/'renders'/(n+'.png'));bpy.ops.render.render(write_still=True)
