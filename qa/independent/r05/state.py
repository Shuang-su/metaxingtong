import bpy,bmesh,json
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104/versions/R05');O=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'models/keyring-material.blend'));o=bpy.data.objects['stage-central-solid'];bm=bmesh.new();bm.from_mesh(o.data)
x={'bad_edges':[{'faces':len(e.link_faces),'coords':[list(v.co) for v in e.verts]} for e in bm.edges if not e.is_manifold]};bm.free()
side=json.loads((R/'docs/render-sidecar.json').read_text());x['light_sidecar_matrix_error']={l['name']:max(abs(bpy.data.objects[l['name']].matrix_world[i][j]-l['matrix_world'][i][j]) for i in range(4) for j in range(4)) for l in side['lights']};x['sidecar_world_fields']={k:v for k,v in side.items() if 'world' in k};(O/'state.json').write_text(json.dumps(x,indent=2));print(json.dumps(x))
