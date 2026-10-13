import bpy,bmesh,json,math
from pathlib import Path
root=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit');out=root/'candidate_b';out.mkdir(exist_ok=True)
b=bpy.data.objects['Bed • observed endboard, consistent width'];bm=bmesh.new();bm.from_mesh(b.data)
# Densify only long upper contour edges before warping; avoid sliver-producing global subdivision.
edges=[e for e in bm.edges if min(v.co.z for v in e.verts)>.11 and abs(e.verts[0].co.y-e.verts[1].co.y)>.25]
bmesh.ops.subdivide_edges(bm,edges=edges,cuts=63,use_grid_fill=False)
changed=0
for v in bm.verts:
 y,z=v.co.y,v.co.z
 if z>.11:
  u=min(1,abs(y)/.91);t=max(0,min(1,(abs(y)-.69)/.22));shoulder=.105*(1-math.sqrt(max(0,1-t*t)));delta=.016*(1-u*u)-shoulder
  v.co.z+=min(1,(z-.11)/.15)*delta;changed+=1
bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bm.normal_update()
qa={'candidate':'B rounded-shoulder hypothesis','vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True),'changed_vertices':changed,'long_upper_edges_densified':len(edges),'subdivision_cuts':63,'parameters_local_model_units':{'half_width':.91,'warp_start_z':.11,'center_arch_delta':.016,'shoulder_start_abs_y':.69,'shoulder_horizontal_radius':.22,'shoulder_vertical_drop':.105},'parameters_status':'inferred, not measured or camera-calibrated','scope':'Only original bed endboard upper silhouette changes; slots below z=.1035, width, thickness, placement and all other scene objects preserved.'}
bm.to_mesh(b.data);bm.free();b.data.update();b['candidate_status']='B continuous rounded shoulder; local hypothesis, source fidelity not accepted'
s=bpy.context.scene;s.cycles.use_denoising=False
for vl in s.view_layers:vl.cycles.use_denoising=False
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hospital_endboard_shape_B.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'hospital_endboard_shape_B.glb'),export_format='GLB',use_selection=False);(out/'candidate_b_geometry_qa.json').write_text(json.dumps(qa,indent=2))
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=16
for tag,name in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/f'{tag}_B_legacy_camera_1920.png');bpy.ops.render.render(write_still=True)
