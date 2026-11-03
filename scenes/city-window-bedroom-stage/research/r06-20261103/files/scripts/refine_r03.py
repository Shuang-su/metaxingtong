import bpy,math,json
from mathutils import Vector
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R02b_{mode}.blend'));s=bpy.context.scene
 for o in s.objects:
  if o.type!='MESH':continue
  if o.name.startswith(('WALL_arch','WINDOW_','CURTAIN_')):
   o.location.x+=1
   # Transform full world coordinates to avoid local-origin dependency.
   im=o.matrix_world.inverted()
   for v in o.data.vertices:
    w=o.matrix_world@v.co;w.z=.18+(w.z-.18)*1.4;v.co=im@w
  if o.name in ['WALL_rear_left','WALL_rear_right']:
   o.location.x+=.5;o.scale.x*= (3.7/2.7 if o.name.endswith('left') else .9/1.9)
   o.location.z*=1.4;o.scale.z*=1.4
  if o.name in ['WALL_left_inferred','WALL_right_inferred','WALL_front_inferred']:
   o.location.z*=1.4;o.scale.z*=1.4
  if o.name=='CEILING_inferred':o.location.z=7.52
  if o.name=='CENTRE_hourglass_stool':
   for v in o.data.vertices:v.co.x*=.7;v.co.y=1.25+(v.co.y-1.25)*.7;v.co.z*=.7
 for name,loc,target,lens in [('SOURCE_A',(0,-6.2,.9),(0,2.1,1.6),24),('SOURCE_B',(.1,-3.7,1.2),(0,2.0,1.7),30)]:
  o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
 o=bpy.data.objects['KEY_fixed'];o.data.type='SPOT';o.data.energy=650;o.data.spot_size=.55;o.data.spot_blend=.6;o.data.shadow_soft_size=.12;o.location=(0,1,6.8);o.rotation_euler=(Vector((0,1.25,0))-o.location).to_track_quat('-Z','Y').to_euler()
 o=bpy.data.objects['FILL_fixed'];o.location=(-5,-3,4);o.data.size=3;o.rotation_euler=(Vector((0,2,1.5))-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=400
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R03_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R03_{mode}.glb'),export_format='GLB',export_apply=True)
(D/'qa/R03-changes.json').write_text(json.dumps({'changes':['Window opening and curtain zone shifted +1 working unit x, enlarged 1.4x vertically about sill. Rear shell widths adjusted to maintain enclosure. All unmeasured hypotheses.','Central hourglass stool reduced uniformly 0.7 about its base center from visible image proportions.','Two source cameras revised to lower viewpoints, conditional uncalibrated poses.','Large disk area reflection failure retained in R01; KEY changed to finite spot, FILL moved left. All cameras share this one fixed rig.'],'limits':'No pixel-fit acceptance; no per-camera geometry or material edits.'},indent=2))
