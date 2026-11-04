import bpy,pathlib,json,hashlib,datetime,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];model=R/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'
bpy.ops.wm.open_mainfile(filepath=str(model));shell=bpy.data.objects['LEAF_001_ThinConcaveShell']
m=shell.data;m.calc_loop_triangles();v=[shell.matrix_world@p.co for p in m.vertices]
tris=[tuple(t.vertices) for t in m.loop_triangles];tree=BVHTree.FromPolygons(v,tris,all_triangles=True)
eps=1e-5
def probe(p):
    hit,n,idx,d=tree.ray_cast(Vector((p.x,p.y,8)),Vector((0,0,-1)),20)
    if hit is None:return dict(point=list(p),state='no_vertical_shell_hit')
    bottom,n2,idx2,d2=tree.ray_cast(hit+Vector((0,0,-1e-5)),Vector((0,0,-1)),20)
    near,nn,ni,nd=tree.find_nearest(p)
    if bottom is None:return dict(point=list(p),state='no_second_shell_hit')
    top_gap=p.z-hit.z;bottom_gap=p.z-bottom.z
    state='above' if top_gap>eps else ('below' if bottom_gap < -eps else ('inside' if top_gap < -eps and bottom_gap>eps else 'near_surface'))
    return dict(point=list(p),state=state,vertical_gap_above_upper=top_gap,vertical_gap_above_lower=bottom_gap,
        nearest_distance=nd,nearest_signed_normal_distance=(p-near).dot(nn),upper_hit=list(hit),lower_hit=list(bottom))

rows=[]
for o in bpy.context.scene.objects:
    if not o.name.startswith(('LEAF_002','LEAF_003')):continue
    sides=9 if o.name.startswith('LEAF_002') else 6
    verts=[o.matrix_world@q.co for q in o.data.vertices];assert len(verts)%sides==0
    rings=[]
    for i in range(len(verts)//sides):
        points=verts[i*sides:(i+1)*sides];points+= [(points[j]+points[(j+1)%sides])*.5 for j in range(sides)]
        samples=[probe(p) for p in points]
        states={state:sum(p['state']==state for p in samples) for state in ['above','below','inside','near_surface','no_vertical_shell_hit','no_second_shell_hit']}
        valid=[p for p in samples if 'vertical_gap_above_upper' in p]
        rings.append(dict(index=i,center=list(sum(verts[i*sides:(i+1)*sides],Vector())/sides),counts=states,
            all_sampled_ring_surface_above=states['above']==len(samples),min_upper_gap=min(p['vertical_gap_above_upper'] for p in valid),
            max_upper_gap=max(p['vertical_gap_above_upper'] for p in valid),min_lower_gap=min(p['vertical_gap_above_lower'] for p in valid),
            min_nearest_distance=min(p['nearest_distance'] for p in valid),samples=samples))
    face_samples=[probe(sum((verts[i] for i in f.vertices),Vector())/len(f.vertices)) for f in o.data.polygons]
    rows.append(dict(name=o.name,sides=sides,ring_count=len(rings),rings=rings,
        wholly_above_sampled_ring_indices=[r['index'] for r in rings if r['all_sampled_ring_surface_above']],
        any_below_lower_ring_indices=[r['index'] for r in rings if r['counts']['below']],face_center_samples=face_samples))
report=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),input_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
    fixture='Nonexact 20-mesh replay; primary shell full hash does not equal archived original. Earlier 1717 ray samples match, not complete geometry recovery.',
    scope='Every vein ring vertex and ring-edge midpoint, plus all polygon centers, probed against actual closed replayed leaf shell. Ringwise positivity is sampled evidence, not a continuous triangle separation proof.',
    epsilon_model_units=eps,source_accepted=False,model_modified=False,rendered_images=0,rows=rows)
(R/'qa/vein-shell-support-samples.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
    last=row['rings'][-1]
    print(row['name'],'above rings',row['wholly_above_sampled_ring_indices'],'below rings',row['any_below_lower_ring_indices'],
          'last ring min gap',last['min_upper_gap'],'min near',last['min_nearest_distance'])
