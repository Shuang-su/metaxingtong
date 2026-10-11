import bpy,json,math
from pathlib import Path
from mathutils import Vector,kdtree
R=Path(__file__).resolve().parents[1];results=[]
def snapshot():
 bpy.context.view_layer.update();out={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  verts=[tuple(o.matrix_world@v.co) for v in o.data.vertices];lo=[min(v[j] for v in verts) for j in range(3)];hi=[max(v[j] for v in verts) for j in range(3)];o.data.calc_loop_triangles()
  out[o.name]={'verts':verts,'triangles':len(o.data.loop_triangles),'bounds':[lo,hi],'uv':bool(o.data.uv_layers),'materials':len(o.data.materials)}
 return out
for stem in ['material','white']:
 bf=R/'models'/('01_bedroom_material.blend' if stem=='material' else '02_bedroom_white.blend');gf=R/'models'/('03_bedroom_material.glb' if stem=='material' else '04_bedroom_white.glb')
 bpy.ops.wm.open_mainfile(filepath=str(bf));a=snapshot();packed=sum(bool(im.packed_file) for im in bpy.data.images)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(gf));b=snapshot();missing=sorted(set(a)-set(b));unexpected=sorted(set(b)-set(a));maxerr=0;bad=[];tridiff=[];boundserr=0
 for name in set(a)&set(b):
  aa=a[name];bb=b[name]
  if aa['triangles']!=bb['triangles']:tridiff.append([name,aa['triangles'],bb['triangles']])
  for source,target in [(aa['verts'],bb['verts']),(bb['verts'],aa['verts'])]:
   tree=kdtree.KDTree(len(target))
   for i,v in enumerate(target):tree.insert(Vector(v),i)
   tree.balance();err=max(tree.find(Vector(v))[2] for v in source);maxerr=max(maxerr,err)
   if err>1e-5:bad.append([name,err])
  boundserr=max(boundserr,max(abs(aa['bounds'][j][k]-bb['bounds'][j][k]) for j in range(2) for k in range(3)))
 r={'variant':stem,'source_mesh_objects':len(a),'imported_mesh_objects':len(b),'source_triangles':sum(q['triangles'] for q in a.values()),'imported_triangles':sum(q['triangles'] for q in b.values()),'source_vertices':sum(len(q['verts']) for q in a.values()),'imported_vertices':sum(len(q['verts']) for q in b.values()),'missing_objects':missing,'unexpected_objects':unexpected,'max_bidirectional_nearest_vertex_error_m':maxerr,'max_bound_error_m':boundserr,'objects_above_10_micrometers':bad,'triangle_count_mismatches':tridiff,'all_imported_meshes_have_uv':all(q['uv'] for q in b.values()),'source_packed_images':packed,'imported_material_count':len(bpy.data.materials),'imported_image_count':len(bpy.data.images),'passed':not missing and not unexpected and not bad and not tridiff and all(q['uv'] for q in b.values())}
 results.append(r)
(R/'analysis/glb_reimport_validation.json').write_text(json.dumps(results,indent=2));print('GLB_VALIDATION',json.dumps(results))
