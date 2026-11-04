import bpy,pathlib,json
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];axis=Vector((0,-.85,-.3)).normalized()
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R02_{mode}.blend'))
 for o in bpy.data.objects:
  if o.name.startswith('UMBRELLA_rib_'):o.location-=axis*.001
 # Hypothetical coat silhouettes, not a recovered dress pattern or confirmed garment count.
 profile=[(-.08,.67),(-.20,.60),(-.33,.20),(-.24,.16),(-.18,.34),(-.18,-.56),(.18,-.56),(.18,.34),(.24,.16),(.33,.20),(.20,.60),(.08,.67),(0,.58)]
 for o in list(bpy.data.objects):
  if not o.name.startswith('GARMENT_finite_proxy_'):continue
  material=o.data.materials[0];N=len(profile);vs=[(x,y,z) for y in [-.035,.035] for x,z in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
  for j in range(N):fs.append((j,(j+1)%N,(j+1)%N+N,j+N))
  d=bpy.data.meshes.new(o.name+'_R03_silhouette');d.from_pydata(vs,[],fs);d.update();o.data=d;o.data.materials.append(material)
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R03_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R03_{mode}.glb'),export_format='GLB',export_cameras=True)
(P/'qa/R03-intent.json').write_text(json.dumps({'rib_shift_world':list(-axis*.001),'scope':'minimal shade contact candidate; must independently verify','garments':'five identical closed extruded sleeve silhouettes, count/identity still hypothetical, not fabric reconstruction','unchanged':'room scope/cameras/lighting/materials; no invented new enclosure'},indent=2))
