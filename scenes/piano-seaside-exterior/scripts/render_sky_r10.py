"""Bounded saved-file regression for R10. Shared sky state selected explicitly."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa/r10';bpy.ops.wm.open_mainfile(filepath=str(R/'models/r10/piano_seaside_material.blend'));s=bpy.context.scene
names=['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766','main']
def render(name,path,width,samples):
 s.camera=bpy.data.objects[name];s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=width;s.render.resolution_y=width*9//16;s.render.resolution_percentage=100;s.eevee.taa_render_samples=samples;s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
for name in names:render(name,Q/(name+'.png'),1920,32)
# Alternate state only exists as an active candidate when antialias is selected.
if 'antialias' in s.get('stage',''):
 s.world=bpy.data.worlds['R09 S105_bluehour global environment'];out=Q/'alternate_S105';out.mkdir(exist_ok=True)
 for name in names:render(name,out/(name+'.png'),960,16)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r10/piano_seaside_white.blend'));s=bpy.context.scene;render('main',Q/'white_main.png',1920,32)
print('R10_BOUNDED_RENDER_COMPLETE')
