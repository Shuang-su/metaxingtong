import bpy,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=R/'c26';bpy.ops.wm.open_mainfile(filepath=str(P/'hospital_C26_structure_controls_CONDITIONAL.blend'));s=bpy.context.scene
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=0.4;s.display.shading.color_type='SINGLE';s.display.shading.single_color=(0.75,0.75,0.75);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.5;s.display.shading.curvature_valley_factor=1.2;s.display.shading.show_specular_highlight=False;s.display.shading.background_type='WORLD';s.world.color=(0.5,0.5,0.5)
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for k in ['H','G']:
 s.camera=bpy.data.objects['C10_'+k+'_shared_sofa_height_CONDITIONAL'];s.render.filepath=str(P/'review_renders'/(k+'_C26_CLAY_DIAGNOSTIC.png'));bpy.ops.render.render(write_still=True)
(P/'clay_render_settings.json').write_text(json.dumps({'engine':'BLENDER_WORKBENCH','purpose':'Readable shape diagnostic; not physically based material or lighting comparison','geometry_visibility_camera':'Unchanged','shading':'Studio single neutral color, shadows and cavity enabled','resolution':[1920,1080]},indent=2)+'\n')
