import bpy,json,hashlib,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables';out={}
for fn in ['03_train_material.glb','04_train_white.glb']:
 p=O/fn
 with p.open('rb') as f:
  magic,version,ln=struct.unpack('<4sII',f.read(12));jl,jt=struct.unpack('<II',f.read(8));j=json.loads(f.read(jl))
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update();tris=[];lo=[1e9]*3;hi=[-1e9]*3;finite=True;mesh=[o for o in bpy.data.objects if o.type=='MESH'];vc=0
 for o in mesh:
  me=o.data;vc+=len(me.vertices);me.calc_loop_triangles();wp=[]
  for v in me.vertices:
   q=o.matrix_world@v.co;pos=tuple(round(float(a),5) for a in q);wp.append(pos);finite=finite and all(math.isfinite(a) for a in pos)
   for i in range(3):lo[i]=min(lo[i],pos[i]);hi[i]=max(hi[i],pos[i])
  for t in me.loop_triangles:tris.append(struct.pack('<9f',*[c for point in sorted([wp[i] for i in t.vertices]) for c in point]))
 h=hashlib.sha256()
 for t in sorted(tris):h.update(t)
 out[fn]={'format_version':version,'declared_length_matches_file':ln==p.stat().st_size,'reimport_success':True,'mesh_objects':len(mesh),'vertices':vc,'triangles':len(tris),'world_bounds':[lo,hi],'finite_coordinates':finite,'canonical_world_triangle_sha256_1e5':h.hexdigest(),'embedded_images':len(j.get('images',[])),'external_image_uris':[i.get('uri') for i in j.get('images',[]) if i.get('uri')],'gltf_materials':len(j.get('materials',[])),'all_images_embedded':all('bufferView' in i for i in j.get('images',[]))}
 print('VALIDATED',fn,out[fn],flush=True)
out['same_canonical_geometry']=out['03_train_material.glb']['canonical_world_triangle_sha256_1e5']==out['04_train_white.glb']['canonical_world_triangle_sha256_1e5'];(O/'glb_validation.json').write_text(json.dumps(out,indent=2));meta=json.loads((O/'verification.json').read_text());meta['glb_validation']=out;(O/'verification.json').write_text(json.dumps(meta,indent=2));print('GLB_VALIDATION_DONE',flush=True)
