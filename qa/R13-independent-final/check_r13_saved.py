import bpy,pathlib,json,hashlib,math,struct
from mathutils.bvhtree import BVHTree
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-layout-qa-20261104');R={};N=[f'COSMETIC_{t}_proxy_{i}'for i in range(3,9)for t in ['bottle','cap']];d=[0,0,0]
for mode in ['material','white']:
 S={}
 for ver in ['R12','R13']:
  f=P/'models'/f'{ver}_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));V={};F={};B={};T={}
  for o in bpy.context.scene.objects:
   if o.type!='MESH':continue
   o.data.calc_loop_triangles();V[o.name]=[tuple(o.matrix_world@p.co)for p in o.data.vertices];F[o.name]=[tuple(t.vertices)for t in o.data.loop_triangles];B[o.name]=[[min(p[i]for p in V[o.name]),max(p[i]for p in V[o.name])]for i in range(3)];T[o.name]=BVHTree.FromPolygons(V[o.name],F[o.name],all_triangles=True)
  S[ver]=(V,F,B,T);R[ver+'_'+mode]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'internal_surface_pairs':{a+' / '+b:len(T[a].overlap(T[b]))for j,a in enumerate(N)for b in N[j+1:]if T[a].overlap(T[b])}}
 V,F,B,T=S['R13'];v0,f0,b0,t0=S['R12'];other=[n for n in V if n not in N and n!='TABLE_top'];table=B['TABLE_top'];out={}
 out['actual_delta_range']={n:[[min(V[n][j][i]-v0[n][j][i]for j in range(len(V[n]))),max(V[n][j][i]-v0[n][j][i]for j in range(len(V[n])))]for i in range(3)]for n in N}
 out['max_absolute_delta_not_expected_error']=max(abs(V[n][j][i]-v0[n][j][i]-d[i])for n in N for j in range(len(V[n]))for i in range(3));out['other224_world_geometry_exact']=all(V[n]==v0[n]and F[n]==f0[n]for n in V if n not in N)
 out['external_object_count']=len(other);out['external_aabb_candidates']={n:[o for o in other if all(B[n][i][0]<=B[o][i][1]+.001 and B[o][i][0]<=B[n][i][1]+.001 for i in range(3))]for n in N};out['external_BVH_face_pairs']={n:{o:len(T[n].overlap(T[o]))for o in other if T[n].overlap(T[o])}for n in N}
 out['minimum_AABB_distance_lower_bound']=min((math.sqrt(sum(max(0,B[o][i][0]-B[n][i][1],B[n][i][0]-B[o][i][1])**2for i in range(3))),n,o)for n in N for o in other);out['table_xy_min_margin']=min(min(B[n][i][0]-table[i][0],table[i][1]-B[n][i][1])for n in N for i in range(2));out['body_table_gap']={n:B[n][2][0]-table[2][1]for n in N if 'bottle' in n};out['body_cap_min_nearestvertex_surface']={n: min(T[n.replace('bottle','cap')].find_nearest(p)[3]for p in V[n])for n in N if 'bottle' in n};R[mode]=out
# raw GLB attributes/bufferview images compare excluding positions/node transforms
G={}
for mode in ['material','white']:
 for ver in ['R12','R13']:
  f=P/'models'/f'{ver}_{mode}.glb';b=f.read_bytes();l,t=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+l]);bl=20+l;length,typ=struct.unpack_from('<II',b,bl);bin=b[bl+8:bl+8+length]
  G[ver+'_'+mode]={'sha256':hashlib.sha256(b).hexdigest(),'images':[],'meshes':{}}
  for im in j.get('images',[]):
   bv=j['bufferViews'][im['bufferView']];data=bin[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']];G[ver+'_'+mode]['images'].append(hashlib.sha256(data).hexdigest())
  for m in j.get('meshes',[]):
   G[ver+'_'+mode]['meshes'][m.get('name','')]=[{'attributes':sorted(p['attributes']),'material':p.get('material')}for p in m['primitives']]
R['rawGLB']=G;R['scope']='Saved files read only, actual world vertices; strict expanded-AABB separation excludes external containment, not source alignment. No saves/renders.';(Q/'R13-saved-transform-check.json').write_text(json.dumps(R,indent=2));print('DONE')
