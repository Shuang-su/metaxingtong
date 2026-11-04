import bpy,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'models/R01_material.blend'));D={}
for n in ['SOURCE_08_wide','SOURCE_23_oblique','SOURCE_26_side']:
 o=bpy.data.objects[n];D[n]={'matrix_world':[list(r) for r in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width}
(P/'qa/R01-camera-seeds.json').write_text(json.dumps(D,indent=2))
