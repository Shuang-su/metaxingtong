import bpy,json,pathlib,hashlib,math
from mathutils.bvhtree import BVHTree
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105/models/R11_material.blend'); Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-layout-qa-20261104')
bpy.ops.wm.open_mainfile(filepath=str(P)); V={};F={};B={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];V[o.name]=v;F[o.name]=[tuple(t.vertices) for t in o.data.loop_triangles];B[o.name]=[[min(p[i] for p in v),max(p[i] for p in v)]for i in range(3)]
N=[f'COSMETIC_{t}_proxy_{i}'for i in range(9)for t in ['bottle','cap']];other=[n for n in B if n not in N and n!='TABLE_top'];eps=1e-6
D=[[-.5,-.1],[-.15,.15]];table=B['TABLE_top']
for i in range(2):
 D[i][0]=max(D[i][0],max(table[i][0]+eps-B[n][i][0]for n in N));D[i][1]=min(D[i][1],min(table[i][1]-eps-B[n][i][1]for n in N))
rect=[]
for n in N:
 for o in other:
  a,b=B[n],B[o]
  if a[2][1]<b[2][0]-eps or b[2][1]<a[2][0]-eps:continue
  r=[[b[i][0]-a[i][1]-eps,b[i][1]-a[i][0]+eps]for i in range(2)]
  if all(r[i][0]<=D[i][1]and r[i][1]>=D[i][0]for i in range(2)):rect.append({'moving':n,'obstacle':o,'range':r})
xs=sorted(set([*D[0]]+[max(D[0][0],min(D[0][1],x))for r in rect for x in r['range'][0]]));ys=sorted(set([*D[1]]+[max(D[1][0],min(D[1][1],x))for r in rect for x in r['range'][1]]))
candidates=[];count=0
for xa,xb in zip(xs,xs[1:]):
 for ya,yb in zip(ys,ys[1:]):
  x,y=(xa+xb)/2,(ya+yb)/2;count+=1
  if not any(r['range'][0][0]<=x<=r['range'][0][1]and r['range'][1][0]<=y<=r['range'][1][1]for r in rect):candidates.append((x*x+y*y,x,y,xa,xb,ya,yb))
R={'model_sha_before':hashlib.sha256(P.read_bytes()).hexdigest(),'group':N,'initial_domain':[[-.5,-.1],[-.15,.15]],'table_constrained_domain':D,'tolerance':eps,'forbidden_rectangles':rect,'arrangement_cells_tested':count,'safe_cells':len(candidates),'obstacles':sorted(set(r['obstacle']for r in rect)),'bounds':{n:B[n]for n in N+['TABLE_top']}}
if candidates:
 c=min(candidates);x,y=c[1:3];R['candidate']={'dx':x,'dy':y,'safe_cell':c[3:]};T={n:BVHTree.FromPolygons([p+Vector((x,y,0)) if n in N else p for p in V[n]],F[n],all_triangles=True)for n in B};R['actual_BVH_external_pairs']={n:{o:len(T[n].overlap(T[o]))for o in other if T[n].overlap(T[o])}for n in N};R['aabb_external_candidates']={n:[o for o in other if all(B[n][i][0]+[x,y,0][i]<=B[o][i][1]+eps and B[o][i][0]<=B[n][i][1]+[x,y,0][i]+eps for i in range(3))]for n in N};R['within_group_pairs']={a+' / '+b:len(T[a].overlap(T[b]))for j,a in enumerate(N)for b in N[j+1:] if T[a].overlap(T[b])};R['containment_exclusion']='Strict AABB separation from every non-table external object excludes surface intersection and containment at this candidate; internal relationships unchanged by common translation.'
if candidates:
 R['external_object_count']=len(other)
 R['minimum_AABB_distance_lower_bound']=min((math.sqrt(sum(max(0,B[o][i][0]-(B[n][i][1]+[x,y,0][i]),B[n][i][0]+[x,y,0][i]-B[o][i][1])**2 for i in range(3))),n,o)for n in N for o in other)
 R['table_xy_clearance']=min(min(B[n][i][0]+[x,y][i]-table[i][0],table[i][1]-B[n][i][1]-[x,y][i])for n in N for i in range(2))
 R['body_table_vertical_gap_unchanged']={n:B[n][2][0]-table[2][1] for n in N if 'bottle' in n}
 R['table_is_axis_aligned_box']=len(set(tuple(round(float(q),7)for q in p)for p in V['TABLE_top']))==8 and all(all(abs(p[i]-table[i][0])<1e-6 or abs(p[i]-table[i][1])<1e-6 for i in range(3))for p in V['TABLE_top'])
R['model_sha_after']=hashlib.sha256(P.read_bytes()).hexdigest();(Q/'translation-check.json').write_text(json.dumps(R,indent=2));print('RESULT',D,len(rect),count,len(candidates),R.get('candidate'),R.get('actual_BVH_external_pairs'))
