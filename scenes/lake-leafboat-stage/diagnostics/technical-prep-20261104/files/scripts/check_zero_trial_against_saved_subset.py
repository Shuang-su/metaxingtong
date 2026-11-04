import bpy,pathlib,json,hashlib,struct
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/leaf-only-r06-nonexact-diagnostic-replay.blend'))
rows=[];first=json.loads((R/'qa/leaf-subset-warp-tests.json').read_text())['rows'][0]
recorded={r['name']:r['geometry_sha256'] for r in first['topology']}
for o in bpy.context.scene.objects:
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(struct.pack('<3d',*(o.matrix_world@v.co)))
    for f in o.data.polygons:
        h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
    rows.append(dict(name=o.name,saved_replay_hash=h.hexdigest(),zero_trial_hash=recorded[o.name],same=h.hexdigest()==recorded[o.name]))
report=dict(scope='Audit original absolute world/local zero-parameter test against previously saved 20-mesh subset',
    identical_count=sum(r['same'] for r in rows),changed_count=sum(not r['same'] for r in rows),rows=rows)
(R/'qa/zero-trial-saved-subset-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['identical_count'],'identical;',report['changed_count'],'different')
