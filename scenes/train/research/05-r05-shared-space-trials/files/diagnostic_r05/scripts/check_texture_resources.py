from pathlib import Path
from PIL import Image
import json,struct,hashlib,io
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c'
def load(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);binary=raw[28+n:];rows={}
 for im in j.get('images',[]):
  v=j['bufferViews'][im['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];i=Image.open(io.BytesIO(b));i.load();rows[im['name']]={'sha256':hashlib.sha256(b).hexdigest(),'pixel_sha256':hashlib.sha256(i.tobytes()).hexdigest(),'size':i.size,'mode':i.mode}
 return j,rows
j,cur=load(O/'train_r05c_material_candidate.glb');_,old=load(R.parent/'deliverables/03_train_material.glb');images=[]
for n,x in cur.items():images.append({'name':n,**x,'matches_frozen_r03_embedded_image_bytes':x['sha256']==old.get(n,{}).get('sha256')})
refs=json.load(open(O/'texture_reference_manifest.json'));files=[]
for item in refs['images']:
 p=O/item['file'];im=Image.open(p);im.load();n=item['image'];row={'image':n,'file':item['file'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded_pixel_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'size':im.size,'mode':im.mode};files.append(row)
# glTF material slots explicitly list basecolor, metallic-roughness and normal texture indices.
mat=[]
for m in j.get('materials',[]):
 mat.append({'name':m.get('name'),'pbr':m.get('pbrMetallicRoughness'),'normalTexture':m.get('normalTexture'),'extensions':m.get('extensions')})
out={'source_glb_sha256':hashlib.sha256((O/'train_r05c_material_candidate.glb').read_bytes()).hexdigest(),'all19_embedded_resources_unchanged_from_r03':all(x['matches_frozen_r03_embedded_image_bytes'] for x in images),'embedded_images':images,'actual_packed_blend_images':files,'gltf_material_bindings':mat,'scope':'Shared geometry only stage: no raster/material edits. Roughness glTF packing may change channel layout relative to author image, so glTF image bytes are independently tracked.'};(O/'texture_glb_resource_check.json').write_text(json.dumps(out,indent=2));print(len(images),len(files),out['all19_embedded_resources_unchanged_from_r03'])
