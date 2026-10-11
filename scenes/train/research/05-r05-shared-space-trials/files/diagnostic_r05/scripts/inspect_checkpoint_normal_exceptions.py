import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c';item=next(x for x in json.loads((O/'checkpoint_manifest.json').read_text())['blends'] if x['kind']=='material');out={}
for stage in ['blend','glb']:
 if stage=='blend':bpy.ops.wm.open_mainfile(filepath=item['file'])
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'train_r05c_material_candidate.glb'))
 frames=[]
 for o in bpy.context.scene.objects:
  if not o.name.startswith('End door rounded dark window frame'):continue
  m=o.data;zeros=[]
  for i,n in enumerate(m.corner_normals):
   if n.vector.length<.5:
    l=m.loops[i];ps=[p for p in m.polygons if i in p.loop_indices];zeros.append({'loop':i,'normal':list(n.vector),'world_vertex':list(o.matrix_world@m.vertices[l.vertex_index].co),'polygons':[{'index':p.index,'area':p.area,'normal':list(p.normal),'vertices':len(p.vertices)} for p in ps]})
  frames.append({'name':o.name,'zero_normals':zeros})
 out[stage]=frames
(O/'normal_exception_detail.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
