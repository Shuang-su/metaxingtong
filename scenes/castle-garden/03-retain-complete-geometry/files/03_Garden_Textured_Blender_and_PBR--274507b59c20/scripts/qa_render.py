import bpy,bmesh,json,os,struct,hashlib
R='/workspace/scratch/fa58bfcf0425/castle_garden_fullscene';D=R+'/delivery'
if not os.path.exists(R+'/RENDER_APPROVED'):raise SystemExit('Awaiting independent geometry review')
bpy.ops.wm.open_mainfile(filepath=D+'/models/Garden_Complete_Textured.blend');s=bpy.context.scene
# Unify material-white geometry, then validate native closed structural elements.
def stats():
 a=[]
 for o in s.objects:
  if o.type!='MESH':continue
  b=bmesh.new();b.from_mesh(o.data);o.data.calc_loop_triangles()
  a.append(dict(name=o.name,plant=o.get('surface_class')=='天然双面薄叶/花瓣',v=len(b.verts),tri=len(o.data.loop_triangles),boundary=sum(e.is_boundary for e in b.edges),nonmanifold=sum(not e.is_manifold for e in b.edges),degenerate=sum(f.calc_area()<1e-10 for f in b.faces),volume=b.calc_volume(signed=True)));b.free()
 return a
native=stats(); native_points=sorted(set(tuple(round(float(v),4) for v in o.matrix_world@x.co) for o in s.objects if o.type=='MESH' for x in o.data.vertices));
json.dump(stats(),open(D+'/qa/完成模型几何审计.json','w'),ensure_ascii=False,indent=2)
s.render.resolution_x=1188;s.render.resolution_y=668;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_denoising=False
for tag in ['A','B']:
 s.camera=bpy.data.objects['MATCH_'+tag+('_00h25m11s' if tag=='A' else '_00h21m59s')];s.render.filepath=D+'/views/材质_源匹配_'+tag+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=960;s.render.resolution_y=640
for cam in ['02_左前','05_右后']:
 s.camera=bpy.data.objects[cam];s.render.filepath=D+'/views/材质_'+cam+'.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=1188;s.render.resolution_y=668
w=bpy.data.materials.new('统一中性白模');w.use_nodes=True;w.diffuse_color=(.72,.72,.72,1);w.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.72,.72,.72,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=D+'/models/Garden_Complete_White.blend',compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=D+'/models/Garden_Complete_White.glb',export_format='GLB',use_selection=True,export_extras=True)
for tag in ['A','B']:
 s.camera=bpy.data.objects['MATCH_'+tag+('_00h25m11s' if tag=='A' else '_00h21m59s')];s.render.filepath=D+'/views/白模_源匹配_'+tag+'.png';bpy.ops.render.render(write_still=True)
# True GLB reimport in empty scene.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=D+'/models/Garden_Complete_Textured.glb')
imp=stats(); used_images={n.image for o in s.objects if o.type=='MESH' for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}; imported_images=[{'name':i.name,'size':list(i.size),'pixels':len(i.pixels),'has_data':i.has_data} for i in used_images];blob=open(D+'/models/Garden_Complete_Textured.glb','rb').read();ln=struct.unpack_from('<I',blob,12)[0];g=json.loads(blob[20:20+ln]);report={'native_objects':len(native),'native_triangles':sum(o['tri'] for o in native),'world_unique_vertex_quantized_sets_equal_1e4':native_points==sorted(set(tuple(round(float(v),4) for v in o.matrix_world@x.co) for o in s.objects if o.type=='MESH' for x in o.data.vertices)),'imported_objects':len(imp),'triangles':sum(o['tri'] for o in imp),'embedded_images':len(g.get('images',[])),'all_images_embedded':all('bufferView' in i for i in g.get('images',[])),'image_mime_types':[i.get('mimeType') for i in g.get('images',[])],'materials':len(g.get('materials',[])),'double_sided_materials':sum(m.get('doubleSided',False) for m in g.get('materials',[])),'imported_images':imported_images,'imported_image_count':sum(i['pixels']>0 for i in imported_images)};json.dump(report,open(D+'/qa/GLB真实回导.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/roundtrip.blend',compress=True)

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=D+'/models/Garden_Complete_White.glb')
wi=stats();json.dump({'imported_meshes':len(wi),'triangles':sum(o['tri'] for o in wi),'native_triangles':sum(o['tri'] for o in native),'nonempty':len(wi)>0,'world_unique_vertex_quantized_sets_equal_1e4':native_points==sorted(set(tuple(round(float(v),4) for v in o.matrix_world@x.co) for o in s.objects if o.type=='MESH' for x in o.data.vertices))},open(D+'/qa/白模GLB真实回导.json','w'),indent=2)
