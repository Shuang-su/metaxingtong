import bpy,json,pathlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-ceiling-qa-20261105');S={};R={}
for mode in ['material','white']:
 for v in ['R07','R08']:
  bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'{v}_{mode}.blend'));S[v]={o.name:[tuple(o.matrix_world@p.co) for p in o.data.vertices] for o in bpy.context.scene.objects if o.type=='MESH'}
 rr={}
 for n,a in S['R07'].items():
  b=S['R08'][n]
  if a==b:continue
  axis=2 if n.startswith('SPOT') else 1;mx=max(p[axis] for p in a);changed=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y];expect=[i for i,p in enumerate(a) if abs(p[axis]-mx)<1e-6]
  rr[n]={'vertex_counts':[len(a),len(b)],'changed_ids':changed,'expected_cap_ids':expect,'only_expected_cap_changed':set(changed)==set(expect),'max_orthogonal_drift':max(abs(x[k]-y[k]) for x,y in zip(a,b) for k in range(3) if k!=axis),'axis_displacements':sorted(set(b[i][axis]-a[i][axis] for i in changed)),'front_or_bottom_unchanged':all(a[i]==b[i] for i in range(len(a)) if i not in expect)}
 R[mode]=rr
(Q/'R08-vertices.json').write_text(json.dumps(R,indent=2));print('DONE')
