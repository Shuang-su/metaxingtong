import bpy,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'models/R05_material.blend'));out={}
for n in ['SOURCE_13_high','SOURCE_21_high']:
 o=bpy.data.objects[n];out[n]={'matrix_world':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width}
(P/'qa/R05-camera-seeds.json').write_text(json.dumps(out,indent=2))
