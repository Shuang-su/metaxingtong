import bpy,json,pathlib
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/cyber-roof-stage-20261105');Q=pathlib.Path(__file__).parent
states=[]
for v in ['','-white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'roof-r05{v}.blend'));s=bpy.context.scene;s.camera=bpy.data.objects['DIAG09 underside single light'];s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=796;s.render.resolution_y=448;s.render.resolution_percentage=100
 s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.3,.3,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 bpy.ops.object.light_add(type='AREA',location=(0,-10,-10));l=bpy.context.object;l.data.energy=2500;l.data.size=12;l.rotation_euler=(Vector((0,2,2))-l.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 states.append({'lights':sorted((o.data.type,o.data.energy,list(o.data.color),o.data.shape,o.data.size,[list(r)for r in o.matrix_world])for o in s.objects if o.type=='LIGHT'),'world':[list(s.world.node_tree.nodes['Background'].inputs[0].default_value),s.world.node_tree.nodes['Background'].inputs[1].default_value],'camera':[list(r)for r in s.camera.matrix_world],'frame':[list(x)for x in s.camera.data.view_frame(scene=s)],'render':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.cycles.samples,s.cycles.use_denoising]})
(Q/'recipe-check.json').write_text(json.dumps({'material':states[0],'white':states[1],'identical_environment_camera_render':states[0]==states[1],'scope':'Independent reconstruction of immutable render recipe; not contemporaneous capture, no render/save.'},indent=2))
