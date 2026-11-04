import bpy,pathlib,json,math
P=pathlib.Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R03_{mode}.blend'))
 for i,cx in enumerate([1,1.45,1.9,2.35,2.8]):
  for name in [f'GARMENT_finite_proxy_{i}',f'HANGER_{i}',f'HANGER_{i}b']:
   o=bpy.data.objects[name];M=o.matrix_world.copy();I=M.inverted()
   for v in o.data.vertices:
    w=M@v.co;w.x=cx+(w.x-cx)*.6;v.co=I@w
  # Explicitly inferred finite ring, not claimed as visible source hook or load-bearing design.
  bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=(cx,2.8,1.9),rotation=(0,math.pi/2,0),major_radius=.026,minor_radius=.009)
  o=bpy.context.object;o.name=f'HANGER_ring_inferred_{i}';o.data.materials.append(bpy.data.materials['DARK_metal' if mode=='material' else 'WHITE_clay'])
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R04_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R04_{mode}.glb'),export_format='GLB',export_cameras=True)
(P/'qa/R04-intent.json').write_text(json.dumps({'scope':'local proxy technical collision repair, not source proportions or room acceptance','garment_and_hanger_x_scale_about_each_center':.6,'ring':'five inferred closed torus connectors, R03 actual hanger-bar gaps ~.005086; contact requires independent verification','source_count_identity_layout':'unverified; no source pose fit'},indent=2))
