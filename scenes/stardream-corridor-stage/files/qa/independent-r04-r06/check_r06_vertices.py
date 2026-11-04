import bpy,json,pathlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105/models');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105');out={}
for mode in ['material','white']:
 snaps=[]
 for v in ['R05','R06']:
  bpy.ops.wm.open_mainfile(filepath=str(P/f'{v}_{mode}.blend'));snaps.append({o.name:([tuple(p.co) for p in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in bpy.context.scene.objects if o.type=='MESH'})
 rows={}
 for n,(a,af) in snaps[0].items():
  b,bf=snaps[1][n]
  if a==b:continue
  ch=[{'index':i,'old':x,'new':y,'delta':[y[k]-x[k] for k in range(3)]} for i,(x,y) in enumerate(zip(a,b)) if x!=y];rows[n]={'vertex_count_same':len(a)==len(b),'face_lists_same':af==bf,'changed_count':len(ch),'changes':ch}
 out[mode]=rows
(Q/'R06-local-vertex-diff.json').write_text(json.dumps(out,indent=2));print('DONE')
