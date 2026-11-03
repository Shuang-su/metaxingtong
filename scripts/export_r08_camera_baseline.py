import bpy,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];p=D/'models/R08_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p));out=[]
for n in ['SOURCE_A','SOURCE_B','SOURCE_C','SOURCE_D_low','SOURCE_E_oblique','SOURCE_F_fan4k']:
 o=bpy.data.objects[n];w=3840 if n=='SOURCE_F_fan4k' else 1920
 out.append({'name':n,'location':list(o.location),'rotation_matrix':[list(r) for r in o.rotation_euler.to_matrix()],'lens_mm':o.data.lens,'sensor_width_mm':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'focal_px':o.data.lens*w/o.data.sensor_width,'width':w,'height':w*9//16})
(D/'qa/R09-baseline-camera-parameters.json').write_text(json.dumps({'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cameras':out},indent=2))
