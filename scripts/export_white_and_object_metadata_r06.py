import bpy,pathlib,json
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/lakeleaf-r06-material.blend'));rows={}
for o in bpy.context.scene.objects:
 if o.type=='MESH':rows[o.name]={'matrix_world':[list(r) for r in o.matrix_world],'location':list(o.location),'rotation_mode':o.rotation_mode,'rotation_euler_radians':list(o.rotation_euler),'scale':list(o.scale),'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials],'mesh_datablock':o.data.name,'mesh_users':o.data.users,'stable_id':o.get('stable_id',o.name),'inference':o.get('inference','unknown')}
(R/'qa/r06/object-transform-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(R/'models/lakeleaf-r06-white.blend'));bpy.ops.export_scene.gltf(filepath=str(R/'models/lakeleaf-r06-white.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_apply=False,export_texcoords=True,export_normals=True,export_materials='EXPORT')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models/lakeleaf-r06-white.glb'))
ref=json.loads((R/'qa/r06/material-mesh-inventory.json').read_text());actual={};cameras=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  v=[o.matrix_world@q.co for q in o.data.vertices];actual[o.name]={'bounds':[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)]}
 elif o.type=='CAMERA':cameras.append(o.name)
errors=[]
for name in set(ref)&set(actual):
 diff=max(abs(ref[name]['bounds'][i][j]-actual[name]['bounds'][i][j]) for i in range(3) for j in range(2))
 if diff>1e-4:errors.append({'id':name,'max_abs_bound_error':diff})
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/lakeleaf-r06-white-glb-reimport-check.blend'))
rep={'mesh_count':len(actual),'camera_count':len(cameras),'missing':sorted(set(ref)-set(actual)),'extra':sorted(set(actual)-set(ref)),'bounds_errors_gt_1e4':errors,'white_glb_bytes':(R/'models/lakeleaf-r06-white.glb').stat().st_size,'check_blend_bytes':(R/'models/lakeleaf-r06-white-glb-reimport-check.blend').stat().st_size,'raw_camera_limitation':'Same standard glTF off-axis-shift limitation as material GLB; use same camera sidecar for restoration. AREA/world/AgX also not fully portable.','source_accepted':False};(R/'qa/r06/white-glb-validation.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep)
