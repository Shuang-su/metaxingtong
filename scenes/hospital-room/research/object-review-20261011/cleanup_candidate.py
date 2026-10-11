import bpy,bmesh,json
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/candidate');o=bpy.data.objects['Bed • observed endboard, consistent width'];bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bm.normal_update()
q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'vertices':len(bm.verts),'faces':len(bm.faces),'volume':bm.calc_volume(signed=True),'cleanup_tolerance_model_units':1e-6}
print(q);bm.to_mesh(o.data);bm.free();o.data.update();bpy.context.scene.cycles.use_denoising=False
for vl in bpy.context.scene.view_layers:vl.cycles.use_denoising=False
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_endboard_shape_candidate.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'hospital_endboard_shape_candidate.glb'),export_format='GLB',use_selection=False);(r/'candidate_cleanup_qa.json').write_text(json.dumps(q,indent=2))
