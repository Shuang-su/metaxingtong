import bpy,pathlib,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'))
o=bpy.data.objects['LEAF_001_ThinConcaveShell'];m=o.data;m.calc_loop_triangles()
v=[o.matrix_world@p.co for p in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles]
tree=BVHTree.FromPolygons(v,tris,all_triangles=True)
def crossings(origin,direction):
    origin=Vector(origin);direction=Vector(direction).normalized();rows=[]
    for _ in range(64):
        p,n,index,d=tree.ray_cast(origin,direction,30)
        if p is None:return rows
        rows.append(dict(point=list(p),normal=list(n),triangle=index,step_distance=d))
        origin=p+direction*1e-5
    raise RuntimeError('Intersection loop did not terminate')
x=json.loads((R/'qa/vein-shell-support-samples.json').read_text())
suspects=[p for r in x['rows'] for ring in r['rings'] for p in ring['samples'] if p['state']=='below']
rows=[]
for p in suspects:
    xyz=p['point'];up=crossings(xyz,(0,0,1));dirs=[(0,0,1),(0,0,-1),(.371,.227,.901),(-.269,.414,.87),(.231,-.193,-.953)]
    votes=[]
    for d in dirs:
        hits=crossings(xyz,d);votes.append(dict(direction=d,intersection_count=len(hits),odd_inside=bool(len(hits)%2),hits=hits))
    rows.append(dict(original_sample=p,vertical_line_from_above=crossings((xyz[0],xyz[1],8),(0,0,-1)),ray_votes=votes,
        unanimous_inside=all(t['odd_inside'] for t in votes),unanimous_outside=all(not t['odd_inside'] for t in votes)))
report=dict(scope='Recheck samples below the second vertical intersection. More than two hits can occur near a curled/tapered shell; below second hit does not by itself mean below the complete shell.',
    source_accepted=False,rows=rows,local_BVHTree_find_nearest_range_doc=BVHTree.find_nearest_range.__doc__)
(R/'qa/tip-multiple-ray-intervals.json').write_text(json.dumps(report,indent=2)+'\n')
for r in rows:print('vertical crossings',len(r['vertical_line_from_above']),'inside votes',[v['odd_inside'] for v in r['ray_votes']])
print(BVHTree.find_nearest_range.__doc__)
