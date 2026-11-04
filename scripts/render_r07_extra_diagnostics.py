import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=6;scene.render.resolution_x=800;scene.render.resolution_y=440;scene.render.resolution_percentage=100
scene.view_layers['MATERIAL'].use=True;scene.view_layers['WHITE'].use=False
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-1.0
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.8,.8,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.data.color=(1,1,1)
# The two new lights are fixed across BOTH diagnostic views, never used in source renders.
lighting=[]
for name,loc,target,power,size in [('DIAG rear fill',(10,17,10),(0,11,3),1800,7),('DIAG interior fill',(2.7,12.5,4.9),(0,8.5,3),160,2)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();lighting.append(dict(name=name,location=loc,target=target,power=power,size=size,color=[1,1,1]))
views=[]
for name,loc,target,lens in [('DIAG_rear_side_junction',(12,20,9),(1.8,10.5,2.8),34),('DIAG_inside_upper_mounts',(3.3,13.8,4.2),(0,8.0,3.6),24)]:
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();scene.camera=o
 path=R/'renders/R07'/(name+'_white_800x440.png');scene.render.filepath=str(path)
 if '--prepare-only' not in sys.argv:bpy.ops.render.render(write_still=True)
 bpy.context.view_layer.update()
 views.append(dict(name=name,location=loc,target=target,lens=lens,sensor_width=36,sensor_fit=d.sensor_fit,clip_start=d.clip_start,clip_end=d.clip_end,pixel_aspect=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],rotation_euler=list(o.rotation_euler),matrix_world=[list(v) for v in o.matrix_world],image=str(path.relative_to(R)),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(R/'qa/R07_extra_diagnostic_manifest.json').write_text(json.dumps(dict(base='models/R07_twistframe_hall_white.blend',base_sha256=hashlib.sha256((R/'models/R07_twistframe_hall_white.blend').read_bytes()).hexdigest(),geometry_changed=False,visibility_changed=False,source_cameras_changed=False,saved_in_original=False,diagnostic_blend='models/R07_diagnostic_views_ONLY.blend',description='Reproducible render-only diagnostic camera/light overrides, not source views; complete geometry remains visible.',resolution=[800,440],engine='CYCLES CPU',samples=128,threads=6,view_transform='AgX',exposure=-1.0,world_strength=.35,fixed_additional_diagnostic_lights=lighting,views=views),indent=2))

scene['diagnostic_only']='Two added check cameras and fixed diagnostic lighting; all R07 geometry and original11 cameras unchanged. Not source fitting, not the material/white delivery original.'
scene['version']='R07 diagnostic views only'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/R07_diagnostic_views_ONLY.blend'))
