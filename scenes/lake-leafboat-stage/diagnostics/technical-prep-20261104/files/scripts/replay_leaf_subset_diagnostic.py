"""Replay only 20 leaf meshes from verified scripts. NOT original BLEND recovery."""
import bpy,bmesh,math,pathlib,json,hashlib,struct,sys,ast
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,sqrt
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from leaf_local_warp import Parameters,forward,inverse
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
c=bpy.data.collections.new('01_LeafBoat');s.collection.children.link(c);collections={'01_LeafBoat':c}
leaf=bpy.data.materials.new('DiagnosticNeutralShell_NOT_ORIGINAL_MATERIAL')
vein=bpy.data.materials.new('DiagnosticNeutralVein_NOT_ORIGINAL_MATERIAL')
source=(R/'upstream/scripts/build_lakeleaf_r04.py').read_text()
module=ast.parse(source)
functions=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['mesh','path']]
exec(compile(ast.Module(body=functions,type_ignores=[]),'<verified upstream mesh helpers>','exec'),globals())
section=source.split('# Shared thin shell,')[1].split('# Lake extends beyond shot.')[0]
section=section.split('\n',1)[1]
exec(compile(section,'<verified upstream leaf construction>','exec'),globals())
for o in collections['01_LeafBoat'].objects:o.location.z-=.16
repair=(R/'upstream/scripts/repair_leaf_veins_r05.py').read_text()
repair=repair[repair.index('def point'):repair.index("s['R05_changes']")]
exec(compile(repair,'<verified upstream R05 two-vein repair>','exec'),globals())
o=s.objects['LEAF_001_ThinConcaveShell'];bpy.context.view_layer.objects.active=o;o.select_set(True)
for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
o.select_set(False);bpy.context.view_layer.update()
assert len(s.objects)==20 and all(o.type=='MESH' for o in s.objects)

def geometry_hash(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(struct.pack('<3d',*(o.matrix_world@v.co)))
    for f in o.data.polygons:
        h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
    return h.hexdigest()

old=json.loads((R/'upstream/qa/r06/delivery-validation.json').read_text())['main_shell']
actual=geometry_hash(o)
vv=[o.matrix_world@v.co for v in o.data.vertices]
bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);bm.normal_update()
shape=dict(vertices=len(vv),faces=len(o.data.polygons),bounds=[[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)],
    volume=bm.calc_volume(signed=True),matrix_world=[list(r) for r in o.matrix_world]);bm.free()
shape['max_bound_difference']=max(abs(shape['bounds'][i][j]-old['bounds'][i][j]) for i in range(3) for j in range(2))
shape['volume_difference']=shape['volume']-old['volume']
e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();h=hashlib.sha256()
for v in m.vertices:h.update(struct.pack('<3d',*(o.matrix_world@v.co)))
for f in m.polygons:
    h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
shape['evaluated_world_hash']=h.hexdigest();e.to_mesh_clear()
out=R/'qa';out.mkdir(exist_ok=True)
proof=dict(scope='Replay of primary shell and 19 veins only; no original BLEND, forest, water, materials or scene history recovered.',
    main_shell_archived_world_hash=old['geometry_sha256'],main_shell_replayed_world_hash=actual,
    main_shell_hash_exact=actual==old['geometry_sha256'],shape=shape,mesh_count=20,original_blend_restored=False,source_accepted=False)
tree=BVHTree.FromPolygons(vv,[list(f.vertices) for f in o.data.polygons])
original_rays=json.loads((R/'upstream/qa/r06/shell-ray-probes.json').read_text());distances=[];thickness_diffs=[]
for row in original_rays['tests']:
    direction=Vector((0,0,-1));loc,normal,index,d=tree.ray_cast(Vector((row['x'],row['y'],8)),direction,20)
    assert loc is not None
    loc2,normal2,index2,d2=tree.ray_cast(loc+direction*1e-5,direction,20);assert loc2 is not None
    distances.extend([(loc-Vector(row['first_hit'])).length,(loc2-Vector(row['second_hit'])).length])
    thickness_diffs.append(abs(d2+1e-5-row['vertical_thickness']))
proof['archived_ray_grid_comparison']=dict(ray_count=len(original_rays['tests']),first_and_second_hit_position_error_max=max(distances),
    vertical_thickness_difference_max=max(thickness_diffs),scope='Only these archived ray samples; not a bound for every vertex or triangle.')
(out/'leaf-subset-replay-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
if not proof['main_shell_hash_exact']:
    assert '--allow-nonexact-subset' in sys.argv,'Keep failed proof; do not call the replay original geometry.'
    assert shape['max_bound_difference']==0 and abs(shape['volume_difference'])<1e-8 and max(distances)<2e-6
    proof['nonexact_subset_tests_only']=True
    (out/'leaf-subset-replay-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
models=R/'models';models.mkdir(exist_ok=True)
checkpoint=models/('leaf-only-r06-diagnostic-replay.blend' if proof['main_shell_hash_exact'] else 'leaf-only-r06-nonexact-diagnostic-replay.blend');assert not checkpoint.exists()
s['diagnostic_only']='20 leaf meshes replayed from source code. Not original BLEND recovery or full-scene candidate.'
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))
baseline={o.name:[v.co.copy() for v in o.data.vertices] for o in s.objects}
baseline_hashes={o.name:geometry_hash(o) for o in s.objects}
archived={r['id']:r for r in json.loads((R/'upstream/qa/r06/finite-vein-footprint-tests.json').read_text())['rows']}

def width(u):return 1.58*max(0,1-u*u)**.72*(1+.06*sin(3*pi*u))
def test(params):
    topology=[];footprints=[]
    for o in s.objects:
        inv=o.matrix_world.inverted()
        for v,co in zip(o.data.vertices,baseline[o.name]):v.co=inv@Vector(forward(o.matrix_world@co,params))
        o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update()
        row=dict(name=o.name,boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
            zero_area_faces=sum(f.calc_area()<1e-12 for f in bm.faces),volume=bm.calc_volume(signed=True),geometry_sha256=geometry_hash(o))
        bm.free();assert not row['boundary_edges'] and not row['nonmanifold_edges'] and not row['zero_area_faces'];topology.append(row)
        if params==Parameters():assert row['geometry_sha256']==baseline_hashes[o.name]
        if o.name.startswith(('LEAF_002','LEAF_003')):
            m=o.data;points=[o.matrix_world@v.co for v in m.vertices]
            probes=points+[(points[e.vertices[0]]+points[e.vertices[1]])*.5 for e in m.edges]+[sum((points[k] for k in f.vertices),Vector())/len(f.vertices) for f in m.polygons]
            vals=[];bad=0
            for v in probes:
                x,y,z=inverse(v,params);u=x/4.65;w=width(u);q=y/w if w else 1e9
                vals.append((u,q));bad+=abs(u)>=1 or abs(q)>=1
            assert bad==0
            row=dict(name=o.name,samples=len(probes),outside=bad,u_range=[min(x[0] for x in vals),max(x[0] for x in vals)],max_abs_v=max(abs(x[1]) for x in vals))
            if params==Parameters():
                original=archived[o.name];row['original_metric_max_error']=max(abs(row['u_range'][k]-original['u_range'][k]) for k in [0,1])
                row['original_metric_max_error']=max(row['original_metric_max_error'],abs(row['max_abs_v']-original['max_abs_v']))
                assert row['samples']==original['sample_count_vertices_edge_mids_face_centers'] and row['original_metric_max_error']<1e-9
            footprints.append(row)
    o=s.objects['LEAF_001_ThinConcaveShell'];m=o.data;vv=[o.matrix_world@v.co for v in m.vertices]
    tree=BVHTree.FromPolygons(vv,[list(f.vertices) for f in m.polygons]);thickness=[]
    for i in range(25):
        u=-.9+1.8*i/24
        for j in range(9):
            x,y,z=forward((4.65*u,width(u)*(-.85+1.7*j/8),8),params)
            direction=Vector((0,0,-1));loc,normal,index,d=tree.ray_cast(Vector((x,y,8)),direction,20);assert loc is not None
            loc2,normal2,index2,d2=tree.ray_cast(loc+direction*1e-5,direction,20);assert loc2 is not None and d2>0
            thickness.append(d2+1e-5)
    return dict(parameters=params.__dict__,topology=topology,footprints=footprints,vertical_shell_double_hits=len(thickness),
        vertical_shell_thickness_range=[min(thickness),max(thickness)],not_proven=['normal thickness','full-scene invariance','source fit','water contact','continuous collision'])

rows=[]
for params in [Parameters(),Parameters(belly_dz=.08),Parameters(belly_dz=-.08),Parameters(shoulder_fraction=.08)]:
    row=test(params);rows.append(row)
    (out/'leaf-subset-warp-tests.json').write_text(json.dumps(dict(scope=proof['scope'],rows=rows,source_accepted=False,production_blend_tested=False),indent=2)+'\n')
print('20-mesh subset tests completed; exact shell hash:',proof['main_shell_hash_exact'],'; no original file/full-scene/source acceptance claim.')
