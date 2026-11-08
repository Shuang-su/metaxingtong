"""Render same fixed cameras under both existing global states."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/r11';bpy.ops.wm.open_mainfile(filepath=str(R/'models/r11/piano_seaside_material.blend'));s=bpy.context.scene
names=['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766','main'];checks=[f'check_{i:02d}' for i in range(8)]+['check_top']
def diagnostic_camera():
 data=bpy.data.cameras.new('diagnostic_lantern');o=bpy.data.objects.new('diagnostic_lantern',data);s.collection.objects.link(o);o.location=(-1.8,.1,1.0);o.rotation_euler=(Vector((-.92,1.22,.21))-o.location).to_track_quat('-Z','Y').to_euler();data.lens=55
def render(name,path,width,samples):
 s.camera=bpy.data.objects[name];s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=width;s.render.resolution_y=width*9//16;s.render.resolution_percentage=100;s.eevee.taa_render_samples=samples;s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
diagnostic_camera()
for name in names+['diagnostic_lantern']:render(name,Q/(name+'.png'),1920,32)
for name in checks:render(name,Q/(name+'.png'),960,32)
s.world=bpy.data.worlds['R09 S105_bluehour global environment'];out=Q/'alternate_S105';out.mkdir(exist_ok=True)
for name in names:render(name,out/(name+'.png'),960,16)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r11/piano_seaside_white.blend'));s=bpy.context.scene;diagnostic_camera()
for name in ['main','diagnostic_lantern']:render(name,Q/('white_'+name+'.png'),1920,32)
print('R11_FINAL_24_RENDERS_COMPLETE')
