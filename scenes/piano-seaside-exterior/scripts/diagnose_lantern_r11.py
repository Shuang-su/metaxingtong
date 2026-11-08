"""Read-only R10 diagnosis. Diagnostic light changes never save a model."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/r11/diagnosis';Q.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r10/piano_seaside_material.blend'));s=bpy.context.scene
lamps=[o for o in s.objects if o.type=='LIGHT' and o.get('evidence_id') in ['L01_lantern','L02_lantern']]
report={'base_commit':'f4138510cde1fd199b49d4fad8bb1a4fc429cb10','engine':s.render.engine,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'lights':[],'materials':[]}
dg=bpy.context.evaluated_depsgraph_get()
for o in lamps:
 rays=[]
 for direction in [(0,0,1),(1,0,0),(0,-1,0),(0,0,-1),(.4,0,-.5)]:
  hit,loc,n,ix,ob,ma=s.ray_cast(dg,o.location,Vector(direction).normalized(),distance=2)
  rays.append({'direction':direction,'first_hit':ob.name if hit else None,'distance':(loc-o.location).length if hit else None})
 report['lights'].append({'name':o.name,'position':list(o.location),'energy':o.data.energy,'color':list(o.data.color),'radius':o.data.shadow_soft_size,'use_shadow':o.data.use_shadow,'rays':rays})
for m in bpy.data.materials:
 if m.users and ('paper' in m.name.lower() or 'lantern' in m.name.lower() or 'back panel' in m.name.lower()):
  b=m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
  report['materials'].append({'name':m.name,'emission_strength':b.inputs['Emission Strength'].default_value if b else None,'emission_color':list(b.inputs['Emission Color'].default_value) if b else None,'images':[{'name':n.image.name,'color_space':n.image.colorspace_settings.name} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]})
(Q/'r10-settings-and-occlusion.json').write_text(json.dumps(report,indent=2)+'\n')
# Use existing main camera and native pixel crop. No additional camera or mesh edits.
s.camera=bpy.data.objects['main'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32
s.render.use_border=True;s.render.use_crop_to_border=True
rect=(550,520,1000,870);s.render.border_min_x=rect[0]/1920;s.render.border_max_x=rect[2]/1920;s.render.border_min_y=1-rect[3]/1080;s.render.border_max_y=1-rect[1]/1080
def render(label):s.render.filepath=str(Q/(label+'.png'));bpy.ops.render.render(write_still=True)
render('A_R10_unchanged')
for o in lamps:o.data.energy=0
render('B_point_lights_zero')
for o,orig in zip(lamps,report['lights']):o.data.energy=orig['energy'];o.location.z+=.075
render('C_points_above_bulb_same_energy')
for o,orig in zip(lamps,report['lights']):o.location=orig['position'];o.data.use_shadow=False
render('D_shadow_disabled_DIAGNOSTIC_ONLY')
(Q/'diagnostic-crop.json').write_text(json.dumps({'camera':'main unchanged','full_resolution':[1920,1080],'xyxy':rect,'samples':32,'labels':{'A':'unmodified R10','B':'both lantern points zero energy only','C':'both lantern points raised 0.075 units, unchanged energy and shadow on','D':'points reset to R10 position/energy, shadow disabled only; not a production proposal'},'no_blend_saved':True},indent=2)+'\n')
print('R11_OCCLUSION_DIAGNOSIS_COMPLETE')
