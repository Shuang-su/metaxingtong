import bpy,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R04D_material.blend'))
s=bpy.context.scene;b=s.world.node_tree.nodes['Background']
j={'version':'R04D','status':'FINITE_CANDIDATE_SOURCE_FAILED','blender':bpy.app.version_string,'active_camera':s.camera.name,'world':{'use_nodes':True,'surface':'Background to World Output Surface','color':list(b.inputs[0].default_value),'strength':b.inputs[1].default_value},'render':{'resolution_x':s.render.resolution_x,'resolution_y':s.render.resolution_y,'resolution_percentage':100,'pixel_aspect_x':s.render.pixel_aspect_x,'pixel_aspect_y':s.render.pixel_aspect_y,'engine':s.render.engine,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'samples':96,'use_denoising':False,'film_transparent':False},'cameras':[],'area_lights':[],'glb_limitations':['AREA lights and World require this sidecar and restore_r03.py; not native GLB environment parity','Active camera, image frame/aspect and display transform require sidecar','Generated two-color region texture replaces unsupported procedural material; it is authored approximation, not recovered source texture','No hidden city, rear stage architecture or full tower recovery']}
for o in bpy.data.objects:
 if o.type=='CAMERA':
  d=o.data;j['cameras'].append({'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'type':d.type,'lens':d.lens,'sensor_width':d.sensor_width,'sensor_height':d.sensor_height,'sensor_fit':d.sensor_fit,'shift_x':d.shift_x,'shift_y':d.shift_y,'clip_start':d.clip_start,'clip_end':d.clip_end})
 if o.type=='LIGHT' and o.data.type=='AREA':
  d=o.data;j['area_lights'].append({'name':o.name,'matrix_world':[list(row) for row in o.matrix_world],'energy':d.energy,'shape':d.shape,'size':d.size,'color':list(d.color)})
(P/'dependencies/R04D-environment-sidecar.json').write_text(json.dumps(j,ensure_ascii=False,indent=2))
inventory=[]
for o in bpy.data.objects:
 if o.type=='MESH':inventory.append({'object':o.name,'group':o.get('group'),'source_evidence':o.get('source_evidence'),'inferred':o.get('inferred'),'revision':o.get('revision')})
(P/'docs/R04D-object-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
print('R04D_SIDECAR_CREATED',len(j['cameras']),len(j['area_lights']),j['active_camera'])
