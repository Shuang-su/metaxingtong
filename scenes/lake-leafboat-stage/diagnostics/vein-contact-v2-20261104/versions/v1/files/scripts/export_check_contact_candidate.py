import bpy,pathlib,json,hashlib,math
from mathutils.kdtree import KDTree
R=pathlib.Path(__file__).resolve().parents[1];p=R/'models/leaf-only-contact-candidate-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(p));old={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.context.scene.objects}
assert len(old)==20 and all(o.type=='MESH' for o in bpy.context.scene.objects)
out=R/'models/leaf-only-contact-candidate-v2.glb';assert not out.exists()
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_cameras=False,export_lights=False,export_apply=False,export_extras=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out));new={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.context.scene.objects if o.type=='MESH'};assert set(old)==set(new)
def directed(a,b):
 t=KDTree(len(b))
 for i,p in enumerate(b):t.insert(p,i)
 t.balance();return max(t.find(p)[2] for p in a)
rows=[dict(name=n,source_vertices=len(old[n]),import_vertices=len(new[n]),bidirectional_max_error=max(directed(old[n],new[n]),directed(new[n],old[n]))) for n in old]
assert max(r['bidirectional_max_error'] for r in rows)<1e-5
report=dict(scope='Only 20-mesh technical fixture, not original full scene; neutral diagnostic materials; no cameras or water/forest included.',blend_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),blend_bytes=p.stat().st_size,glb_bytes=out.stat().st_size,names_equal=True,rows=rows)
(R/'qa/partial-glb-roundtrip.json').write_text(json.dumps(report,indent=2)+'\n');print(report['blend_bytes'],report['glb_bytes'],'max error',max(r['bidirectional_max_error'] for r in rows))
