"""C3 width-only continuation from failed C2; retains explicit unresolved column-depth hypothesis."""
import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;W=json.load(open(R/'drape_width_screen.json'));s=bpy.context.scene;out=R/'renders_C3';out.mkdir(exist_ok=True);models=R/'models'
o=bpy.data.objects['Curtain • rebuilt uniform eight-fold drape'];inv=o.matrix_world.inverted();xmin=W['fixed_left_x']
for v in o.data.vertices:
 p=o.matrix_world@v.co;p.x=xmin+(p.x-xmin)*W['scale_x'];v.co=inv@p
o.data.update();o['C3_edit']='Shared X width scale %.12f at fixed left boundary; same geometry in all views. Eight-fold topology unverified.'%W['scale_x'];s['candidate_status']='UNACCEPTED: partial silhouette/physical improvement only; column depth, fold topology, camera-bed, lighting unresolved'
def fp():return hashlib.sha256(json.dumps({o.name:{'v':[list(o.matrix_world@v.co) for v in o.data.vertices],'p':[list(p.vertices) for p in o.data.polygons],'hide_render':o.hide_render} for o in bpy.data.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
s.camera=bpy.data.objects['MATCH_G_Sofa_And_Bed'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(models/'hospital_C3_width_refinement_UNACCEPTED.blend'));geo=fp()
mats={o.name:list(o.data.materials) for o in bpy.data.objects if o.type=='MESH'};white=bpy.data.materials.get('C2 white geometry inspection')
for o in bpy.data.objects:
 if o.type=='MESH' and 'closed_glass' not in o.name and not o.name.startswith('Approximate city'):o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(models/'hospital_C3_width_refinement_WHITE_UNACCEPTED.blend'))
for o in bpy.data.objects:
 if o.type=='MESH':
  o.data.materials.clear()
  for m in mats[o.name]:o.data.materials.append(m)
bpy.ops.export_scene.gltf(filepath=str(models/'hospital_C3_width_refinement_UNACCEPTED.glb'),export_format='GLB',use_selection=False,export_cameras=True,export_lights=True,export_apply=True)
# Actual requested source-camera renders at native size.
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True; s.view_layers[0].cycles.use_denoising=False; # inherited raw-noise layer state, explicitly retained
s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';manifest=[]
for k,n in [('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H'),('F','MATCH_F_Turning_Right'),('N640','C2_N640_static_background_hypothesis')]:
 s.camera=bpy.data.objects[n];s.render.filepath=str(out/f'{k}_C3_RAW_1920x1080.png');before=fp();t=time.time();bpy.ops.render.render(write_still=True);p=Path(s.render.filepath);manifest.append({'view':k,'file':p.name,'camera':n,'camera_matrix':[list(r) for r in s.camera.matrix_world],'lens_mm':s.camera.data.lens,'size':[1920,1080],'seconds':time.time()-t,'samples':16,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'fingerprint_before':before,'fingerprint_after':fp(),'same_geometry':before==fp(),'image_transform':'none; raw Blender output'});(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# 8 ordinary inside-room diagnostic views. No cutaway or per-camera hidden geometry.
inspect=R/'inspection_C3';inspect.mkdir(exist_ok=True);s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.72,.72,.72);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_specular_highlight=False
for i in range(1,9):
 cam=next(o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('VIEW_%02d_'%i));s.camera=cam;s.render.filepath=str(inspect/f'{cam.name}_diagnostic_960x540.png');bpy.ops.render.render(write_still=True)
(R/'C3_model_manifest.json').write_text(json.dumps({'candidate_status':'UNACCEPTED','mesh_fingerprint':geo,'models':[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in models.glob('*C3*')],'shared_geometry_per_source_view':all(x['same_geometry'] for x in manifest),'global_width_scale':W['scale_x'],'no_existing_visibility_changes':True,'diagnostic_views':8,'inspection_engine':'Workbench studio lighting, not source lighting'},ensure_ascii=False,indent=2))
