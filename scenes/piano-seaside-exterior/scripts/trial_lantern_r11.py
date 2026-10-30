import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from lantern_material_r11 import apply_lanterns
Q=R/'qa/r11/trial_a';Q.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r10/piano_seaside_material.blend'));s=bpy.context.scene
report=apply_lanterns();(Q/'parameters.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.resolution_x=1920;s.render.resolution_y=1080;s.eevee.taa_render_samples=32;s.render.resolution_percentage=100;s.camera=bpy.data.objects['main'];s.render.use_border=True;s.render.use_crop_to_border=True
r=(550,520,1000,870);s.render.border_min_x=r[0]/1920;s.render.border_max_x=r[2]/1920;s.render.border_min_y=1-r[3]/1080;s.render.border_max_y=1-r[1]/1080;s.render.filepath=str(Q/'main_lamp_native_crop.png');bpy.ops.render.render(write_still=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=960;s.render.resolution_y=540;s.eevee.taa_render_samples=16
for state in ['S40_sunset','S105_bluehour']:
 s.world=bpy.data.worlds['R09 '+state+' global environment']
 for name in ['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766','main']:
  s.camera=bpy.data.objects[name];s.render.filepath=str(Q/(state+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('R11_TRIAL_A_COMPLETE_NO_MODEL_SAVED')
