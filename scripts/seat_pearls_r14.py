import bpy,pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];records={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap():
 return {o.name:{'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices] if o.type=='MESH' else None,'uv':[[list(x.uv) for x in l.data] for l in o.data.uv_layers] if o.type=='MESH' else None,'materials':[s.material.name if s.material else None for s in o.material_slots]} for o in bpy.context.scene.objects}
for mode in ['material','white']:
 src=P/'models'/f'R13_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(src));before=snap();pearls=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('NECKLACE_pearl_proxy_')];assert len(pearls)==32
 top=max((bpy.data.objects['TABLE_top'].matrix_world@v.co).z for v in bpy.data.objects['TABLE_top'].data.vertices);bottom=min((o.matrix_world@v.co).z for o in pearls for v in o.data.vertices);dz=top-bottom;changes=[]
 for o in pearls:
  old=list(o.location);o.location.z+=dz;changes.append({'name':o.name,'old':old,'new':list(o.location)})
 bpy.context.view_layer.update();after=snap();names={o.name for o in pearls};assert all(before[n]==after[n] for n in before if n not in names)
 for n in names:assert all(before[n][k]==after[n][k] for k in ['vertices','uv','materials'])
 deps=[]
 for im in bpy.data.images:
  if im.source=='FILE':deps.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file),'resolved':bpy.path.abspath(im.filepath)})
 cams={o.name:{'matrix_world':[list(r)for r in o.matrix_world],'type':o.data.type,'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'sensor_fit':o.data.sensor_fit,'ortho_scale':o.data.ortho_scale,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end} for o in bpy.context.scene.objects if o.type=='CAMERA'}
 side={'cameras':cams,'active_camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None,'resolution':[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y,bpy.context.scene.render.resolution_percentage],'pixel_aspect':[bpy.context.scene.render.pixel_aspect_x,bpy.context.scene.render.pixel_aspect_y],'note':'GLB may not preserve sensor fit/aspect in viewers. Restore from blend or this explicit sidecar; no source registration.'};(P/'qa'/f'R14_{mode}_camera_restore.json').write_text(json.dumps(side,indent=2))
 dst=P/'models'/f'R14_{mode}.blend';assert not dst.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dst));glb=P/'models'/f'R14_{mode}.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_cameras=True,export_extras=True)
 records[mode]={'input':str(src.relative_to(P)),'input_sha256':sha(src),'blend':str(dst.relative_to(P)),'blend_sha256':sha(dst),'glb':str(glb.relative_to(P)),'glb_sha256':sha(glb),'mesh_count':sum(o.type=='MESH'for o in bpy.context.scene.objects),'changed_meshes':32,'unchanged_meshes':204,'dz':dz,'changes':changes,'other_objects_unchanged':True,'mesh_local_vertices_uv_material_bindings_unchanged':True,'dependencies':deps,'camera_count':len(cams)}
(P/'qa/R14-build-record.json').write_text(json.dumps(records,indent=2))
