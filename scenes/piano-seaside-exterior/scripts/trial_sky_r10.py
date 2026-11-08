"""Sky-only trial on unchanged R09 scene; no BLEND overwrite."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa/r10/diagnosis';bpy.ops.wm.open_mainfile(filepath=str(R/'models/r09/piano_seaside_material.blend'));s=bpy.context.scene
for state in ['S40_sunset','S105_bluehour']:
 w=bpy.data.worlds['R09 '+state+' global environment'];n=next(n for n in w.node_tree.nodes if n.type=='TEX_ENVIRONMENT');n.image=bpy.data.images.load(str(R/'textures/r10_trial'/f'{state}.hdr'));n.interpolation='Cubic'
s.camera=bpy.data.objects['source_N6766'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=.375;s.render.border_min_y=1/3;s.render.border_max_y=1;s.render.filepath=str(Q/'N6766_resampled_mask.png');bpy.ops.render.render(write_still=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=640;s.render.resolution_y=360;s.eevee.taa_render_samples=8
out=Q/'trial_low';out.mkdir(exist_ok=True)
for state in ['S40_sunset','S105_bluehour']:
 s.world=bpy.data.worlds['R09 '+state+' global environment']
 for name in ['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766','main']:
  s.camera=bpy.data.objects[name];s.render.filepath=str(out/(state+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('SKY_TRIAL_RENDERED')
