import os
import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
r=Path(__file__).parent;d=r.parent/'spatial_fit_d';source=Path(os.environ.get('HOSPITAL_D_BASELINE',str(d/'hospital_spatial_D.blend')));bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
p=json.load(open(r/'candidate_parameters.json'))['params'];cx,w,f,b,tf,tb=p
o=bpy.data.objects['Sofa • broad padded arm'];before=[list(v.co) for v in o.data.vertices];uv_before=[list(x.uv) for x in o.data.uv_layers.active.data]
for v in o.data.vertices:
 x,y,z=v.co;t=(y+.74)/1.48;v.co.x=cx+x*w/.24;v.co.y=f+t*(b-f);v.co.z=-.195+(z+.195)/.39*(tf+(tb-tf)*t+.195)
o.data.update();assert uv_before==[list(x.uv) for x in o.data.uv_layers.active.data]
s['candidate_status']='E left-arm-only conditional experiment; rejected pending source and collision review; frozen D cameras and all other mesh geometry unchanged'
s.camera=bpy.data.objects['MATCH_G_Sofa_And_Bed'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.threads_mode='FIXED';s.render.threads=2
for vl in s.view_layers:vl.cycles.use_denoising=False
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_sofa_arm_E_REJECTED.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'hospital_sofa_arm_E_REJECTED.glb'),export_format='GLB',use_selection=False)
m=bpy.data.materials.new('Diagnostic white - shared E geometry');m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(.74,.74,.74,1);q.inputs['Roughness'].default_value=.8
for x in s.objects:
 if x.type=='MESH':x.data.materials.clear();x.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_sofa_arm_E_REJECTED_white.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'hospital_sofa_arm_E_REJECTED_white.glb'),export_format='GLB',use_selection=False)
(r/'one_mesh_change_receipt.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changed_object':o.name,'before_local_vertices':before,'after_local_vertices':[list(v.co) for v in o.data.vertices],'parameter_source':'candidate_parameters.json','UV_unchanged':True,'object_matrix_unchanged':True,'status':'E_REJECTED_DIAGNOSTIC'},ensure_ascii=False,indent=2))
