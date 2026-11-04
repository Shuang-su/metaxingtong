import bpy,pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];audit={};remove=['DEVICE_front_bezel_bottom','DEVICE_front_bezel_left','DEVICE_front_bezel_right','DEVICE_front_bezel_top','DEVICE_front_divider','DEVICE_horizontal_tuning_region','DEVICE_left_grille_region']
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R10_{mode}.blend'))
 for n in remove:
  o=bpy.data.objects[n];bpy.data.objects.remove(o,do_unlink=True)
 o=bpy.data.objects['COSMETIC_case_body'];uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap');changes=[]
 if mode=='material':
  m=bpy.data.materials.new('DEVICE_front_diagram_not_scan');m.use_nodes=True;nodes=m.node_tree.nodes;p=nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=.15;p.inputs['Roughness'].default_value=.6;t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'textures/R11_device_front_proxy.png'));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);o.data.materials.append(m);mi=len(o.data.materials)-1
 else:mi=0
 for f in o.data.polygons:
  if f.normal.y<-.9:
   for li in f.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;old=list(uv.data[li].uv);uv.data[li].uv=((v.x+.29)/.58,(v.z+.18)/.36);changes.append({'loop':li,'old_uv':old,'new_uv':list(uv.data[li].uv)})
   f.material_index=mi
 o['R11_surface_scope']='Seven intersecting R10 panel meshes removed. Diagrammatic front appearance uses existing exact body surface, no overlay/coplanar duplicate faces or new recess geometry. Old bottle-body intersections and tabletop gap remain.'
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R11_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R11_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'removed_failed_new_panels':remove,'front_uv_changes':changes,'retained_new_controls':'two knobs and three top buttons','scope':'Conditional device appearance, not source geometry acceptance. Old231 mesh positions/vertices unchanged; counts236mesh/8camera.','model_sha256':hashlib.sha256((P/'models'/f'R11_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R11-device-surface-applied.json').write_text(json.dumps(audit,indent=2))
