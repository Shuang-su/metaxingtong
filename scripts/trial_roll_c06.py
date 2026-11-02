import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/C05_remade_materials.blend'));s=bpy.context.scene;q=json.load(open(R/'qa/roll_c06/conditional_fit.json'))['nominal_candidate'];a=Vector(q['bottom_axis_center_working']);b=Vector(q['top_axis_center_working']);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1))).normalized();v=axis.cross(u);canvas=bpy.data.objects['P01_roll'].data.materials[0];pink=bpy.data.objects['P01_roll_band'].data.materials[0]
def hashes():
 dg=bpy.context.evaluated_depsgraph_get();out={}
 for o in s.objects:
  if o.type not in {'MESH','CURVE'} or o.name.startswith('P01_'):continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();out[o.name]=hashlib.sha256(json.dumps([tuple(ev.matrix_world@x.co) for x in me.vertices]).encode()).hexdigest();ev.to_mesh_clear()
 return out
before=hashes();cams={o.name:[list(row) for row in o.matrix_world] for o in s.objects if o.type=='CAMERA'}
for o in list(s.objects):
 if o.name.startswith('P01_'):bpy.data.objects.remove(o,do_unlink=True)
def cylinder(name,A,B,rad,mat):
 N=24;verts=[];faces=[]
 for c in [A,B]:
  for i in range(N):ang=math.tau*i/N;verts.append(c+rad*(math.cos(ang)*u+math.sin(ang)*v))
 for i in range(N):j=(i+1)%N;faces.append((i,j,j+N,i+N))
 faces.extend([tuple(reversed(range(N))),tuple(range(N,2*N))]);me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return o
roll=cylinder('P01_roll',a,b,.32,canvas)
for i,t in enumerate([.25,.77]):c=a.lerp(b,t);cylinder('P01_roll_band'+('' if i==0 else '.001'),c-axis*.033,c+axis*.033,.328,pink)
report={'stage':'C06 nominal fixed-radius .32 soft two-source roll candidate','other_evaluated_world_geometry_equal':before==hashes(),'all_camera_matrices_equal':cams=={o.name:[list(row) for row in o.matrix_world] for o in s.objects if o.type=='CAMERA'},'actual_roll_min_z':min(x.co.z for x in roll.data.vertices),'ground_constraint':'inferred support tangency, NOT observed bottom point','source_fit_limit':'some residuals still exceed5/6/8px; radius.36 profile smaller training cost not substituted for predeclared nominal .32','source_status':'FAIL/PENDING','third_used_to_fit':False};(R/'qa/roll_c06/actual_model_changes.json').write_text(json.dumps(report,indent=2));bpy.context.preferences.filepaths.save_version=0;s.render.threads=2;s.cycles.samples=12;s.cycles.use_denoising=False;bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C06_roll_trial_materials.blend'))
boxes={1:(100,440,300,650),2:(540,300,740,490)}
for role in ['materials','white']:
 if role=='white':
  white=bpy.data.materials['WHITE_GEOMETRY_PERSISTENT'];white.use_fake_user=True
  for o in s.objects:
   if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(white)
  bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C06_roll_trial_white.blend'))
 for i,box in boxes.items():
  s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=box[0]/1920;s.render.border_max_x=box[2]/1920;s.render.border_min_y=1-box[3]/1080;s.render.border_max_y=1-box[1]/1080;s.render.filepath=str(R/f'renders/C06_SOURCE{i}_roll_{role}_native_crop.png');bpy.ops.render.render(write_still=True)
  if role=='materials':
   s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=960;s.render.resolution_y=540;s.render.filepath=str(R/f'renders/C06_SOURCE{i}_materials_960.png');bpy.ops.render.render(write_still=True)
 s.render.use_border=False;s.render.use_crop_to_border=False
(R/'qa/roll_c06/crop_coordinates.json').write_text(json.dumps({'source_grid':{'width':1920,'height':1080},'native_crop_boxes':boxes,'no_pixel_warp':True},indent=2));print('C06_TRIAL_DONE')
