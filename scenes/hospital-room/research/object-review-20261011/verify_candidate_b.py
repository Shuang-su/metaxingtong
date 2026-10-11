import bpy,json,hashlib,bmesh
from pathlib import Path
root=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit');out=root/'candidate_b'
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));r={}
 for o in bpy.context.scene.objects:
  v={'type':o.type,'matrix':[list(row) for row in o.matrix_world],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
  if o.type=='MESH':v['mesh']=hashlib.sha256(repr(([tuple(x.co) for x in o.data.vertices],[tuple(x.vertices) for x in o.data.polygons])).encode()).hexdigest()
  if o.type=='CAMERA':v['lens']=o.data.lens
  r[o.name]=v
 return r
base=snap(root/'models/extracted/hospital_complete_materials.blend');cand=snap(out/'hospital_endboard_shape_B.blend')
report={'object_count_before':len(base),'object_count_after':len(cand),'added':list(cand.keys()-base.keys()),'removed':list(base.keys()-cand.keys()),'changed_objects':[k for k in base.keys()&cand.keys() if base[k]!=cand[k]]}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'hospital_endboard_shape_B.glb'))
r=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and 'observed endboard' in o.name:
  bm=bmesh.new();bm.from_mesh(o.data);r.append({'name':o.name,'verts':len(bm.verts),'edges':len(bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges_before_weld':sum(not e.is_manifold for e in bm.edges)})
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);r[-1]['nonmanifold_edges_after_position_weld']=sum(not e.is_manifold for e in bm.edges);r[-1]['volume_after_weld']=bm.calc_volume(signed=True);bm.free()
report['real_glb_reimport']=r;report['acceptance']='Technical checks only; source fidelity not accepted';(out/'candidate_roundtrip_and_scope_qa.json').write_text(json.dumps(report,indent=2))
