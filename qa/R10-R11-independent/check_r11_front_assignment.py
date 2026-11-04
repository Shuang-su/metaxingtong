import bpy,json,pathlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');R={}
for mode in ['material','white']:
 S={}
 for ver in ['R10','R11']:
  bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'{ver}_{mode}.blend'));o=bpy.data.objects['COSMETIC_case_body'];S[ver]={'uv':[list(x.uv)for x in o.data.uv_layers.active.data],'faces':[{'index':f.index,'normal':list(f.normal),'loops':list(f.loop_indices),'material':o.data.materials[f.material_index].name}for f in o.data.polygons]}
 R[mode]={'changed_uv_loop_indices':[i for i,(a,b)in enumerate(zip(S['R10']['uv'],S['R11']['uv']))if a!=b],'before':S['R10'],'after':S['R11']}
(Q/'R11-front-assignment.json').write_text(json.dumps(R,indent=2));print({m:(x['changed_uv_loop_indices'],x['after']['faces'])for m,x in R.items()})
