"""Controlled R09/R10 world-image test of the cropped N6318 lamp opening."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa/r11/diagnosis/sky_response';Q.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r10/piano_seaside_material.blend'));s=bpy.context.scene;s.camera=bpy.data.objects['source_N6318'];s.world=bpy.data.worlds['R09 S105_bluehour global environment']
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.eevee.taa_render_samples=16
s.render.use_border=True;s.render.use_crop_to_border=True;r=(235,490,340,540)
s.render.border_min_x=r[0]/960;s.render.border_max_x=r[2]/960;s.render.border_min_y=0;s.render.border_max_y=1-r[1]/540
n=next(n for n in s.world.node_tree.nodes if n.type=='TEX_ENVIRONMENT');new=n.image;old=bpy.data.images.load(str(R/'textures/r09/S105_bluehour.hdr'),check_existing=False)
for ray in [True,False]:
 s.eevee.use_raytracing=ray
 for label,im,interp in [('R10',new,'Cubic'),('R09_world_only',old,'Linear'),('R10_repeat',new,'Cubic')]:
  n.image=im;n.interpolation=interp;s.render.filepath=str(Q/(label+('_ray_on' if ray else '_ray_off')+'.png'));bpy.ops.render.render(write_still=True)
(Q/'settings.json').write_text(json.dumps({'camera':'source_N6318 unchanged','full_pixels':[960,540],'xyxy':r,'samples':16,'state':'S105_bluehour','changes':'world image/interpolation and diagnostic ray tracing flag only; no model saved','exposure':s.view_settings.exposure},indent=2)+'\n')
print('R11_SKY_RESPONSE_DIAGNOSIS_COMPLETE')
