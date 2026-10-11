import bpy, os, sys, json, hashlib
R='/workspace/scratch/fa58bfcf0425'
O=R+'/ktv_fixed_visibility_20261010'
args=sys.argv[sys.argv.index('--')+1:];model,view,state=args
paths={'legacy':R+'/ktv_fullroom/source/restored/models/Xingtong_KTV_Textured.blend','current':R+'/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend','current_white':R+'/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage_White.blend'}
cam={'Empty_Stage':'MATCH_D_01h58m39s_empty','Telescope_Detail':'DETAIL_Telescope_Lamp'}[view]
bpy.ops.wm.open_mainfile(filepath=paths[model]);sc=bpy.context.scene
if state=='historical_hidden':
 assert model=='legacy', 'Hidden state is only allowed for labelled historical ablation.'
 for n in ['02_Inflated_Armchairs','08_Optional_Star_Companion']:bpy.data.collections[n].hide_render=True
else:
 # This is an assertion, not a repair: current stored model already has fixed visibility.
 for n in ['02_Inflated_Armchairs','08_Optional_Star_Companion']:assert not bpy.data.collections[n].hide_render
assert bpy.data.collections['09_Optional_Moving_Balloon_Dog'].hide_render
sc.camera=bpy.data.objects[cam];sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=48;sc.cycles.seed=20261010;sc.cycles.use_animated_seed=False;sc.cycles.use_denoising=False
sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1188;sc.render.resolution_y=668;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8'
sc.render.use_border=False;sc.render.use_crop_to_border=False
sc.use_nodes=False
tag=model+'_'+view+'_'+state;out=O+'/renders/'+tag+'.png';sc.render.filepath=out
vis={'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in sorted(bpy.data.collections,key=lambda c:c.name)},'objects':{o.name:{'hide_render':o.hide_render,'visible_camera':o.visible_camera} for o in sorted(sc.objects,key=lambda o:o.name) if o.type=='MESH'}}
meta={'role':'historical_hidden_ablation' if state=='historical_hidden' else 'fixed_visibility_regression','input_model':paths[model],'input_sha256':hashlib.sha256(open(paths[model],'rb').read()).hexdigest(),'output':out,'blender_version':bpy.app.version_string,'camera':cam,'camera_world_matrix':[list(x) for x in sc.camera.matrix_world],'lens_mm':sc.camera.data.lens,'sensor_width_mm':sc.camera.data.sensor_width,'shift':[sc.camera.data.shift_x,sc.camera.data.shift_y],'resolution':[1188,668],'samples':48,'seed':20261010,'threads':2,'use_denoising':False,'geometry_edits':False,'model_saved':False,'visibility':vis,'visibility_sha256':hashlib.sha256(json.dumps(vis,sort_keys=True).encode()).hexdigest(),'source_camera_match':'approximate legacy D, not source-accepted' if view=='Empty_Stage' else 'none; synthetic geometry diagnostic only','source_time':'01:58:39' if view=='Empty_Stage' else None,'source_url':'https://www.bilibili.com/video/BV1ru41147sn/' if view=='Empty_Stage' else None}
json.dump(meta,open(O+'/qa/'+tag+'.json','w'),indent=2)
bpy.ops.render.render(write_still=True)
meta['output_sha256']=hashlib.sha256(open(out,'rb').read()).hexdigest();meta['output_bytes']=os.path.getsize(out);json.dump(meta,open(O+'/qa/'+tag+'.json','w'),indent=2)
print('REGRESSION_RENDER_DONE',tag,meta['output_sha256'],flush=True)
