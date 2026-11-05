import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r04.blend'));s=bpy.context.scene
bpy.ops.object.camera_add(location=(0,-27,-8));c=bpy.context.object;c.name='DIAG09 underside single light';c.rotation_euler=(Vector((0,2,3))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=35;bpy.context.view_layer.update()
s.camera=bpy.data.objects['SOURCE11 conditional camera']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r05.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r05.glb'),export_format='GLB',export_cameras=True,export_extras=True)
d=json.loads((P/'models/roof-r04-recovery.json').read_text());d['source_blend']='roof-r05.blend';d['glb']='roof-r05.glb';d['objects'].append({'name':c.name,'type':'CAMERA','matrix_world':[list(r) for r in c.matrix_world],'properties':{'purpose':'explicit changed-light diagnostic only'},'camera':{k:getattr(c.data,k) for k in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','type','clip_start','clip_end']}})
d['diagnostic09_recipe']={'camera':c.name,'resolution':[796,448],'percentage':100,'samples':8,'world_background':[.3,.3,.3,1],'world_strength':.8,'add_single_light':{'type':'AREA','location':[0,-10,-10],'look_at':[0,2,2],'energy':2500,'size':12,'shape':'SQUARE'},'production_state_changed':False,'method':'fresh load each material/white original; same world replacement plus exactly one extra light; diagnostic only, not source view'}
(P/'models/roof-r05-recovery.json').write_text(json.dumps(d,indent=2))
w=bpy.data.materials.new('White diagnostic R05');w.use_nodes=True;w.diffuse_color=(.66,.66,.66,1);b=w.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.7
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r05-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r05-white.glb'),export_format='GLB',export_cameras=True,export_extras=True)
for variant in ['','-white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/('roof-r05'+variant+'.blend')));s=bpy.context.scene;s.camera=bpy.data.objects['DIAG09 underside single light'];s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=796;s.render.resolution_y=448;s.render.resolution_percentage=100
 s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.3,.3,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 bpy.ops.object.light_add(type='AREA',location=(0,-10,-10));l=bpy.context.object;l.name='DIAG09 exactly one additional AREA';l.data.energy=2500;l.data.size=12;l.rotation_euler=(Vector((0,2,2))-l.location).to_track_quat('-Z','Y').to_euler()
 assert len([o for o in s.objects if o.type=='LIGHT'])==4
 s.render.filepath=str(P/'renders'/('diagnostic09-single-light'+variant+'.png'));bpy.ops.render.render(write_still=True)
