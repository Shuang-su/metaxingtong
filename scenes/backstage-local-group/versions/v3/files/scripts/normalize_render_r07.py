import bpy,pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));s=bpy.context.scene;before={'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'samples':s.cycles.samples,'camera':s.camera.name};s.camera=bpy.data.objects['MANNEQUIN_local'];s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
 s['R07_scope']='Only canonical saved render state updated to executed R06 preview state; geometry/camera transforms/materials unchanged. Re-export GLB yfov for1192x671; historical R06 PNG reuse explicit, no new render claimed.'
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R07_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R07_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'before':before,'after':{'resolution':[1192,671,100],'samples':64,'denoise':False,'camera':s.camera.name},'model_sha256':hashlib.sha256((P/'models'/f'R07_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R07-render-state.json').write_text(json.dumps(audit,indent=2))
