import bpy,bmesh,pathlib,json,itertools,math
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-ceiling-qa-20261105');S={}
def parts(o):
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();unseen=set(bm.verts);out=[]
 while unseen:
  pending=[unseen.pop()];group=set(pending)
  while pending:
   for e in pending.pop().link_edges:
    for v in e.verts:
     if v in unseen:unseen.remove(v);group.add(v);pending.append(v)
  vs=[o.matrix_world@v.co for v in group];bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)];faces={f for v in group for f in v.link_faces};corner_ok=all(all(min(abs(v[i]-b) for b in bounds[i])<1e-7 for i in range(3)) for v in vs);axis_faces=all(any(max((o.matrix_world@v.co)[i] for v in f.verts)-min((o.matrix_world@v.co)[i] for v in f.verts)<1e-7 for i in range(3)) for f in faces)
  out.append({'bounds':bounds,'verts':len(group),'faces':len(faces),'box_corners':corner_ok,'axis_faces':axis_faces,'nonmanifold':sum(not e.is_manifold for e in {e for v in group for e in v.link_edges})})
 bm.free();return out
for version in ['R06','R07']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'{version}_white.blend'));S[version]={o.name:parts(o) for o in bpy.context.scene.objects if o.name.startswith('CEILING_crossrail') or o.name=='CEILING_center_rail'}
def inside(p,boxes):return any(all(b[i][0]-1e-7<=p[i]<=b[i][1]+1e-7 for i in range(3)) for b in boxes)
R={'components':S,'union_tests':{}}
for n in S['R06']:
 if 'crossrail' not in n:continue
 old=[x['bounds'] for x in S['R06'][n]+S['R06']['CEILING_center_rail']];new=[x['bounds'] for x in S['R07'][n]+S['R07']['CEILING_center_rail']];axes=[]
 for i in range(3):
  b=sorted(set(v for box in old+new for v in box[i]));axes.append(sorted(set(b+[(x+y)/2 for x,y in zip(b,b[1:])]+[b[0]-.01,b[-1]+.01])))
 bad=[];total=0
 for p in itertools.product(*axes):
  total+=1
  if inside(p,old)!=inside(p,new):bad.append(p)
 R['union_tests'][n]={'axis_cell_and_boundary_samples':total,'mismatches':bad,'note':'Exhaustive endpoint/midpoint Cartesian partition for verified axis-aligned boxes, tolerance1e-7; union with center only, not entire room.'}
(Q/'R07-union.json').write_text(json.dumps(R,indent=2));print('DONE')
