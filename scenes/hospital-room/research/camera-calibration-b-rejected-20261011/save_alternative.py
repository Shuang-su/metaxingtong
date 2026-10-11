import bpy,json,math
from mathutils import Vector,Quaternion
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/camera_calibration_b');j=json.loads((r/'fit_results.json').read_text());x=j['G']['candidates']['pose6']['parameters'];c=bpy.data.objects['MATCH_G_Sofa_And_Bed'];v=Vector(x[:3]);m=Quaternion(v.normalized(),v.length).to_matrix().to_4x4();m.translation=Vector(x[3:6]);c.matrix_world=m;c.data.lens=math.exp(x[6]);c.data.shift_x=-x[7]/1920;c.data.shift_y=x[8]/1920;bpy.context.scene.camera=c;bpy.context.scene.render.filepath=str(r/'G_fixed_focal_alternative_raw.png');bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_B_fixed_focal_alternative_NOT_ADOPTED.blend'))
