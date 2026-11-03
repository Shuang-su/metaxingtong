import bpy,json
from pathlib import Path
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/R04_material.blend'))
a=[]
for n in ['SOURCE_A','SOURCE_B','SOURCE_C']:
 o=bpy.data.objects[n]; a.append({'name':n,'location':list(o.location),'rotation_matrix':[list(r) for r in o.rotation_euler.to_matrix()],'focal_px':o.data.lens*1920/36,'width':1920,'height':1080})
(D/'qa/R04-camera-parameters.json').write_text(json.dumps(a,indent=2))
