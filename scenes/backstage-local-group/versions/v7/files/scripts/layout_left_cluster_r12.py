import bpy,pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];dx=-.27252954041957855;dy=.02242484486103058;records={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R11_{mode}.blend'));changes=[]
 for i in range(9):
  for n in [f'COSMETIC_bottle_proxy_{i}',f'COSMETIC_cap_proxy_{i}']:
   o=bpy.data.objects[n];old=list(o.location);o.location.x+=dx;o.location.y+=dy;changes.append({'object':n,'old_location':old,'new_location':list(o.location)});o['R12_placement_limit']='Unified conditional left-cluster shift to remove known proxy intersections; source009 only supplies weak left-of-device grouping, not calibrated position or instance identity. Relative arrangement and Z preserved.'
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R12_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R12_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);records[mode]={'translation':[dx,dy,0],'changes':changes,'unchanged_other_meshes_intent':218,'camera_count':8,'scope':'236 meshes; no new instances, no removal; six bottle/table gaps and other unrelated errors remain. Not source geometry acceptance.','sha256':hashlib.sha256((P/'models'/f'R12_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R12-cluster-applied.json').write_text(json.dumps(records,indent=2))
