import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1];d=json.loads((R/'docs/diagnostic-configuration-b.json').read_text());C=d['camera']
for v in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/f'r07-{v}.blend'));s=bpy.context.scene;c=s.objects[C['name']];c.location=C['location'];c.data.lens=C['lens'];c.rotation_mode='QUATERNION';c.rotation_quaternion=(Vector(C['target'])-c.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),math.radians(C['roll_degrees']));bpy.context.view_layer.update()
 if v=='material':
  side=json.loads((R/'docs/render-sidecar.json').read_text());side['cameras']=[{'name':o.name,'matrix_world':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end,'role':'additional artificial underside diagnostic B' if o.name==C['name'] else 'unchanged R06 camera; coverage only when R07 actually rendered'} for o in s.objects if o.type=='CAMERA'];side['diagnostic_light_restore']='docs/diagnostic-configuration-b.json and scripts/render_diagnostic.py, extra AREA only for identical before/after diagnostic';(R/'docs/render-sidecar-b.json').write_text(json.dumps(side,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/f'r07b-{v}.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'models'/f'r07b-{v}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=True)
