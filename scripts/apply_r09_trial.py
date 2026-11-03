import bpy,json
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parents[1];records=json.load(open(D/'qa/R09-camera-fit.json'))['results'];bpy.ops.wm.open_mainfile(filepath=str(D/'models/R08_material.blend'))
for a in records:
 o=bpy.data.objects[a['camera']];o.location=a['fitted'][:3];o.rotation_euler=Matrix(a['rotation_matrix']).to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(D/'models/R09_camera_trial.blend'))
