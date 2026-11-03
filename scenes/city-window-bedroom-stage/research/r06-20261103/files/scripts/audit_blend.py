"""Read-only finite mesh audit. Does not assert source fidelity or intersections."""
import bpy, bmesh, json, sys, math, hashlib
from pathlib import Path
args = sys.argv[sys.argv.index('--')+1:]
source, output = map(Path,args[:2])
bpy.ops.wm.open_mainfile(filepath=str(source))
records=[]
for obj in sorted(bpy.context.scene.objects,key=lambda o:o.name):
    if obj.type != 'MESH': continue
    bm=bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    world=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
    coords='\n'.join(','.join(format(v,'.9g') for v in p) for p in world).encode()
    records.append({'name':obj.name,'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),
      'boundary_edges':sum(e.is_boundary for e in bm.edges),
      'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
      'wire_edges':sum(e.is_wire for e in bm.edges),
      'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),
      'signed_local_volume':bm.calc_volume(signed=True),
      'finite_world_vertices':all(math.isfinite(v) for p in world for v in p),
      'world_vertex_order_sha256':hashlib.sha256(coords).hexdigest(),
      'bounds_min':[min(p[i] for p in world) for i in range(3)],
      'bounds_max':[max(p[i] for p in world) for i in range(3)],
      'materials':[s.material.name if s.material else None for s in obj.material_slots],
      'observation_status':obj.get('observation_status','UNDECLARED'),
      'object_role':obj.get('object_role','UNDECLARED')})
    bm.free()
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'input':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'mesh_count':len(records),'objects':records,
 'limits':'Mesh topology and finite-coordinate audit only. No proof of source geometry, correct contact, total scene closure, hidden surfaces, calibration or absence of inter-object intersections.'},indent=2))
