import bpy,math,json
from pathlib import Path
from mathutils import Quaternion
r=Path(__file__).resolve().parents[1];out=r/'versions/R01C';out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(r/'versions/R01B/ring-remake-R01B-shared-candidate.blend'));s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('LED_PANEL'):
  for uv in o.data.uv_layers.active.data:uv.uv.x=1-uv.uv.x
cam=bpy.data.objects['C_OBLIQUE_UNCALIBRATED'];D=7;e=.45;az=-math.pi/3;cam.location=(D*math.cos(e)*math.sin(az),-D*math.cos(e)*math.cos(az),D*math.sin(e));cam.rotation_quaternion=(-cam.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),-.02);cam.data.shift_y=(1000-540)/1920
s['stage_status']='R01C UV direction repair + separately declared oblique camera hypothesis, geometry unchanged';bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R01C-shared-candidate.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'ring-remake-R01C-shared-candidate.glb'),export_format='GLB')
(r/'qa/R01C-scope.json').write_text(json.dumps({'changes':['All LED panel UV horizontal reversed, same shared material','Oblique camera elevation .05 to .45rad, principalY980 to1000, D7/az-60/f1300 unchanged'],'unchanged':'all mesh vertices/transforms/faces, other cameras, lights, platform and arcs','camera_status':'conditional test, not calibrated; no passing metric claimed'},indent=2))
for n,c in [('source4k','C_4K_CONDITIONAL'),('front','C_FRONT_CONDITIONAL'),('oblique','C_OBLIQUE_UNCALIBRATED')]:
 s.camera=bpy.data.objects[c];s.render.resolution_x=960;s.render.resolution_y=540;s.render.filepath=str(out/(n+'-low-material.png'));bpy.ops.render.render(write_still=True)
