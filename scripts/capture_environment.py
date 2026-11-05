import bpy,os,json
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=root+'/models/material.blend');bpy.context.view_layer.update();s=bpy.context.scene
p=root+'/models/environment.json';d=json.load(open(p))
d['active_camera']=s.camera.name;d['render']={k:getattr(s.render,k) for k in ['resolution_x','resolution_y','resolution_percentage','pixel_aspect_x','pixel_aspect_y','engine','film_transparent']};d['view']={k:getattr(s.view_settings,k) for k in ['view_transform','look','exposure','gamma']};d['cycles']={'samples':32,'use_denoising':False};d['display_device']=s.display_settings.display_device
d['cameras']=[];d['lights']=[]
for o in s.objects:
 if o.type=='CAMERA':d['cameras'].append({'name':o.name,**{k:getattr(o.data,k) for k in ['type','lens','sensor_width','sensor_height','sensor_fit','clip_start','clip_end','shift_x','shift_y','ortho_scale']},'matrix_world':[list(r) for r in o.matrix_world]})
 if o.type=='LIGHT':d['lights'].append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size,'shape':o.data.shape,'matrix_world':[list(r) for r in o.matrix_world]})
json.dump(d,open(p,'w'),indent=2)
