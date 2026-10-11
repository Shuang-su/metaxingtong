import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c';item=next(x for x in json.loads((O/'checkpoint_manifest.json').read_text())['blends'] if x['kind']=='material')
def snap():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  m=o.data;uv=m.uv_layers.active;nm=o.matrix_world.to_3x3().inverted().transposed()
  pairs=set();norms=set()
  for i,l in enumerate(m.loops):
   v=o.matrix_world@m.vertices[l.vertex_index].co;n=(nm@m.corner_normals[i].vector).normalized();p=tuple(round(float(a),4) for a in v)
   if uv:pairs.add(p+tuple(round(float(a),4) for a in uv.data[i].uv))
   norms.add(p+tuple(round(float(a),3) for a in n))
  out[o.name]={'uv':pairs,'normals':norms}
 return out
bpy.ops.wm.open_mainfile(filepath=item['file']);a=snap();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'train_r05c_material_candidate.glb'));b=snap();rows=[]
for n,x in a.items():
 y=b[n];rows.append({'name':n,'uv_unique_pairs_source':len(x['uv']),'uv_unique_pairs_reimport':len(y['uv']),'uv_set_equal_at_1e4':x['uv']==y['uv'],'normal_set_equal_at_1e3':x['normals']==y['normals'],'uv_symmetric_difference':len(x['uv']^y['uv']),'normal_symmetric_difference':len(x['normals']^y['normals'])})
out={'input_blend_sha256':item['sha256'],'gltf_sha256':hashlib.sha256((O/'train_r05c_material_candidate.glb').read_bytes()).hexdigest(),'comparison':'Unique per-corner world-position+UV rounded 1e-4, world-position+normal normals rounded1e-3. Quantization-boundary differences are retained, not silently passed.','objects':len(rows),'uv_exact_objects':sum(x['uv_set_equal_at_1e4'] for x in rows),'normal_exact_objects':sum(x['normal_set_equal_at_1e3'] for x in rows),'nonexact_uv_objects':[x for x in rows if not x['uv_set_equal_at_1e4']],'nonexact_normal_objects':[x for x in rows if not x['normal_set_equal_at_1e3']]}
(O/'uv_normal_roundtrip.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if not k.startswith('nonexact')},indent=2));print('UV_NONEXACT',len(out['nonexact_uv_objects']),'NORMAL_NONEXACT',len(out['nonexact_normal_objects']))
