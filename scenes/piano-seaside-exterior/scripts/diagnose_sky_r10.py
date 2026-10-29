"""Controlled R09 background crop: samples/interpolation only, no saved scene edits."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa/r10/diagnosis';bpy.ops.wm.open_mainfile(filepath=str(R/'models/r09/piano_seaside_material.blend'));s=bpy.context.scene;s.camera=bpy.data.objects['source_N6766'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=.375;s.render.border_min_y=1/3;s.render.border_max_y=1
node=next(n for n in s.world.node_tree.nodes if n.type=='TEX_ENVIRONMENT');report={'camera':'source_N6766 unchanged','crop_full_image_xyxy':[0,0,720,720],'world':s.world.name,'image':node.image.name,'image_dimensions':list(node.image.size),'original_interpolation':node.interpolation,'render_engine':s.render.engine,'baseline_full_image':'qa/r09/source_N6766.png','no_geometry_or_camera_edits':True}
for interpolation,samples in [('Linear',32),('Linear',128),('Cubic',32)]:
 node.interpolation=interpolation;s.eevee.taa_render_samples=samples;s.render.filepath=str(Q/f'N6766_{interpolation}_{samples}.png');bpy.ops.render.render(write_still=True)
(Q/'controlled-settings.json').write_text(json.dumps(report,indent=2)+'\n');print('DIAGNOSIS_COMPLETE')
