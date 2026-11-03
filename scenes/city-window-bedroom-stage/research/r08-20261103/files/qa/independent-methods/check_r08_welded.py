import bpy,bmesh,json,hashlib
from pathlib import Path
D=Path('/workspace/shared/metaxingtong-production-20261103/models');out=Path('/workspace/shared/novelty-review-20261103/qa')
files=[]
for name in ['R08_material.blend','R08_white.blend','R08_material.glb','R08_white.glb']:
 p=D/name
 if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
 objs=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);before=len(bm.verts)
  if p.suffix=='.glb':bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bm.normal_update();objs.append({'name':o.name,'before_vertices':before,'diagnostic_vertices':len(bm.verts),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_local_volume':bm.calc_volume(signed=True)});bm.free()
 files.append({'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':objs})
res={'files':files,'glb_weld_tolerance_local_units':1e-6,'scope':'In-memory diagnostic only, input files unchanged. Welding handles glTF attribute-split vertices, does not establish inter-object contact/intersections or source fidelity.'}
(out/'R08-welded-topology-independent.json').write_text(json.dumps(res,indent=2))
for r in files:
 print(r['file'],{k:sum(x[k] for x in r['objects']) for k in ['boundary_edges','nonmanifold_edges','degenerate_faces']},'negative',sum(x['signed_local_volume']<0 for x in r['objects']))
