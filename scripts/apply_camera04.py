import bpy,os,json
from mathutils import Vector
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));a=json.load(open(r+'/qa/camera-fit04.json'))['parameters']
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=r+'/models/'+mode+'.blend');s=bpy.context.scene;o=bpy.data.objects['SOURCE04 conditional'];o.location=a[:3];o.rotation_euler=(Vector((a[3],2.5,a[4]))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=a[5];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=r+'/models/'+mode+'.blend');bpy.ops.export_scene.gltf(filepath=r+'/models/'+mode+'.glb',export_format='GLB',export_cameras=True,export_lights=False)
 s.camera=o;s.cycles.samples=4;s.cycles.use_denoising=False;s.render.resolution_percentage=50;s.render.filepath=r+'/renders/'+mode+'-source04-camera-fit-low.png';bpy.ops.render.render(write_still=True)
