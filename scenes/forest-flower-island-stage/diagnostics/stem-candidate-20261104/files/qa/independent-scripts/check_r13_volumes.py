import bpy,json,bmesh,hashlib
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/forest-diagnostic-replay-20261104');p=R/'models/R13_root-diagnostic_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['ISLAND_turf_blades_procedural'];groups=[[]for _ in range(4500)]
for f in o.data.polygons:groups[f.vertices[0]//6].append([i%6 for i in f.vertices])
rows=[]
for i,fs in enumerate(groups):
 bm=bmesh.new();vs=[bm.verts.new(o.matrix_world@v.co)for v in o.data.vertices[i*6:i*6+6]]
 for f in fs:bm.faces.new([vs[k]for k in f])
 bm.normal_update();rows.append({'leaf':i,'signed_volume':bm.calc_volume(signed=True),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces)});bm.free()
j={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'count':4500,'nonpositive_volume':sum(r['signed_volume']<=0 for r in rows),'minimum_volume':min(r['signed_volume']for r in rows),'rows':rows};Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104/R13-individual-leaf-topology.json').write_text(json.dumps(j,indent=2));print(j['nonpositive_volume'],j['minimum_volume'])
