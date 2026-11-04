import bpy,runpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
g=runpy.run_path(str(R/'scripts/test_bridges.py'))
CAM={'name':'diagnostic-underbridge-fixed','location':[5.6,0,-2],'target':[5.5,0,-.35],'lens':22,'sensor_width':36,'purpose':'artificial underside close view, not source; original 11 cameras unchanged'}
LIGHT={'name':'diagnostic-only-underfill','location':[5.5,-1,-2],'target':[5.5,0,-.4],'energy':500,'color':[1,1,1],'size':2,'purpose':'same extra AREA for before and after only; never added to source scene or final production BLEND'}
def setup():
 s=bpy.context.scene;bpy.ops.object.camera_add(location=CAM['location']);c=bpy.context.object;c.name=CAM['name'];c.data.lens=CAM['lens'];c.data.sensor_width=36;c.rotation_euler=(Vector(CAM['target'])-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
 bpy.ops.object.light_add(type='AREA',location=LIGHT['location']);l=bpy.context.object;l.name=LIGHT['name'];l.data.energy=LIGHT['energy'];l.data.color=LIGHT['color'];l.data.size=LIGHT['size'];l.rotation_euler=(Vector(LIGHT['target'])-l.location).to_track_quat('-Z','Y').to_euler()
 s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_percentage=40;return s
s=setup();s.render.filepath=str(R/'renders/preview-candidate-under.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/keyring-material.blend'));s=setup();s.render.filepath=str(R/'renders/preview-baseline-under.png');bpy.ops.render.render(write_still=True)
(R/'docs/diagnostic-configuration.json').write_text(json.dumps({'camera':CAM,'light':LIGHT,'preview_resolution_percentage':40,'nominal_resolution':[1192,671],'samples':8,'denoising':False},indent=2))
