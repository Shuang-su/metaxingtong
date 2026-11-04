import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];V=R/'versions/V03'
def value(x):
 try:return list(x)
 except TypeError:return x
def make(variant):
 bpy.ops.wm.open_mainfile(filepath=str(R/f'versions/V02/models/phone-{variant}.blend'));s=bpy.context.scene;source=s.camera
 vs=[o.matrix_world@v.co for o in s.objects if o.type=='MESH' for v in o.data.vertices];center=Vector([(min(v[i] for v in vs)+max(v[i] for v in vs))/2 for i in range(3)])
 for name,v in [('front',Vector((0,0,4.5))),('rear',Vector((0,0,-4.5))),('side',Vector((4.5,0,0))),('top',Vector((0,4.5,.45)))]:
  data=source.data.copy();data.lens=48;o=bpy.data.objects.new('DIAGNOSTIC_'+name,data);s.collection.objects.link(o);o.location=center+v;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();o['role']='Diagnostic only; exact state of V02 final render, not source camera'
 s.camera=source
 bpy.context.view_layer.update()
 state={'variant':variant,'source_version':'b41bda63a86bc457bbf712362ceabef51c957a0a','active_camera':source.name,'cameras':{},'lights':{},'world':{'color':list(s.world.color),'use_nodes':s.world.use_nodes},'render':{k:getattr(s.render,k) for k in ['resolution_x','resolution_y','resolution_percentage','pixel_aspect_x','pixel_aspect_y','film_transparent','engine','threads_mode','threads']},'cycles':{'samples':s.cycles.samples,'use_denoising':s.cycles.use_denoising,'device':s.cycles.device},'color_management':{k:getattr(s.view_settings,k) for k in ['view_transform','look','exposure','gamma']},'display_device':s.display_settings.display_device,'glb_limit':'glTF does not encode Blender world or area lights; full state retained in BLEND and this JSON. Native cameras exported, validate projection after real import; use restore-state.py for Blender render equivalence.'}
 for o in s.objects:
  if o.type=='CAMERA':state['cameras'][o.name]={'matrix_world':[list(r) for r in o.matrix_world],'type':o.data.type,'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'sensor_fit':o.data.sensor_fit,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'dof_use_dof':o.data.dof.use_dof,'aspect_ratio':s.render.resolution_x*s.render.pixel_aspect_x/(s.render.resolution_y*s.render.pixel_aspect_y)}
  elif o.type=='LIGHT':state['lights'][o.name]={'matrix_world':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size,'size_y':o.data.size_y,'use_shadow':o.data.use_shadow}
 if s.world.use_nodes:
  wn=s.world.node_tree
  state['world']['nodes']=[]
  for node in wn.nodes:
   nd={'name':node.name,'bl_idname':node.bl_idname,'inputs':{}}
   for inp in node.inputs:
    if hasattr(inp,'default_value'):
     val=inp.default_value
     if isinstance(val,(int,float,bool,str)):nd['inputs'][inp.name]=val
     else:
      try:nd['inputs'][inp.name]=list(val)
      except TypeError:pass
   state['world']['nodes'].append(nd)
  state['world']['links']=[{'from_node':l.from_node.name,'from_socket':l.from_socket.name,'to_node':l.to_node.name,'to_socket':l.to_socket.name} for l in wn.links]
 json.dump(state,open(V/f'qa/{variant}-scene-state.json','w'),indent=2)
 # --metadata-only keeps existing V03 model bytes unchanged during sidecar correction.
 if "--metadata-only" in sys.argv:return
 bpy.ops.wm.save_as_mainfile(filepath=str(V/f'models/phone-{variant}.blend'))
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(V/f'models/phone-{variant}.glb'),export_format='GLB',use_selection=True,export_cameras=True,export_lights=False)
for variant in ['material','white']:make(variant)
