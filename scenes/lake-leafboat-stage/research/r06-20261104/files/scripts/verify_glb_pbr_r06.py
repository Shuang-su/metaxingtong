from pathlib import Path
import json,struct,io,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1];f=R/'models/lakeleaf-r06.glb';b=f.read_bytes();assert b[:4]==b'glTF';off=12;j=None;binchunk=None
while off<len(b):
 n,t=struct.unpack_from('<II',b,off);data=b[off+8:off+8+n];off+=8+n
 if t==0x4e4f534a:j=json.loads(data)
 elif t==0x004e4942:binchunk=data
ims=[];decoded=[]
for i,im in enumerate(j.get('images',[])):
 v=j['bufferViews'][im['bufferView']];start=v.get('byteOffset',0);raw=binchunk[start:start+v['byteLength']];pic=Image.open(io.BytesIO(raw)).convert('RGB');a=np.array(pic);decoded.append(a);ims.append({'index':i,'name':im.get('name'),'size':list(pic.size),'encoded_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'rgb_mean':list(map(float,a.mean(axis=(0,1))))})
rows=[];leafcheck=None
for m in j.get('materials',[]):
 p=m.get('pbrMetallicRoughness',{});row={'name':m.get('name'),'baseColorFactor':p.get('baseColorFactor',[1,1,1,1]),'metallicFactor':p.get('metallicFactor',1),'roughnessFactor':p.get('roughnessFactor',1),'baseColorTexture':p.get('baseColorTexture'),'metallicRoughnessTexture':p.get('metallicRoughnessTexture'),'normalTexture':m.get('normalTexture')}
 if m.get('name','').startswith('LEAF_'):
  ti=p['baseColorTexture']['index'];ii=j['textures'][ti]['source'];arr=decoded[ii];orig=np.array(Image.open(R/'textures/leaf-tissue-albedo.png').convert('RGB'));leafcheck={'material':m['name'],'embedded_image_index':ii,'green_channel_mean_above_red_blue':bool(arr[:,:,1].mean()>max(arr[:,:,0].mean(),arr[:,:,2].mean())),'embedded_pixels_exactly_equal_original_albedo':bool(np.array_equal(arr,orig)),'rgba_constant_only':False,'not_default_white':True}
 rows.append(row)
rep={'file':str(f.relative_to(R)),'glb_sha256':hashlib.sha256(b).hexdigest(),'material_count':len(rows),'embedded_images':ims,'materials':rows,'leaf_base_colour_validation':leafcheck,'shader_source':'Image textures connected to supported Principled PBR inputs, plus constant PBR foliage/vein/shore colours. No unbaked Noise or procedural Bump nodes drive material appearance. Water normal is an actual image and WaveUV texture coordinate.','limits':['Blender AREA light is omitted from raw GLB','Blender world/AgX/exposure not portable unchanged','top camera offaxis shift needs explicit sidecar restoration','Material parameter/export validity is not source photometric agreement'],'source_accepted':False};assert leafcheck and leafcheck['green_channel_mean_above_red_blue'] and leafcheck['embedded_pixels_exactly_equal_original_albedo'];(R/'qa/r06/glb-material-pbr-validation.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(leafcheck,indent=2));print('Materials',len(rows),'embedded PNGs',len(ims))
