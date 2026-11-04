import bpy,json,sys,re,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]);dg=bpy.context.evaluated_depsgraph_get();d={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();v=[o.matrix_world@x.co for x in me.vertices];p=[list(f.vertices)for f in me.polygons];d[o.name]={'tree':BVHTree.FromPolygons(v,p),'bounds':[[min(x[i]for x in v)for i in range(3)],[max(x[i]for x in v)for i in range(3)]]};ev.to_mesh_clear()
def intersects(a,b):
 aa=d[a]['bounds'];bb=d[b]['bounds']
 if any(aa[1][i]<bb[0][i]or bb[1][i]<aa[0][i]for i in range(3)):return False
 return bool(d[a]['tree'].overlap(d[b]['tree']))
mounts=[]
for n in d:
 m=re.match(r'inferred frame (\d+) ceiling mount',n)
 if not m:continue
 edges=[x for x in d if x.startswith('frame '+m.group(1)+' edge')]
 mounts.append({'name':n,'intersecting_frame_edges':[x for x in edges if intersects(n,x)],'intersects_roof':intersects(n,'tunnel upper dark return')})
# Surface-intersection adjacency for abstract edge decor, plus floor penetration.
names=[n for n in d if n.startswith('decor cluster')];parents={n:n for n in names}
def root(n):
 while parents[n]!=n:n=parents[n]
 return n
pairs=[]
for i,a in enumerate(names):
 for b in names[i+1:]:
  if intersects(a,b):parents[root(a)]=root(b);pairs.append([a,b])
groups={}
for n in names:groups.setdefault(root(n),[]).append(n)
groups=[{'objects':v,'floor_touch_or_penetration':any(d[n]['bounds'][0][2]<=1e-5 for n in v),'min_z':min(d[n]['bounds'][0][2]for n in v)}for v in groups.values()]
r={'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'method':'Evaluated world-space BVHTree surface triangle intersections; AABB rejects non-overlapping candidates. Decor support means same connected surface-intersection component reaches z<=1e-5. Does not prove structural load capacity; full-containment pairs without surface intersections are not detected.','mount_contacts':mounts,'decor_components':groups,'floating_decor_components':[g for g in groups if not g['floor_touch_or_penetration']],'decor_intersection_pair_count':len(pairs)}
out.write_text(json.dumps(r,indent=2));print('MOUNTS',mounts);print('DECOR',len(groups),'floating',len(r['floating_decor_components']),'objects',sum(len(g['objects'])for g in r['floating_decor_components']))
