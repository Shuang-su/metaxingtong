import bpy,json,pathlib
R=pathlib.Path('/workspace/scratch/fa58bfcf0425/metaxingtong-harbor-candidate-20261102/stages/r06-review-candidate');O=pathlib.Path(__file__).resolve().parent
out={}
for state in ['white','material']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'harbor-r06-{state}.blend'))
 out[state]={'mesh_modifiers':{o.name:[m.type for m in o.modifiers] for o in bpy.context.scene.objects if o.type=='MESH' and o.modifiers},'render_hidden_meshes':[o.name for o in bpy.context.scene.objects if o.type=='MESH' and o.hide_render],'mesh_animation':[o.name for o in bpy.context.scene.objects if o.type=='MESH' and o.animation_data],'camera_animation':[o.name for o in bpy.context.scene.objects if o.type=='CAMERA' and o.animation_data],'frame_current':bpy.context.scene.frame_current}
(O/'independent-scene-state.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
