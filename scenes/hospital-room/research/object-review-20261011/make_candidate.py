import bpy,bmesh,json,math,os
from pathlib import Path
root=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit'); out=root/'candidate';out.mkdir(exist_ok=True)
s=bpy.context.scene;b=bpy.data.objects['Bed • observed endboard, consistent width']
# Preserve aperture vertices (all at local z <= .1035), thickness, placement, width.
bm=bmesh.new();bm.from_mesh(b.data)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.subdivide_edges(bm,edges=[e for e in bm.edges if max(v.co.z for v in e.verts)>.11],cuts=12,use_grid_fill=True)
changed=0
for v in bm.verts:
 y,z=v.co.y,v.co.z
 if z>.11:
  u=min(1,abs(y)/.91);weight=min(1,(z-.11)/(.26-.11));v.co.z += weight*(.02*(1-u*u)-.11*u**12);changed+=1
bm.normal_update();bm.to_mesh(b.data);bm.free();b.data.update()
b['candidate_status']='Shape hypothesis from native F/G; not camera-calibrated or source accepted'
b['changed_scope']='Upper silhouette only; slots, placement, thickness and width preserved'
qa=bmesh.new();qa.from_mesh(b.data)
report={'changed_vertices':changed,'vertices':len(qa.verts),'faces':len(qa.faces),'nonmanifold_edges':sum(not e.is_manifold for e in qa.edges),'boundary_edges':sum(e.is_boundary for e in qa.edges),'volume':qa.calc_volume(signed=True),'hypothesis_parameters_local':{'top_center_delta':.02,'shoulder_drop':.11,'shoulder_exponent':12,'warp_start_z':.11},'scope':'Only endboard geometry changed. Cameras, other objects, materials, lighting and visibility untouched. Parameters are inferred model units, not measured.','source_acceptance':False};qa.free()
(out/'candidate_geometry_qa.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out/'hospital_endboard_shape_candidate.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'hospital_endboard_shape_candidate.glb'),export_format='GLB',use_selection=False)
# Native-resolution render using unchanged legacy cameras. This is conditional diagnosis.
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=12;s.cycles.use_denoising=True
for tag,name in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/f'{tag}_candidate_legacy_camera_1920.png');bpy.ops.render.render(write_still=True)
