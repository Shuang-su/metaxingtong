import bpy,pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');S={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R11_{mode}.blend'));out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  v=[tuple(o.matrix_world@p.co)for p in o.data.vertices];o.data.calc_loop_triangles()
  ts=sorted(tuple(sorted(v[i]for i in t.vertices))for t in o.data.loop_triangles)
  uv=sorted(tuple(sorted((v[o.data.loops[i].vertex_index],tuple(o.data.uv_layers.active.data[i].uv))for i in p.loop_indices))for p in o.data.polygons)if o.data.uv_layers else []
  out[o.name]={'vertices':sorted(v),'triangles':ts,'surface_uv':uv}
 S[mode]=out
R={n:{k:S['material'][n][k]==S['white'][n][k]for k in ['vertices','triangles','surface_uv']}for n in S['material']}
(Q/'R11-shared-surface-check.json').write_text(json.dumps(R,indent=2));print({n:r for n,r in R.items()if not all(r.values())})
