import bpy,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from layout_states import *
args=sys.argv[sys.argv.index('--')+1:];workspace=Path(args[0]);requested=args[1]
m=json.loads((root/'layout_state_manifest.json').read_text());base=workspace/m['base_blend']['workspace_relative_path']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base)==m['base_blend']['sha256'];bpy.ops.wm.open_mainfile(filepath=str(base));sc=bpy.context.scene
state,selection=choose_state(m,explicit_state=requested)
selection['diagnostic_source_reference']=m['diagnostic_render']['source_reference_state_labels'][state]
selection['note']='Manual observed-image state for a fixed-camera diagnostic; not an automatic timeline inference or calibrated source view.'
switch=apply_layout(sc,m,state,selection)
# Camera is selected independently after the state has been applied. No state decisions use its name.
sc.camera=sc.objects[m['diagnostic_render']['camera']]
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=48;sc.cycles.seed=20261010;sc.cycles.use_animated_seed=False;sc.cycles.use_denoising=False
sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1180;sc.render.resolution_y=664;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.use_border=False;sc.render.use_crop_to_border=False;sc.use_nodes=False
out=root/'renders'/('fixed_01_front_'+state+'.png');sc.render.filepath=str(out)
meta={'input_blend_sha256':sha(base),'manifest_sha256':sha(root/'layout_state_manifest.json'),'state_module_sha256':sha(root/'scripts/layout_states.py'),'state_switch':switch,'camera':sc.camera.name,'camera_world_matrix':[list(x) for x in sc.camera.matrix_world],'lens_mm':sc.camera.data.lens,'sensor_width_mm':sc.camera.data.sensor_width,'sensor_fit':sc.camera.data.sensor_fit,'shift':[sc.camera.data.shift_x,sc.camera.data.shift_y],'camera_calibrated_to_source':False,'camera_and_geometry_unchanged_between_states':True,'resolution':[1180,664],'samples':48,'seed':20261010,'threads':2,'denoising':False,'blender_version':bpy.app.version_string,'model_saved':False,'source_fidelity_accepted':False,'visibility':object_visibility(sc),'collection_visibility':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in bpy.data.collections}}
(root/'qa'/f'render_{state}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
bpy.ops.render.render(write_still=True)
meta['output_sha256']=sha(out);meta['output_bytes']=out.stat().st_size
(root/'qa'/f'render_{state}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('STATE_RENDER_DONE',state,meta['output_sha256'],flush=True)
