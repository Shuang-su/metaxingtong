import pathlib,json,struct,io,hashlib
import numpy as np
from PIL import Image
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105');out={}
for mode in ['material','white']:
 f=P/'models'/f'R04_{mode}.glb';data=f.read_bytes();ln=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+ln]);bl=data[28+ln:];imgs=[];decoded=[]
 for im in g.get('images',[]):
  bv=g['bufferViews'][im['bufferView']];raw=bl[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']];a=np.array(Image.open(io.BytesIO(raw)).convert('RGB'));decoded.append(a);imgs.append({'name':im.get('name'),'sha256':hashlib.sha256(raw).hexdigest(),'shape':list(a.shape),'range':[int(a.min()),int(a.max())]})
 mesh=g['meshes'][next(n['mesh'] for n in g['nodes'] if n.get('name')=='FLOOR_finite_slab')];prim=mesh['primitives'][0];mat=g['materials'][prim['material']];checks={};pbr=mat.get('pbrMetallicRoughness',{})
 for slot,entry,fn,ch in [('color',pbr.get('baseColorTexture'),'stone_diffuse.png',None),('rough',pbr.get('metallicRoughnessTexture'),'stone_roughness.png',1),('normal',mat.get('normalTexture'),'stone_normal.png',None)]:
  if not entry:checks[slot]={'present':False};continue
  imindex=g['textures'][entry['index']]['source'];actual=decoded[imindex];expected=np.array(Image.open(P/'textures'/fn).convert('RGB'));aa=actual if ch is None else actual[:,:,ch];ee=expected if ch is None else expected[:,:,0];checks[slot]={'present':True,'max_pixel_difference':int(np.max(abs(aa.astype(int)-ee.astype(int)))),'different_channels':int(np.count_nonzero(aa!=ee)),'entry':entry}
 out[mode]={'images':imgs,'floor_material':mat,'floor_attributes':prim['attributes'],'texture_pixel_checks':checks,'external_uris':[b.get('uri') for b in g.get('buffers',[]) if b.get('uri')]+[i.get('uri') for i in g.get('images',[]) if i.get('uri')]}
(Q/'R04-texture-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
