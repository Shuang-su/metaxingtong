import bpy,pathlib,json,hashlib,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];out=[]
for mode in ['material','white']:
 src=R/('models/R13_root-diagnostic_'+mode+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));ob=bpy.data.objects['TREE_background_03'];terrain=bpy.data.objects['TERRAIN_finite_working_domain'];bt=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[p.vertices[:] for p in terrain.data.polygons]);old=[tuple(v.co) for v in ob.data.vertices];samples=[]
 if len(old)!=48:raise RuntimeError('unexpected original tube topology')
 for i in range(12):
  p=ob.matrix_world@ob.data.vertices[i].co;hit,norm,index,d=bt.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),200)
  if hit is None:raise RuntimeError('no terrain below base ring')
  samples.append({'index':i,'old_world':list(p),'terrain_z':hit.z,'gap':p.z-hit.z})
 if any(x['gap']<=0 for x in samples):raise RuntimeError('not uniformly gapped as hypothesized')
 lower=max(x['gap'] for x in samples)+.005
 for i in range(12):ob.data.vertices[i].co+=ob.matrix_world.inverted().to_3x3()@Vector((0,0,-lower))
 ob.data.update();changed=[i for i,v in enumerate(ob.data.vertices) if tuple(v.co)!=old[i]]
 if changed!=list(range(12)):raise RuntimeError('changed more than base ring')
 world=[ob.matrix_world@v.co for v in ob.data.vertices];tt=BVHTree.FromPolygons(world,[p.vertices[:] for p in ob.data.polygons]);pairs=tt.overlap(bt)
 if not pairs:raise RuntimeError('no actual terrain surface overlap')
 for row in samples:
  p=world[row['index']];hit,n,idx,d=bt.ray_cast(p,Vector((0,0,-1)),2)
  row.update(new_world=list(p),below_top=p.z<row['terrain_z'],below_ray_exit=hit.z if hit is not None else None)
  if not row['below_top'] or hit is None or hit.z>=p.z:raise RuntimeError('base not inside finite terrain vertical interval')
 bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);vol=bm.calc_volume(signed=True);bm.free()
 if bad or deg or vol<=0:raise RuntimeError('topology failed')
 ob['inference']='Observed tree-family proxy, individual trunk placement not calibrated. R14 only lowers first12 base-ring vertices by measured model gap plus .005 working unit into inferred finite terrain; upper36 vertices unchanged. Not source root reconstruction.'
 dest=R/('models/R14_anchor-diagnostic_'+mode+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.export_scene.gltf(filepath=str(dest.with_suffix('.glb')),export_format='GLB',export_apply=True,export_cameras=True);out.append({'mode':mode,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'base_ring_lowered_by':lower,'changed_vertices':changed,'terrain_surface_intersection_pairs':len(pairs),'samples':samples,'nonmanifold':bad,'degenerate':deg,'signed_volume':vol})
(R/'qa/R14-tree-base-contact.json').write_text(json.dumps({'role':'inferred basal structural completion on replay baseline, no source calibration','variants':out},indent=2));print('R14',[(x['mode'],x['base_ring_lowered_by'],x['terrain_surface_intersection_pairs']) for x in out])
