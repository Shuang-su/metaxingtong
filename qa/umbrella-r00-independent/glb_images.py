import json,struct,hashlib,io
from PIL import Image
from pathlib import Path
Q=Path(__file__).parent;out={};native=Q/'frozen/textures/umbrella-band-proxy.png'
for mode in ['material','white']:
 p=Q/f'frozen/models/{mode}.glb';raw=p.read_bytes();pos=12;chunks={}
 while pos<len(raw):
  size,t=struct.unpack_from('<II',raw,pos);pos+=8;chunks[t]=raw[pos:pos+size];pos+=size
 j=json.loads(chunks[0x4e4f534a]);bb=chunks[0x004e4942];images=[]
 for im in j.get('images',[]):
  v=j['bufferViews'][im['bufferView']];data=bb[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];a=Image.open(io.BytesIO(data));a.load();ref=Image.open(native).convert('RGB');images.append({'name':im.get('name'),'size':list(a.size),'sha256':hashlib.sha256(data).hexdigest(),'same_native_bytes':data==native.read_bytes(),'same_native_RGB':a.convert('RGB').size==ref.size and a.convert('RGB').tobytes()==ref.tobytes()})
 out[mode]={'glb_sha256':hashlib.sha256(raw).hexdigest(),'images':images,'canopy_mesh_uv_attributes':{m.get('name'): [list(p['attributes']) for p in m['primitives']] for m in j['meshes'] if m.get('name','').startswith('U02')},'textured_materials':[m for m in j.get('materials',[]) if 'baseColorTexture' in m.get('pbrMetallicRoughness',{})]}
(Q/'glb-images.json').write_text(json.dumps(out,indent=2));print(out['material']['images'],out['white']['images'])
