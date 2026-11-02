import bpy,bmesh,json,hashlib
from mathutils import Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/C04_partial_materials.blend'));s=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
for o in s.objects:
 if o.name.startswith('V04_open_tuft'):o.location.z=0
q=json.load(open(R/'qa/third_conditions/cameras_for_render.json'))
for c in q['cameras']:
 bpy.ops.object.camera_add();o=bpy.context.object;o.name=f"SOURCE3_CONDITIONAL_F{c['focal_px']}_NOT_BLIND";o.matrix_world=Matrix(c['matrix_world']);o.data.lens=c['lens_mm'];o.data.sensor_width=c['sensor_width_mm'];o.data.sensor_fit=c['sensor_fit'];o.data.clip_end=500
s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.use_denoising=False;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100

def inventory():
 out=[];points={};dg=bpy.context.evaluated_depsgraph_get()
 for o in sorted(s.objects,key=lambda a:a.name):
  if o.type not in {'MESH','CURVE'}:continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);p=[tuple(ev.matrix_world@v.co) for v in me.vertices];out.append({'name':o.name,'vertices':len(p),'triangles':len(me.loop_triangles),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-10 for f in bm.faces),'zero_edges':sum(e.calc_length()<1e-8 for e in bm.edges),'zmin':min(a[2] for a in p),'zmax':max(a[2] for a in p),'position_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest(),'open_sheet_intended':o.name.startswith('V04_open_tuft')});points[o.name]=p;bm.free();ev.to_mesh_clear()
 return out,points
inv,points=inventory();sig=hashlib.sha256(json.dumps(inv,sort_keys=True).encode()).hexdigest();(R/'qa/C05_inventory.json').write_text(json.dumps({'objects':inv,'geometry_signature':sig,'limits':'topology and positions not source acceptance or exhaustive collision validation'},indent=2));(R/'qa/C05_export_expected_vertices.json').write_text(json.dumps(points,separators=(',',':')));s.camera=bpy.data.objects['CHECK_MAIN'];s.render.resolution_x=1440;s.render.resolution_y=1080;bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C05_remade_materials.blend'))
# Explicitly clear original scene selection, avoiding the old R08 duplicate-object export bug.
bpy.ops.object.select_all(action='DESELECT');original=s;exp=bpy.data.scenes.new('C05_EXPORT_EVALUATED')
for o in list(original.objects):
 if o.type not in {'MESH','CURVE'}:continue
 bpy.context.window.scene=original;dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me.transform(ev.matrix_world);copy=bpy.data.objects.new(o.name,me);exp.collection.objects.link(copy)
bpy.context.window.scene=exp;bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(R/'models/C05_remade.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True);bpy.context.window.scene=original;bpy.data.scenes.remove(exp)
white=bpy.data.materials.get('WHITE_GEOMETRY_PERSISTENT');white.use_fake_user=True
for o in s.objects:
 if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(white)
inv2,_=inventory();sig2=hashlib.sha256(json.dumps(inv2,sort_keys=True).encode()).hexdigest();(R/'qa/C05_white_same_geometry.json').write_text(json.dumps({'materials':sig,'white':sig2,'equal':sig==sig2,'grass_base_change_from_C04':'.002 to0 work units, no new fit','third_f2500':'nominal representative matching original source-pair focal, not selected using rear-box errors','source_gate':'FAIL/PENDING; no later independent replay'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C05_remade_white.blend'));print('C05_MODELS_SAVED',flush=True)

def render(role,cam,path,w,h,samples):
 dst=R/'renders'/path
 if dst.exists():print('PRESERVE_EXISTING',path);return
 model=R/f'models/C05_remade_{role}.blend'
 if bpy.data.filepath!=str(model):bpy.ops.wm.open_mainfile(filepath=str(model))
 s=bpy.context.scene;s.camera=bpy.data.objects[cam];s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;s.cycles.samples=samples;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=str(dst);bpy.ops.render.render(write_still=True)
for role in ['materials','white']:
 for i in [1,2]:render(role,f'SOURCE_CONDITIONAL_{i}',f'C05_SOURCE{i}_{role}_1920.png',1920,1080,16 if role=='materials' else 12)
 render(role,'SOURCE3_CONDITIONAL_F2500_NOT_BLIND',f'C05_SOURCE3_F2500_NOT_BLIND_{role}_1920.png',1920,1080,16 if role=='materials' else 12)
 render(role,'CHECK_MAIN',f'C05_MAIN_CHECK_{role}.png',1440,1080,20 if role=='materials' else 12)
for i in range(1,9):render('materials',f'CHECK_{i:02}',f'C05_CHECK_{i:02}_materials.png',960,720,12)
for f in [1800,2500,3200]:render('materials',f'SOURCE3_CONDITIONAL_F{f}_NOT_BLIND',f'C05_SOURCE3_F{f}_NOT_BLIND_960.png',960,540,8)
print('C05_PACKAGE_DONE',flush=True)
