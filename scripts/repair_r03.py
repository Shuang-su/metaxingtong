import bpy,bmesh,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r02.blend'))
s=bpy.context.scene;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_denoising=False
rows=[]
for o in s.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);before=sum(e.is_boundary for e in bm.edges)
 if before:
  # Welding coincident end rings closes the deliberately closed cloud outlines.
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  ed=[e for e in bm.edges if e.is_boundary]
  if ed:bmesh.ops.holes_fill(bm,edges=ed,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 after=sum(not e.is_manifold for e in bm.edges);rows.append({'object':o.name,'boundary_before':before,'nonmanifold_after':after,'signed_volume':bm.calc_volume(signed=True)})
 bm.to_mesh(o.data);bm.free();o.data.update()
(P/'qa/r03-cap-repair.json').write_text(json.dumps(rows,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r03.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r03.glb'),export_format='GLB',export_cameras=True,export_extras=True)
d=json.loads((P/'models/roof-r02-recovery.json').read_text());d['schema']=2;d['render'].update({'percentage':100,'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y],'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma});d['active_camera']=s.camera.name;d['source_blend']='roof-r03.blend';d['glb']='roof-r03.glb'
for r in d['objects']:
 if r['type']=='CAMERA':
  c=bpy.data.objects[r['name']].data;r['camera']['sensor_fit']=c.sensor_fit;r['camera']['sensor_height']=c.sensor_height;r['camera']['shift_x']=c.shift_x;r['camera']['shift_y']=c.shift_y;r['camera']['type']=c.type
 if r['type']=='LIGHT':r['light']['shape']='DISK'
(P/'models/roof-r03-recovery.json').write_text(json.dumps(d,indent=2))
w=bpy.data.materials.new('White diagnostic R03');w.use_nodes=True;w.diffuse_color=(.66,.66,.66,1);b=w.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.7
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'models/roof-r03-white.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'models/roof-r03-white.glb'),export_format='GLB',export_cameras=True,export_extras=True)
