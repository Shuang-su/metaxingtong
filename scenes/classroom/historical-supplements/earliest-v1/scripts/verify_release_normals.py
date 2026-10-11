import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
report={}
for v in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/Xingtong_Classroom_{v}.blend'))
 neg=[];openmesh=[];count=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  count+=1;bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges)
  if not closed:openmesh.append(o.name)
  elif bm.calc_volume(signed=True)<-1e-10:neg.append(o.name)
  bm.free()
 report[v]={'mesh_count':count,'closed_negative_volume_objects':neg,'open_mesh_count':len(openmesh),'open_meshes':openmesh,'pass':len(neg)==0}
report['method']='BMesh signed-volume check on closed meshes; open surfaces reported separately. No geometry modified.'
json.dump(report,open(R/'qa/normal_orientation_check.json','w'),indent=2)
print(report)
