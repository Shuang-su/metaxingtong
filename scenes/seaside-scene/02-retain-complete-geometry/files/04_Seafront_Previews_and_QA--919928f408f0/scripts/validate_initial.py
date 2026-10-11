import bpy,bmesh,json,os,hashlib,struct
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
def audit():
 out={'objects':[],'images':[]};allv=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);o.data.calc_loop_triangles();raw_boundary=sum(e.is_boundary for e in bm.edges);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
  d={'raw_uv_split_boundary_edges':raw_boundary,'name':o.name,'vertices':len(bm.verts),'triangles':len(o.data.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'uv':bool(o.data.uv_layers)}
  d['thin_surface_allowed']=('leaflet' in o.name or 'groundcover' in o.name or 'ocean' in o.name.lower())
  out['objects'].append(d);allv.extend([o.matrix_world@v.co for v in o.data.vertices]);bm.free()
 out['bounds']=[[min(v[i] for v in allv) for i in range(3)],[max(v[i] for v in allv) for i in range(3)]]
 for im in bpy.data.images:
  if im.source=='FILE':out['images'].append({'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'path':im.filepath})
 out['totals']={'meshes':len(out['objects']),'triangles':sum(d['triangles'] for d in out['objects']),'unapproved_boundary_objects':[d['name'] for d in out['objects'] if d['boundary_edges'] and not d['thin_surface_allowed']],'degenerate_faces':sum(d['degenerate_faces'] for d in out['objects'])}
 return out
results={}
for variant in ['Textured']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend');results[variant+'_blend']=audit()
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+'/models/Seafront_'+variant+'.glb');results[variant+'_glb_import']=audit();bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/roundtrip_'+variant+'.blend',compress=True)
 p=R+'/models/Seafront_'+variant+'.glb';data=open(p,'rb').read();ln,typ=struct.unpack_from('<II',data,12);j=json.loads(data[20:20+ln]);results[variant+'_glb_structure']={'images':len(j.get('images',[])),'all_images_embedded':all('bufferView' in x for x in j.get('images',[])),'external_buffer_uris':[x.get('uri') for x in j.get('buffers',[]) if 'uri' in x],'nodes':len(j.get('nodes',[]))}
json.dump(results,open(R+'/qa/geometry_roundtrip_validation.json','w'),indent=2,ensure_ascii=False)
