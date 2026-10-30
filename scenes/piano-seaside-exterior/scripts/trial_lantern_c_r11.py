"""Only area emitter orientation differs from saved B; no geometry/material edits."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa/r11/trial_c';Q.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r11/piano_seaside_material.blend'));s=bpy.context.scene;report=[]
for o in s.objects:
 if o.type!='LIGHT' or 'R11 paper exitance' not in o.name:continue
 old=list(o.rotation_euler);direction=o.rotation_euler.to_quaternion()@Vector((0,0,-1));direction.z=0;direction.normalize();o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
 report.append({'name':o.name,'rotation_before':old,'rotation_after':list(o.rotation_euler),'energy_unchanged':o.data.energy,'position_unchanged':list(o.location),'emitter_plane_clearance':.008,'previous_min_clearance':.008-o.data.size_y*.5*.35/(1+.35**2)**.5})
(Q/'area-plane-diagnosis.json').write_text(json.dumps({'only_changes':'8 area light rotations; no saved model','changes':report},indent=2)+'\n')
s.camera=bpy.data.objects['main'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.render.use_border=True;s.render.use_crop_to_border=True
r=(550,520,1000,870);s.render.border_min_x=r[0]/1920;s.render.border_max_x=r[2]/1920;s.render.border_min_y=1-r[3]/1080;s.render.border_max_y=1-r[1]/1080;s.render.filepath=str(Q/'main_lamp_native_crop.png');bpy.ops.render.render(write_still=True)
d=bpy.data.cameras.new('diagnostic_lantern');o=bpy.data.objects.new('diagnostic_lantern',d);s.collection.objects.link(o);o.location=(-1.8,.1,1.0);o.rotation_euler=(Vector((-.92,1.22,.21))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=55;s.camera=o;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(Q/'diagnostic_lantern.png');bpy.ops.render.render(write_still=True)
print('R11_TRIAL_C_COMPLETE')
