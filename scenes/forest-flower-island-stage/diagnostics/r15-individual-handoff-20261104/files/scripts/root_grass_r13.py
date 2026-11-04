import bpy,pathlib,json,hashlib,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];j=json.load(open(R/'qa/grass-base-check.json'));selected=[x for x in j['leaves'] if x['bed_below'] and x['vertical_gap']>.0001 and not x['surface_intersects_bed']];reports=[]
for mode in ['material','white']:
 src=R/('models/R12_support-diagnostic_'+mode+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));ob=bpy.data.objects['ISLAND_turf_blades_procedural'];bed=bpy.data.objects['ISLAND_moss_bedding_inferred'];bt=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[p.vertices[:] for p in bed.data.polygons]);original=[tuple(v.co) for v in ob.data.vertices];changed=[]
 for row in selected:
  index=row['base_vertex'];p=ob.matrix_world@ob.data.vertices[index].co
  if (p-Vector(row['original_world_base'])).length>1e-6:raise RuntimeError('source baseline mismatch')
  dz=row['bed_z']-.003-p.z;ob.data.vertices[index].co+=ob.matrix_world.inverted().to_3x3()@Vector((0,0,dz));changed.append(index)
 ob.data.update();actual=[i for i,v in enumerate(ob.data.vertices) if tuple(v.co)!=original[i]]
 if actual!=sorted(changed):raise RuntimeError('unexpected changed vertices')
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];groups=[[] for _ in range(len(vs)//6)]
 for face in ob.data.polygons:
  g=face.vertices[0]//6
  if any(i//6!=g for i in face.vertices):raise RuntimeError('cross leaf')
  groups[g].append(tuple(i-g*6 for i in face.vertices))
 contacts=[]
 for row in selected:
  g=row['leaf'];tree=BVHTree.FromPolygons(vs[g*6:g*6+6],groups[g]);hit=bool(tree.overlap(bt));contacts.append({'leaf':g,'base_vertex':row['base_vertex'],'old_world_base':row['original_world_base'],'new_world_base':list(vs[row['base_vertex']]),'bed_surface_intersection':hit})
  if not hit:raise RuntimeError('new grass contact failed '+str(g))
 bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces);volume=bm.calc_volume(signed=True);bm.free()
 if bad or deg or volume<=0:raise RuntimeError('grass topology changed adversely')
 ob['inference']='Procedural grass family, individual blades not source-recovered. R13 extends only 3627 verified gapped basal vertices into inferred bedding by .003 working unit; upper five vertices of each blade unchanged. Eighteen missing basal terrain rays and two other edge cases remain unmodified.'
 dest=R/('models/R13_root-diagnostic_'+mode+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.export_scene.gltf(filepath=str(dest.with_suffix('.glb')),export_format='GLB',export_apply=True,export_cameras=True);reports.append({'mode':mode,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed_vertices':actual,'contacts':contacts,'nonmanifold_edges':bad,'degenerate_faces':deg,'signed_volume':volume})
(R/'qa/R13-grass-root-check.json').write_text(json.dumps({'role':'inferred basal geometry structural completion on replay baseline, not observed root geometry or source acceptance','variants':reports},indent=2));print('R13',[(x['mode'],len(x['contacts'])) for x in reports])
