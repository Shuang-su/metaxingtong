import bpy,pathlib,json,hashlib,bmesh
from mathutils.bvhtree import BVHTree
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parent;R=D.parent/'forest-diagnostic-replay-20261104';report=json.load(open(D/'projected-surface-gap.json'));gap=next(x['minimum_vertical_gap'] for x in report['objects'] if x['object']=='LOG_left_fallen');delta=gap+.003;rows=[]
for mode in ['material','white']:
 src=R/('models/R14_anchor-diagnostic_'+mode+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.objects['LOG_left_fallen'];old=[list(o.matrix_world@v.co) for v in o.data.vertices];o.location.z-=delta;bpy.context.view_layer.update()
 terrain=bpy.data.objects['TERRAIN_finite_working_domain'];tree=lambda x:BVHTree.FromPolygons([x.matrix_world@v.co for v in x.data.vertices],[p.vertices[:] for p in x.data.polygons]);pairs=tree(o).overlap(tree(terrain));bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);vol=bm.calc_volume(signed=True);bm.free()
 if not pairs or bad or deg or vol<=0:raise RuntimeError('candidate geometry failed')
 new=[list(o.matrix_world@v.co) for v in o.data.vertices];o['inference']='R15 inferred existing fallen-log proxy, only rigid world-Z lowered by minimum vertical gap to finite terrain plus .003 working units. Not source position reconstruction or stable support/whole footprint proof.'
 dst=R/('models/R15_log-contact-diagnostic_'+mode+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dst));bpy.ops.export_scene.gltf(filepath=str(dst.with_suffix('.glb')),export_format='GLB',export_apply=True,export_cameras=True)
 rows.append({'mode':mode,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'world_z_lowering':delta,'vertices':len(old),'max_xy_change':max(abs(a[i]-b[i]) for a,b in zip(old,new) for i in [0,1]),'actual_z_delta_range':[min(b[2]-a[2] for a,b in zip(old,new)),max(b[2]-a[2] for a,b in zip(old,new))],'terrain_bvh_face_pairs':len(pairs),'nonmanifold':bad,'degenerate':deg,'signed_volume':vol})
(R/'qa/R15-log-contact.json').write_text(json.dumps({'role':'finite model structural-contact candidate, source FAILED; whole-scene exact original not restored','minimum_vertical_gap':gap,'numerical_margin':.003,'variants':rows},indent=2));print(rows)
