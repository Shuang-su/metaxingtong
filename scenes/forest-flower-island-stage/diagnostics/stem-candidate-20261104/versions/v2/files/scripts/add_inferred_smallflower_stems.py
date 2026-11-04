"""Structural diagnostic candidate on replay baseline, NOT restored original model.
Adds inferred stems only; never claims recovered source geometry or metric scale.
"""
import bpy,pathlib,math,json,hashlib,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path('forest-diagnostic-replay-20261104').resolve();reports=[]
for mode in ['material','white']:
 source=R/('models/R09_'+mode+'.blend');bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 bed=bpy.data.objects['ISLAND_moss_bedding_inferred'];bedtop=max((bed.matrix_world@v.co).z for v in bed.data.vertices)
 bt=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[p.vertices[:] for p in bed.data.polygons])
 patches=sorted([o for o in s.objects if o.name.startswith('SMALL_FLOWERS_patch_')],key=lambda o:o.name); rows=[]
 for patch in patches:
  original=[patch.matrix_world@v.co for v in patch.data.vertices];allv=[];allf=[]
  if len(original)%30:raise RuntimeError('unexpected topology')
  for h,start in enumerate(range(0,len(original),30)):
   vv=original[start:start+30];c=sum(vv,Vector())/30
   bottom=bedtop-.015;top=c.z+.012;radius=.009;N=8
   verts=[(c.x+radius*math.cos(i*math.tau/N),c.y+radius*math.sin(i*math.tau/N),z) for z in [bottom,top] for i in range(N)]
   faces=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[tuple(reversed(range(N))),tuple(N+i for i in range(N))]
   tree=BVHTree.FromPolygons(verts,faces);headfaces=[]
   for petal in range(5):
    off=petal*6;headfaces.extend(tuple(off+j for j in f) for f in [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)])
   head=BVHTree.FromPolygons(vv,headfaces);touchhead=bool(tree.overlap(head));touchbed=bool(tree.overlap(bt))
   rows.append(dict(patch=patch.name,head=h,centre=list(c),radius=radius,bottom_z=bottom,top_z=top,head_surface_intersection=touchhead,bed_surface_intersection=touchbed))
   if not(touchhead and touchbed):raise RuntimeError('connection check failed '+str(rows[-1]))
   off=len(allv);allv.extend(verts);allf.extend(tuple(j+off for j in f) for f in faces)
  me=bpy.data.meshes.new(patch.name+'_inferred_stems');me.from_pydata(allv,[],allf);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  if any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-12 for f in bm.faces):raise RuntimeError('topology failure')
  bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(patch.name+'_inferred_stems',me);s.collection.objects.link(ob);me.materials.append(bpy.data.materials['Leaf' if mode=='material' else 'WHITE_clay']);ob['inference']='Hidden finite stem geometry inferred to connect preexisting approximate flower heads to inferred bedding; no source instance recovery or measured radius/length claim';ob['diagnostic_baseline']='script replay, not original blend byte recovery'
 out=R/('models/R10_support-diagnostic_'+mode+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out));bpy.ops.export_scene.gltf(filepath=str(out.with_suffix('.glb')),export_format='GLB',export_apply=True,export_cameras=True)
 reports.append(dict(mode=mode,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),new_meshes=len(patches),stems=len(rows),rows=rows))
(R/'qa/R10-inferred-stem-contact.json').write_text(json.dumps({'role':'inferred structural completion on replay candidate; original model and source acceptance still pending','reports':reports},indent=2));print('STEMS',[(x['mode'],x['stems']) for x in reports])
