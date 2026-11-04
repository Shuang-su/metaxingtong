import bpy,json,pathlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425');Q=P/'independent-backstage-tabletop-qa-20261104';bpy.ops.wm.open_mainfile(filepath=str(P/'backstage-local-study-20261105/models/R09_material.blend'));D=json.loads((Q/'R09-case-clock-bottom-memory-trial.json').read_text());R={}
for target,numbers in [('COSMETIC_case_body',[6,7,8]),('CLOCK_red_case_proxy',[12])]:
 ob=bpy.data.objects[target];wv=[ob.matrix_world@v.co for v in ob.data.vertices];bb=D['targets'][target]['before']['bounds'];assert len(wv)==8 and all(all(v[j] in bb[j] for j in range(3))for v in wv) and len(set(tuple(v)for v in wv))==8
 out={}
 for i in numbers:
  for typ in ['bottle','cap']:
   n=f'COSMETIC_{typ}_proxy_{i}';o=bpy.data.objects[n];vs=[o.matrix_world@v.co for v in o.data.vertices];rec={}
   for phase in ['before','after']:
    box=D['targets'][target][phase]['bounds'];inside=[all(box[j][0]<v[j]<box[j][1]for j in range(3))for v in vs];rec[phase]={'strictly_inside_vertices':sum(inside),'vertices':len(vs),'all_vertices_strictly_inside':all(inside),'minimum_signed_margin':min(min(v[j]-box[j][0],box[j][1]-v[j])for v in vs for j in range(3))}
   out[n]=rec
 R[target]=out
(Q/'R09-case-clock-containment.json').write_text(json.dumps(R,indent=2));print(R)
