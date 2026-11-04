import bpy,pathlib,json,hashlib,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];out=[]
for mode in ['material','white']:
 src=R/('models/R11_support-diagnostic_'+mode+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));bed=bpy.data.objects['ISLAND_moss_bedding_inferred'];bt=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[p.vertices[:] for p in bed.data.polygons]);rows=[]
 for ob in bpy.context.scene.objects:
  if not ob.name.endswith('_inferred_stems'):continue
  patch=bpy.data.objects[ob.name[:-len('_inferred_stems')]];vv=[patch.matrix_world@v.co for v in patch.data.vertices]
  for idx,start in enumerate(range(0,len(vv),30)):
   headverts=vv[start:start+30];c=sum(headverts,Vector())/30
   for k in range(8,16):
    v=ob.data.vertices[idx*16+k];v.co.x=c.x+(v.co.x-c.x)/3;v.co.y=c.y+(v.co.y-c.y)/3;v.co.z=c.z-.004
   fstem=[tuple(v-idx*16 for v in f.vertices) for f in ob.data.polygons if all(idx*16<=v<(idx+1)*16 for v in f.vertices)];sv=[ob.matrix_world@v.co for v in ob.data.vertices[idx*16:(idx+1)*16]];st=BVHTree.FromPolygons(sv,fstem)
   hf=[tuple(v-start for v in f.vertices) for f in patch.data.polygons if all(start<=v<start+30 for v in f.vertices)];ht=BVHTree.FromPolygons(headverts,hf)
   hhit=bool(st.overlap(ht));bhit=bool(st.overlap(bt));probes=[Vector((c.x,c.y,c.z-.004+.00001))]+[v+Vector((0,0,.00001)) for v in sv[8:]];clear=sum(ht.ray_cast(p,Vector((0,0,1)),.1)[0] is None for p in probes)
   rows.append(dict(patch=patch.name,head=idx,head_intersection=hhit,bed_intersection=bhit,cap_probes=9,upward_uncovered=clear))
   if not hhit or not bhit or clear:raise RuntimeError('R12 support/cap check failed '+str(rows[-1]))
  ob.data.update();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free();ob['inference']='Inferred hidden tapered stem; radius .009 at bedding to .003 at top, top .004 below head centre, working units not measured source. Structural overlap/cap-probe candidate only.'
 dest=R/('models/R12_support-diagnostic_'+mode+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(dest));bpy.ops.export_scene.gltf(filepath=str(dest.with_suffix('.glb')),export_format='GLB',export_apply=True,export_cameras=True);out.append(dict(mode=mode,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),checks=rows))
(R/'qa/R12-contact-and-cap-check.json').write_text(json.dumps({'role':'actual saved geometry new stem top refinement, inferred structural candidate, not source acceptance','variants':out},indent=2));print('R12',[(x['mode'],len(x['checks'])) for x in out])
