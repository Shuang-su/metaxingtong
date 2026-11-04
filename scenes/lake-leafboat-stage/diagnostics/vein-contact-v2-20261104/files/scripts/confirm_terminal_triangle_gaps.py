import bpy,pathlib,json,sys,math,datetime,hashlib,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from triangle_distance import triangle_triangle2,tests
R=pathlib.Path(__file__).resolve().parents[1]
model=R/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'
bpy.ops.wm.open_mainfile(filepath=str(model));shell=bpy.data.objects['LEAF_001_ThinConcaveShell'];m=shell.data;m.calc_loop_triangles()
vs=[shell.matrix_world@v.co for v in m.vertices];indices=[tuple(t.vertices) for t in m.loop_triangles]
tris=[tuple(tuple(vs[i]) for i in f) for f in indices];tree=BVHTree.FromPolygons(vs,indices,all_triangles=True)
checks=tests();rows=[];started=time.time()
for o in bpy.context.scene.objects:
    if not o.name.startswith(('LEAF_002','LEAF_003')):continue
    sides=9 if o.name.startswith('LEAF_002') else 6
    m=o.data;m.calc_loop_triangles();vv=[o.matrix_world@v.co for v in m.vertices];rings=len(vv)//sides;sidefaces=(rings-1)*sides
    selected=[t for t in m.loop_triangles if ((t.polygon_index<2*sides or t.polygon_index==sidefaces) if sides==9 else
        ((rings-3)*sides<=t.polygon_index<sidefaces or t.polygon_index==sidefaces+1))]
    distances=[]
    for t in selected:
        points=[vv[i] for i in t.vertices];center=sum(points,Vector())/3;radius=max((p-center).length for p in points)
        upper=min(tree.find_nearest(p)[3] for p in points);search=radius+upper+1e-5
        candidates={x[2] for x in tree.find_nearest_range(center,search)};assert candidates
        a=tuple(tuple(p) for p in points);best=float('inf');bestidx=None
        for i in candidates:
            d2=triangle_triangle2(a,tris[i])
            if d2<best:best=d2;bestidx=i
        distance=math.sqrt(best);assert distance<=upper+1e-5
        distances.append(dict(tube_triangle=t.index,tube_polygon=t.polygon_index,minimum_distance=distance,
            nearest_shell_triangle=bestidx,candidates_tested=len(candidates),search_radius=search))
    row=dict(name=o.name,scope='first two ring bands and start cap' if sides==9 else 'last two ring bands and terminal cap',
        triangle_count=len(selected),minimum_distance=min(x['minimum_distance'] for x in distances),triangles=distances)
    rows.append(row);print(o.name,row['triangle_count'],row['minimum_distance'],flush=True)
    report=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixture_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
        method='All selected tube triangles: candidate leaf triangles within center radius + a known vertex-to-shell upper distance +1e-5; exact feature-distance/segment-face tests in Python float64. The radius bound excludes farther triangles by triangle inequality. Blender BVH float32 candidate search has the stated margin.',
        numerical_margin=1e-5,scope='Selected terminal bands only, against the entire closed replayed shell. Not a whole-vein collision sweep or source contact verification.',
        tests=checks,elapsed_seconds=time.time()-started,rows=rows,source_accepted=False,production_blend_tested=False)
    (R/'qa/terminal-triangle-distances.json').write_text(json.dumps(report,indent=2)+'\n')
print('Selected terminal gaps checked; no geometry changed.',flush=True)
