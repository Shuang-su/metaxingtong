import bpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r01.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=24
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.004,.008,.025,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
s.camera.data.lens=43
# Camera changes are global fit hypotheses, never image warps.
from mathutils import Vector
s.camera.rotation_euler=(Vector((0,2.4,3.8))-s.camera.location).to_track_quat('-Z','Y').to_euler()
for o in s.objects:
 if o.name.startswith('STAGE_INNER'):o.scale.x=o.scale.y=1.12
 if o.type=='LIGHT':o.data.energy*=.55
# Preserve materials and stable object properties; evaluate curves to mesh for portable editable export.
for o in list(s.objects):
 if o.type=='CURVE':
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
s.render.filepath=str(P/'renders/preview11-r02.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r02.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r02.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True)
side={'schema':1,'source_state':'11 fixed; 10 auxiliary different dynamic state','blender':bpy.app.version_string,'render':{'engine':s.render.engine,'samples':s.cycles.samples,'denoise':False,'resolution':[1192,671]},'world':{'background':[.004,.008,.025,1],'strength':.4},'objects':[]}
for o in s.objects:
 d={'name':o.name,'type':o.type,'matrix_world':[list(r) for r in o.matrix_world],'properties':dict(o.items())}
 if o.type=='CAMERA':d['camera']={'lens':o.data.lens,'sensor_width':o.data.sensor_width,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end}
 if o.type=='LIGHT':d['light']={'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size}
 side['objects'].append(d)
(P/'models/roof-r02-recovery.json').write_text(json.dumps(side,indent=2))
bpy.ops.render.render(write_still=True)
# White model is the same mesh and state, replacing material assignments only.
white=bpy.data.materials['White diagnostic']
geom={o.name:[len(o.data.vertices),len(o.data.polygons)] for o in s.objects if o.type=='MESH'}
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r02-white.blend'))
assert geom=={o.name:[len(o.data.vertices),len(o.data.polygons)] for o in s.objects if o.type=='MESH'}
(P/'qa/material-white-mesh-counts.json').write_text(json.dumps(geom,indent=2))
