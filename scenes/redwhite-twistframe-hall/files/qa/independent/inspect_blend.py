import bpy,bmesh,json,sys,math,hashlib,os,struct
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]; src=Path(args[0]); out=Path(args[1]); mode=args[2]
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=1
if mode=='glb':
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(src))
scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get(); records=[]
for o in scene.objects:
 r={'name':o.name,'type':o.type,'location':list(o.location),'collections':[c.name for c in o.users_collection],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
 if o.type in ['MESH','CURVE']:
  eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);bm.transform(o.matrix_world)
  bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
  h=hashlib.sha256()
  for v in bm.verts:
   h.update(struct.pack('<3d',*v.co))
  for f in bm.faces:
   h.update(struct.pack('<I',len(f.verts)));h.update(struct.pack('<'+'I'*len(f.verts),*(v.index for v in f.verts)))
  r['evaluated_world_geometry_sha256']=h.hexdigest()
  r.update(vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),wire_edges=sum(e.is_wire for e in bm.edges),degenerate_faces=sum(f.calc_area()<1e-12 for f in bm.faces),signed_volume=bm.calc_volume(signed=True),uv_layers=[l.name for l in me.uv_layers],materials=[m.name if m else None for m in me.materials],bounds=[[min((v.co[i] for v in bm.verts),default=0) for i in range(3)],[max((v.co[i] for v in bm.verts),default=0) for i in range(3)]])
  # glTF attribute seams are not geometric holes: measure after positional welding.
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  r.update(welded_vertices=len(bm.verts),welded_boundary_edges=sum(e.is_boundary for e in bm.edges),welded_nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),welded_degenerate_faces=sum(f.calc_area()<1e-12 for f in bm.faces),welded_signed_volume=bm.calc_volume(signed=True))
  bm.free();eo.to_mesh_clear()
 elif o.type=='CAMERA':r.update(matrix_world=[list(row) for row in o.matrix_world],lens=o.data.lens,sensor_width=o.data.sensor_width,angle_x=o.data.angle_x,angle_y=o.data.angle_y,projection=o.data.type,ortho_scale=o.data.ortho_scale)
 records.append(r)
res={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bytes':src.stat().st_size,'mode':mode,'blender_version':bpy.app.version_string,'scene_render_resolution':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage],'pixel_aspect':[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],'scene_camera':scene.camera.name if scene.camera else None,'objects':records,'materials':[{'name':m.name,'nodes':m.use_nodes,'images':[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []} for m in bpy.data.materials],'images':[{'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file),'source':im.source,'size':list(im.size)} for im in bpy.data.images],'view_layers':[{'name':v.name,'enabled':v.use,'material_override':v.material_override.name if v.material_override else None} for v in scene.view_layers]}
out.write_text(json.dumps(res,ensure_ascii=False,indent=2));print('QA_OUT',out,'OBJECTS',len(records),'MESHES',sum('vertices' in r for r in records))
