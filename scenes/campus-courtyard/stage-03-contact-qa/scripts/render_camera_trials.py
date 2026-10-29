import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];D=R/'stage-03-contact-qa';T=D/'research/camera-only-trials';T.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(D/'campus-courtyard_material.blend'));s=bpy.context.scene
trials=json.loads((D/'qa/camera_only_trials.json').read_text())
for name,p in trials.items():
 c=bpy.data.objects[name];c.location=p['location'];c.rotation_euler=(Vector(p['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=p['lens_mm']
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50;s.cycles.samples=24
bpy.ops.wm.save_as_mainfile(filepath=str(T/'rejected_camera_only_trial.blend'),compress=True)
for name in trials:
 s.camera=bpy.data.objects[name];s.render.filepath=str(T/(name+'_trial_960x540.png'));bpy.ops.render.render(write_still=True)
