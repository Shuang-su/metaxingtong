"""Render camera-only hypotheses on frozen D. Source images are never read here."""
import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).parent;P=R.parent/'hospital_d_recovery_20261013b/spatial_fit_d/hospital_spatial_D.blend';J=json.load(open(R/'patient_camera_constraint.json'));SHA=hashlib.sha256(P.read_bytes()).hexdigest()
assert SHA==J['frozen_blend_sha256'];bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene

def fingerprint():
 out={}
 for o in bpy.data.objects:
  if o.type=='CAMERA':continue
  q={'type':o.type,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'collections':sorted(c.name for c in o.users_collection)}
  if o.type=='MESH':q.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[m.name if m else None for m in o.data.materials])
  if o.type=='LIGHT':q.update(energy=o.data.energy,color=list(o.data.color),light_type=o.data.type)
  out[o.name]=q
 mats={}
 for m in bpy.data.materials:
  mats[m.name]={'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes,'nodes':[(n.name,n.bl_idname,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes] if m.node_tree else None}
 payload={'objects':out,'materials':mats,'world':s.world.name,'world_nodes':[(n.name,n.bl_idname,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in s.world.node_tree.nodes],'layers':[(vl.name,[(o.name,o.hide_render) for o in vl.objects if o.type!='CAMERA']) for vl in s.view_layers]}
 return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
initial=fingerprint();records=[]
s.render.engine='CYCLES';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0
for vl in s.view_layers:vl.cycles.use_denoising=False
for k,c in J['cameras'].items():
 d=bpy.data.cameras.new('PATIENT_REGION_'+k+'_camera_candidate');o=bpy.data.objects.new('PATIENT_REGION_'+k+'_camera_candidate',d);s.collection.objects.link(o);o.matrix_world=Matrix(c['matrix_world']);d.lens=c['lens_mm'];d.sensor_width=c['sensor_width_mm'];d.sensor_fit=c['sensor_fit'];d.shift_x=d.shift_y=0;d.clip_start=.1;d.clip_end=1000
s.camera=bpy.data.objects['PATIENT_REGION_A_camera_candidate'];assert fingerprint()==initial
bpy.ops.wm.save_as_mainfile(filepath=str(R/'hospital_D_patient_region_STRESS_TEST.blend'))
for k,c in [('A', J['cameras']['A'])]:
 s.camera=bpy.data.objects['PATIENT_REGION_'+k+'_camera_candidate'];out=R/f'{k}_patient_region_STRESS_TEST_1920x1080_16spp_RAW.png';s.render.filepath=str(out);start=time.monotonic();bpy.ops.render.render(write_still=True)
 assert fingerprint()==initial
 records.append({'view':k,'render_file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_blend':str(P),'source_blend_sha256':SHA,'noncamera_fingerprint_before':initial,'noncamera_fingerprint_after':fingerprint(),'geometry_material_lighting_visibility_unchanged':True,'camera':c,'engine':'CYCLES','samples':16,'denoise':False,'adaptive_sampling':False,'device':'CPU','threads':2,'seed':0,'resolution':[1920,1080],'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'runtime_seconds':time.monotonic()-start,'source_fidelity_accepted':False});(R/'patient_region_render_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print('RENDER_DONE',k,flush=True)
