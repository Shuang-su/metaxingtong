import bpy,bmesh,math,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R05_{mode}.blend'));s=bpy.context.scene
 mat=bpy.data.objects['BAR_top'].data.materials[0]
 for n in ['BAR_top','BAR_waterfall_end_-1','BAR_waterfall_end_1']:
  bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 # Continuous constant-thickness waterfall U section, two rounded upper bends.
 L=2.2;R=5.3;z=1.31;r=.32;ri=.16
 poly=[(L,0),(L,z)]
 poly += [(L+r+r*math.cos(math.pi-i*math.pi/2/16),z+r*math.sin(math.pi-i*math.pi/2/16)) for i in range(1,17)]
 poly += [(R-r,z+r)]
 poly += [(R-r+r*math.cos(math.pi/2-i*math.pi/2/16),z+r*math.sin(math.pi/2-i*math.pi/2/16)) for i in range(1,17)]
 poly += [(R,0),(R-.16,0),(R-.16,z)]
 poly += [(R-r+ri*math.cos(i*math.pi/2/16),z+ri*math.sin(i*math.pi/2/16)) for i in range(1,17)]
 poly += [(L+r,z+ri)]
 poly += [(L+r+ri*math.cos(math.pi/2+i*math.pi/2/16),z+ri*math.sin(math.pi/2+i*math.pi/2/16)) for i in range(1,17)]
 poly += [(L+.16,0)]
 N=len(poly);v=[(x,y,z) for y in [2.25,3.12] for x,z in poly];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]
 for i in range(N):j=(i+1)%N;f.append((i,j,N+j,N+i))
 me=bpy.data.meshes.new('continuous_U_profile');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new('BAR_continuous_waterfall_U',me);s.collection.objects.link(o);me.materials.append(mat);o['observation_status']='Continuous rounded silhouette supported by source; radii/thickness/depth/right termination inferred';o['object_role']='BAR'
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 # Smooth curved strips only, keep planar front/back section sharply defined.
 for p in me.polygons:
  if abs(p.normal.y)<.5:p.use_smooth=True
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R06_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R06_{mode}.glb'),export_format='GLB',export_apply=True)
(D/'qa/R06-changes.json').write_text(json.dumps({'change':'Replace three separate bar slabs with one physically continuous U-profile extrusion; outer bend radius 0.32 and thickness 0.16 are working hypotheses based on visible rounded silhouette, not measured.','unchanged':'All other geometry, materials, fixed lighting and R05 source cameras.','remaining':'Section depth, radius, right termination and source alignment remain unaccepted. R05 fit anchors refer prior approximate upper-left landmark; final evaluation updates this landmark, no refit.'},indent=2))
