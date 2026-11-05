import bpy,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R01_material.blend'))
s=bpy.context.scene;b=s.world.node_tree.nodes['Background'];j={'version':'R01','status':'FINITE_CANDIDATE_SOURCE_FAILED','blender':bpy.app.version_string,'world':{'color':list(b.inputs[0].default_value),'strength':b.inputs[1].default_value},'render':{'resolution_x':s.render.resolution_x,'resolution_y':s.render.resolution_y,'resolution_percentage':s.render.resolution_percentage,'pixel_aspect_x':s.render.pixel_aspect_x,'pixel_aspect_y':s.render.pixel_aspect_y,'engine':s.render.engine,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'cameras':[],'area_lights':[],'glb_limitations':['AREA lights and World not represented natively in this GLB; sidecar required','Procedural Noise material base color in BLEND is unsupported by glTF export; GLB is fixed base-color approximation, not exact appearance parity','Camera image frame/aspect and active camera require sidecar; cameras themselves exported','No recovered source textures, no source-image billboard']}
for o in bpy.data.objects:
 if o.type=='CAMERA':
  d=o.data;j['cameras'].append({'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'type':d.type,'lens':d.lens,'sensor_width':d.sensor_width,'sensor_height':d.sensor_height,'sensor_fit':d.sensor_fit,'shift_x':d.shift_x,'shift_y':d.shift_y,'clip_start':d.clip_start,'clip_end':d.clip_end})
 if o.type=='LIGHT' and o.data.type=='AREA':
  d=o.data;j['area_lights'].append({'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'energy':d.energy,'shape':d.shape,'size':d.size,'color':list(d.color)})
(P/'dependencies/R01-environment-sidecar.json').write_text(json.dumps(j,ensure_ascii=False,indent=2))
print('R01_SIDECAR_CREATED',len(j['cameras']),len(j['area_lights']))
