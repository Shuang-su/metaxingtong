import bpy,json,os
R='/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2'
s=bpy.context.scene
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.cycles.samples=8;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.cycles.seed=0;s.render.use_compositing=False;s.render.threads_mode='FIXED';s.render.threads=4
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.filepath=R+'/T3_material_raw.png'
bpy.ops.render.render(write_still=True)
# White material override is a render-only diagnostic. Original candidate file is never overwritten.
m=bpy.data.materials.new('T3_DIAGNOSTIC_WHITE_OVERRIDE');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.6,.6,.6,1);p.inputs['Roughness'].default_value=.75
bpy.context.view_layer.material_override=m;s.render.filepath=R+'/T3_white_raw.png';bpy.ops.render.render(write_still=True)
json.dump({'camera':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'lens':s.camera.data.lens,'resolution':[1920,1080],'samples':8,'seed':0,'threads':4,'denoising':False,'material_image':'T3_material_raw.png','white_image':'T3_white_raw.png','white_is_render_override_only':True,'lighting_unchanged':True,'source_time':5586.011739,'source_camera_not_recalibrated':True},open(R+'/render_manifest.json','w'),indent=2)
