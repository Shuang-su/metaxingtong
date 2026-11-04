import bpy,json,pathlib,hashlib
P=pathlib.Path(__file__).resolve().parents[1];records={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R02_{mode}.blend'));o=bpy.data.objects['FLOOR_finite_slab'];mesh=o.data;uv=mesh.uv_layers.active or mesh.uv_layers.new(name='Floor_metric_proxy_UV')
 for face in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in face.loop_indices:
   co=o.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/2,co[axes[1]]/2)
 if mode=='material':
  m=o.data.materials[0];nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
  for fname,kind in [('stone_diffuse.png','color'),('stone_roughness.png','rough'),('stone_normal.png','normal')]:
   im=bpy.data.images.load(str(P/'textures'/fname),check_existing=True);im.colorspace_settings.name='sRGB' if kind=='color' else 'Non-Color';im.pack();im.filepath='//../textures/'+fname;n=nt.nodes.new('ShaderNodeTexImage');n.name='SYNTHETIC_'+kind;n.image=im;n.extension='REPEAT'
   if kind=='color':nt.links.new(n.outputs['Color'],bs.inputs['Base Color'])
   elif kind=='rough':nt.links.new(n.outputs['Color'],bs.inputs['Roughness'])
   else:
    nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;nt.links.new(n.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
  m['evidence']='Synthetic periodic stone proxy, not source texture recovery. Not accepted.'
 f=P/'models'/f'R03_{mode}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R03_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);records[mode]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),'camera_count':sum(o.type=='CAMERA' for o in bpy.data.objects),'geometry_change':'none; floor UV only','source_status':'FAILED'}
(P/'qa/R03-build-summary.json').write_text(json.dumps(records,indent=2))
