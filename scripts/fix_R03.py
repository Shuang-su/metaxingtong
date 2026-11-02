import bpy,bmesh,json,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[-2:]))
D=Path(__file__).resolve().parents[1];records={}
for mode in['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R02_{mode}.blend'));s=bpy.context.scene;s.render.threads=2;s.cycles.use_denoising=False
 weld=[]
 for name in['L_front_NOTCHED','R_front_NOTCHED']:
  o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);before=(len(bm.verts),sum(e.is_boundary for e in bm.edges));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));weld.append({'name':name,'before_vertices_boundary':before,'after_vertices':len(bm.verts),'after_boundary':sum(e.is_boundary for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)});bm.to_mesh(o.data);bm.free()
 # Explicit engineering hypothesis only: shared rigid vertical move rim to proxy floor.
 deps=bpy.context.evaluated_depsgraph_get();umb=[o for o in s.objects if o.type=='MESH' and o.name.startswith('UMBRELLA')];oldmin=min((o.matrix_world@v.co).z for o in umb for v in o.data.vertices);delta=.012-oldmin;bpy.data.objects['UMBRELLA_RIG'].location.z+=delta;bpy.context.view_layer.update()
 bpy.data.objects['UMBRELLA_RIG']['R03_ground_hypothesis']='Rigid downshift lowest rim to proxy z=.012; unseen actual source ground/support unconfirmed'
 audit=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in s.objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);bm.transform(o.matrix_world);boundary=sum(e.is_boundary for e in bm.edges);vol=bm.calc_volume(signed=True);audit.append({'name':o.name,'evaluated_boundary_edges':boundary,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_world':vol if boundary==0 else None,'volume_valid_only_closed':boundary==0,'min_z':min(v.co.z for v in bm.verts)});bm.free();ev.to_mesh_clear()
 # Dense top cap footprint rays through upper band (actual faces, not AABB).
 band=bpy.data.objects['BAND_finite_arc'];bm=bmesh.new();bm.from_mesh(band.data);bm.transform(band.matrix_world);tree=BVHTree.FromBMesh(bm);caps=[]
 for name in['L_COLUMN_cap','R_COLUMN_cap']:
  o=bpy.data.objects[name];hits=0;total=0;pts=[]
  for ix in range(-8,9):
   for iy in range(-8,9):
    dx,dy=ix*.055,iy*.055
    if dx*dx+dy*dy>.48**2:continue
    total+=1;hit=tree.ray_cast(Vector((o.location.x+dx,o.location.y+dy,3.45)),Vector((0,0,1)),.55);ok=hit[0] is not None;hits+=ok;pts.append({'dx':dx,'dy':dy,'band_hit':ok,'hit_z':hit[0].z if ok else None})
  caps.append({'name':name,'samples':total,'band_intersections':hits,'points':pts,'interpretation':'Partial sampled footprint overlap only; no load capacity/source construction proof'})
 bm.free()
 records[mode]={'weld':weld,'umbrella_old_min_z':oldmin,'rigid_delta_z':delta,'umbrella_new_min_z':min(x['min_z'] for x in audit if x['name'].startswith('UMBRELLA')),'evaluated_meshes':audit,'column_band_footprint':caps,'limitations':'Leaves intentional open surfaces. No global solid-union/watertight claim. Source camera/shape still failed.'}
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R03_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R03_{mode}.glb'),export_format='GLB',export_cameras=True,export_lights=False)
(D/'models/R03-technical-audit.json').write_text(json.dumps(records,indent=2));print('R03_SAVED')
