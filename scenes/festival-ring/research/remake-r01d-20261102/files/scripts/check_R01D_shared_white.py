import bpy,hashlib,json,struct
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'versions/R01D';checks={};bounds={}
for fn in ['ring-remake-R01D-material.blend','ring-remake-R01D-white-same-geometry.blend','ring-remake-R01D-white-export-slots.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(out/fn));h=hashlib.sha256();count=0
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  if o.type!='MESH':continue
  count+=1;h.update(o.name.encode());h.update(repr([list(v) for v in o.matrix_world]).encode());h.update(repr([list(v.co) for v in o.data.vertices]).encode());h.update(repr([list(p.vertices) for p in o.data.polygons]).encode());bounds[o.name]=[[min((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)],[max((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)]]
 checks[fn]={'mesh_count':count,'geometry_sha256':h.hexdigest()}
checks['all_geometry_equal']=len(set(v['geometry_sha256'] for v in checks.values()))==1
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'ring-remake-R01D-white.glb'));actual={o.name:[[min((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)],[max((o.matrix_world@Vector(v))[j] for v in o.bound_box) for j in range(3)]] for o in bpy.context.scene.objects if o.type=='MESH'};errs=[abs(bounds[n][i][j]-actual[n][i][j]) for n in bounds if n in actual for i in range(2) for j in range(3)];checks['white_glb_actual_import']={'meshes':len(actual),'missing':list(set(bounds)-set(actual)),'max_bounds_diff':max(errs)}
data=(out/'ring-remake-R01D-white.glb').read_bytes();n,typ=struct.unpack_from('<II',data,12);g=json.loads(data[20:20+n]);checks['white_glb_json']={'materials':g.get('materials',[]),'images':len(g.get('images',[])),'textures':len(g.get('textures',[]))};(r/'qa/R01D-shared-white-export.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
