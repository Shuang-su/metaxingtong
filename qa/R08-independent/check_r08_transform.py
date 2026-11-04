import bpy,pathlib,json
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');R={}
for mode in ['material','white']:
 snapshots={}
 for ver in ['R07','R08']:
  bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'{ver}_{mode}.blend'))
  snapshots[ver]={o.name:{'m':[list(r)for r in o.matrix_world],'v':[tuple(o.matrix_world@v.co)for v in o.data.vertices]}for o in bpy.context.scene.objects if o.type=='MESH'}
 out={}
 for n,a in snapshots['R07'].items():
  b=snapshots['R08'][n]
  if a!=b:
   ds=[[y-x for x,y in zip(p,q)]for p,q in zip(a['v'],b['v'])]
   out[n]={'matrix_differences':[[i,j,b['m'][i][j]-a['m'][i][j]]for i in range(4)for j in range(4)if b['m'][i][j]!=a['m'][i][j]],'delta_min':[min(p[i]for p in ds)for i in range(3)],'delta_max':[max(p[i]for p in ds)for i in range(3)]}
 R[mode]=out
(Q/'R08-transforms.json').write_text(json.dumps(R,indent=2))
