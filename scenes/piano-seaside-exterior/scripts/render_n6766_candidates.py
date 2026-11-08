import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1];out=root/'qa/r08/previews';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'models/r07/piano_seaside_material.blend'));sc=bpy.context.scene;o=bpy.data.objects['source_N6766'];sc.camera=o;sc.render.resolution_x=640;sc.render.resolution_y=360;sc.eevee.taa_render_samples=8
for p in json.loads((root/'qa/r08/camera-candidates.json').read_text())['candidates']:
 if '--pan-only' in sys.argv and not p['id'].startswith('pan_close_'):continue
 if '--final-only' in sys.argv and not p['id'].startswith('final_close_'):continue
 if '--roll-only' in sys.argv and not p['id'].startswith('pose_roll_'):continue
 if '--three-only' in sys.argv and not p['id'].startswith('silhouette_three_'):continue
 if '--side-only' in sys.argv and not p['id'].startswith(('framing_four_','side_close_')):continue
 if len(sys.argv)>1 and '--new-only' in sys.argv and not p['id'].startswith('low_close_'):continue
 o.location=p['location'];q=(Vector(p['target'])-o.location).to_track_quat('-Z','Y');o.rotation_euler=(q@Quaternion((0,0,1),p['roll_rad'])).to_euler();o.data.lens=p['lens_mm'];sc.render.filepath=str(out/(p['id']+'.png'));bpy.ops.render.render(write_still=True)
print('PREVIEWS_COMPLETE')
