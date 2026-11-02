import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=[]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/ferris_remake_R03_{mode}.blend'));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.samples=24 if mode=='material' else 12;s.cycles.use_denoising=False
 for name in ['SRC_front','SRC_bench','SRC_corner','SRC_high','MAIN']:
  c=bpy.data.objects[name];s.camera=c;s.render.filepath=str(R/f'renders/R03_native_{mode}_{name}.png');bpy.ops.render.render(write_still=True);rows.append({'mode':mode,'camera':name,'matrix_world':[list(r) for r in c.matrix_world],'lens_mm':c.data.lens,'resolution':[1920,1080],'samples':s.cycles.samples,'geometry_mutated':False,'lights_mutated':False,'white_material_note':'Persistent neutral material replaces all surfaces including lamp emissive shader; area-light objects identical'})
 # Higher quality inspection views, same shared materials/lights, no concealment.
 if mode=='material':
  s.render.resolution_x=960;s.render.resolution_y=540;s.cycles.samples=16
  for name in [f'CHECK{i:02d}' for i in range(1,9)]+['CHECK09_ceiling','CHECK10_support']:
   s.camera=bpy.data.objects[name];s.render.filepath=str(R/f'renders/R03_check_{name}.png');bpy.ops.render.render(write_still=True)
(R/'qa/native-render-settings.json').write_text(json.dumps(rows,indent=2))
# Additional openly-labelled diagnostic camera/light only, not source comparison.
bpy.ops.wm.open_mainfile(filepath=str(R/'models/ferris_remake_R03_material.blend'));s=bpy.context.scene;s.render.resolution_x=960;s.render.resolution_y=540;s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads=2
c=bpy.data.objects['CHECK10_support'];c.location=(.3,-1.18,.18);c.rotation_euler=(Vector((1.30,-.95,.16))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=22;s.camera=c
d=bpy.data.lights.new('DIAGNOSTIC_ONLY_support_fill','AREA');d.energy=35;d.size=.7;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(.5,-.8,.23);o.rotation_euler=(Vector((1.32,-.95,.165))-o.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/R03_DIAGNOSTIC_support_fill.png');bpy.ops.render.render(write_still=True)
print('NATIVE_DONE')
