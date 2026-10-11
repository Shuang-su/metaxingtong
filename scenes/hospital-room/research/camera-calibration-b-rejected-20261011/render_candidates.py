import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/camera_calibration_b');base=r.parent/'candidate_b/hospital_endboard_shape_B.blend';fit=json.loads((r/'fit_results.json').read_text())
def fingerprint():
 d={'objects':[],'materials':[],'world':{},'collections':[]}
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  if o.type=='CAMERA':continue
  a={'name':o.name,'type':o.type,'matrix':[list(x) for x in o.matrix_world],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'visible_camera':o.visible_camera,'materials':[s.material.name if s.material else None for s in o.material_slots]}
  if o.type=='MESH':a.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],material_indices=[p.material_index for p in o.data.polygons])
  if o.type=='LIGHT':a.update(light_type=o.data.type,energy=o.data.energy,color=list(o.data.color))
  d['objects'].append(a)
 for m in sorted(bpy.data.materials,key=lambda x:x.name):
  d['materials'].append({'name':m.name,'diffuse':list(m.diffuse_color),'nodes':[(n.name,n.type,[(p.name,str(p.default_value)) for p in n.inputs if hasattr(p,'default_value')]) for n in m.node_tree.nodes] if m.use_nodes else []})
 for c in bpy.data.collections:d['collections'].append([c.name,c.hide_render,c.hide_viewport])
 if bpy.context.scene.world and bpy.context.scene.world.use_nodes:d['world']=[(n.name,n.type,[(p.name,str(p.default_value)) for p in n.inputs if hasattr(p,'default_value')]) for n in bpy.context.scene.world.node_tree.nodes]
 s=json.dumps(d,sort_keys=True);return hashlib.sha256(s.encode()).hexdigest()
def assign(cam,x):
 v=Vector(x[:3]);q=v.normalized().to_track_quat('Z','Y') if False else None
 from mathutils import Quaternion
 R=Quaternion(v.normalized(),v.length).to_matrix().to_4x4();R.translation=Vector(x[3:6]);cam.matrix_world=R;cam.data.lens=math.exp(x[6]);cam.data.shift_x=-x[7]/1920;cam.data.shift_y=x[8]/1920
bpy.ops.wm.open_mainfile(filepath=str(base));before=fingerprint();s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_denoising=False
for vl in s.view_layers:vl.cycles.use_denoising=False
names={'F':'MATCH_F_Turning_Right','G':'MATCH_G_Sofa_And_Bed','H':'MATCH_H'}
for tag,mode in [('F','pose6'),('G','pose_focal7')]:assign(bpy.data.objects[names[tag]],fit[tag]['candidates'][mode]['parameters'])
bpy.context.view_layer.update();after=fingerprint();assert before==after
s.camera=bpy.data.objects[names['G']];s.render.filepath=str(r/'G_candidate_camera_raw.png');bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_B_camera_candidate_NOT_ADOPTED.blend'))
meta={'base_blend_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'base_pr37_sha':'e3ffa57208e2b382a39fc3a7c3972a5958d9845b','shared_state_before_sha256':before,'shared_state_after_sha256':after,'shared_geometry_material_lights_visibility_unchanged':before==after,'object_count':len(bpy.data.objects),'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'engine':s.render.engine,'samples':s.cycles.samples,'denoising':False,'resolution':[1920,1080],'blender_version':bpy.app.version_string,'display_device':s.display_settings.display_device,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'cameras':{},'no_warp':True,'no_visibility_changes':True,'candidate_status':'RESEARCH_NOT_ADOPTED'}
for tag,n in names.items():
 c=bpy.data.objects[n];meta['cameras'][tag]={'name':n,'matrix_world':[list(v) for v in c.matrix_world],'lens_mm':c.data.lens,'shift_x':c.data.shift_x,'shift_y':c.data.shift_y,'clip_start':c.data.clip_start,'clip_end':c.data.clip_end,'sensor_width':c.data.sensor_width,'sensor_fit':c.data.sensor_fit}
(r/'render_manifest.json').write_text(json.dumps(meta,indent=2))
for tag in ['G','F','H']:
 s.camera=bpy.data.objects[names[tag]];s.render.filepath=str(r/f'{tag}_candidate_camera_raw.png');bpy.ops.render.render(write_still=True)
# diagnostic alternative, real camera only; do not resave the main candidate
assign(bpy.data.objects[names['G']],fit['G']['candidates']['pose6']['parameters']);s.camera=bpy.data.objects[names['G']];s.render.filepath=str(r/'G_fixed_focal_alternative_raw.png');bpy.ops.render.render(write_still=True)
