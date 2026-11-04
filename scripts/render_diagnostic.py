import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Quaternion
import math
R=Path(__file__).resolve().parents[1];d=json.loads((R/'docs/diagnostic-configuration-b.json').read_text());C=d['camera'];L=d['light'];preview='preview' in sys.argv
for label,file in [('baseline',R/'inputs/keyring-material.blend'),('candidate',R/'models'/('r07b-material.blend' if (R/'models/r07b-material.blend').exists() else 'r07-material.blend'))]:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;c=s.objects.get(C['name'])
 if c is None:bpy.ops.object.camera_add();c=bpy.context.object;c.name=C['name']
 c.location=C['location'];c.data.lens=C['lens'];c.data.sensor_width=C['sensor_width'];c.rotation_mode='QUATERNION';c.rotation_quaternion=(Vector(C['target'])-c.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),math.radians(C['roll_degrees']));s.camera=c
 bpy.ops.object.light_add(type='AREA',location=L['location']);l=bpy.context.object;l.name=L['name'];l.data.energy=L['energy'];l.data.color=L['color'];l.data.size=L['size'];l.data.shape='SQUARE';l.rotation_euler=(Vector(L['target'])-l.location).to_track_quat('-Z','Y').to_euler()
 s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=8 if preview else 32;s.cycles.use_denoising=False;s.render.resolution_percentage=40 if preview else 100;s.render.filepath=str(R/'renders'/f'{"preview-b" if preview else "diagnostic-b"}-{label}.png');bpy.ops.render.render(write_still=True)
