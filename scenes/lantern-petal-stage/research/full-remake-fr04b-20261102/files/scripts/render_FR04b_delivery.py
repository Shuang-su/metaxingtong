# Corrected winding model only; stable source condition. No geometry/focal fitting.
import bpy
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/FR04b_{typ}.blend'));s=bpy.context.scene;s.render.threads=2;s.view_settings.exposure=-1.3;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.resolution_x=640;s.render.resolution_y=360
 for i in range(8):
  s.camera=bpy.data.objects['CHECK'+str(i)];s.render.filepath=str(D/f'renders/FR04b_CHECK{i}_{typ}.png');bpy.ops.render.render(write_still=True)
 for n,loc,target in [('LOW_FRONT',(0,-14,2.4),(0,2,2.5)),('LOW_INSIDE',(2,0,2.2),(7,3,4))]:
  c=bpy.data.cameras.new('INSPECTION_'+n);o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=28;s.camera=o;s.render.filepath=str(D/f'renders/FR04b_{n}_{typ}.png');bpy.ops.render.render(write_still=True)
 s.camera=bpy.data.objects['AUG23_CIRCLE_CONDITION_NOT_CALIBRATED'];s.render.resolution_x=3840;s.render.resolution_y=2160;s.cycles.samples=4;s.render.filepath=str(D/f'renders/FR04b_AUG23_native4k_{typ}.png');bpy.ops.render.render(write_still=True)
