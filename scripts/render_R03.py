import bpy
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
for stage,kind in [('R02','material'),('R03','material'),('R03','white')]:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/arcade_remake_{stage}_{kind}.blend'));s=bpy.context.scene;s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=32;s.cycles.use_denoising=False
 for name,loc in [('R03_DETAIL_FRONT',(-3.5,-4,3.7)),('R03_DETAIL_OBLIQUE',(-5.1,-4,4.0))]:
  if name not in bpy.data.objects:
   d=bpy.data.cameras.new(name);d.lens=55;d.sensor_width=36;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-3.5,-.12,3.66))-o.location).to_track_quat('-Z','Y').to_euler()
  s.camera=bpy.data.objects[name];s.render.filepath=str(D/f'renders/R03_{stage}_{kind}_{name}.png');bpy.ops.render.render(write_still=True)
 if stage=='R03' and kind=='material':
  tex=next(n for n in bpy.data.materials['R03 M01 partial source-lit NOT albedo'].node_tree.nodes if n.type=='TEX_IMAGE')
  for variant in ['STRESS_A','STRESS_B']:
   tex.image=bpy.data.images.load(str(D/f'textures/R03/DERIVED_SOURCE_LIT_{variant}.png'));s.camera=bpy.data.objects['R03_DETAIL_FRONT'];s.render.filepath=str(D/f'renders/R03_{variant}_FRONT.png');bpy.ops.render.render(write_still=True)
