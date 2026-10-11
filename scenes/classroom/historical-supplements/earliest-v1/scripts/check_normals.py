import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'))
r=[]
for name in ['Continuous wood plank floor','Front pale blue plaster wall','Green teaching chalkboard','R1C1 rounded oak desktop','Window glass 1_1_1','Observed red plant pot','Observed dark door leaf']:
 o=bpy.data.objects.get(name)
 if o:
  bm=bmesh.new();bm.from_mesh(o.data);vol=bm.calc_volume(signed=True);r.append({'name':name,'signed_volume':vol,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)});bm.free()
json.dump(r,open(R/'qa/normal_orientation_check.json','w'),indent=2);print(r)
