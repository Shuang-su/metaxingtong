from pathlib import Path
import struct,json,io,hashlib
import numpy as np
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent
src=P/'dependencies/R04-generated-color-regions.png';a=np.array(Image.open(src).convert('RGBA'));out={'external_sha':hashlib.sha256(src.read_bytes()).hexdigest(),'images':[]}
for mode in ['material','white']:
 data=(P/f'models/R04_{mode}.glb').read_bytes();pos=12;j=None;binary=None
 while pos<len(data):
  n,t=struct.unpack_from('<II',data,pos);chunk=data[pos+8:pos+8+n];pos+=8+n
  if t==0x4e4f534a:j=json.loads(chunk)
  elif t==0x004e4942:binary=chunk
 for im in j.get('images',[]):
  v=j['bufferViews'][im['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];arr=np.array(Image.open(io.BytesIO(b)).convert('RGBA'));out['images'].append({'mode':mode,'sha':hashlib.sha256(b).hexdigest(),'shape':list(arr.shape),'equal_all_channels':bool(np.array_equal(a,arr)),'max_channel_error':int(np.abs(a.astype(int)-arr.astype(int)).max())})
 out[mode+'_image_count']=len(j.get('images',[]));out[mode+'_textured_meshes']=[m['name']for m in j['meshes']if any('TEXCOORD_0'in p['attributes']for p in m['primitives'])]
b=(O/'packed-generated-region.png').read_bytes();out['packed_sha']=hashlib.sha256(b).hexdigest();out['packed_equals_external_bytes']=b==src.read_bytes();out['packed_equals_pixels']=bool(np.array_equal(a,np.array(Image.open(io.BytesIO(b)).convert('RGBA'))));(O/'texture-check.json').write_text(json.dumps(out,indent=2));print(out)
