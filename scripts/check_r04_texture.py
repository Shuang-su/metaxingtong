import struct,json,pathlib,hashlib,io
from PIL import Image,ImageChops
P=pathlib.Path(__file__).resolve().parents[1]
data=(P/'models/R04_material.glb').read_bytes();pos=12;j=None;binary=None
while pos<len(data):
 n,typ=struct.unpack_from('<II',data,pos);chunk=data[pos+8:pos+8+n];pos+=8+n
 if typ==0x4E4F534A:j=json.loads(chunk)
 elif typ==0x004E4942:binary=chunk
src=P/'dependencies/R04-generated-color-regions.png';im=Image.open(src).convert('RGBA');out=[]
for x in j.get('images',[]):
 v=j['bufferViews'][x['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];other=Image.open(io.BytesIO(b)).convert('RGBA');equal=other.size==im.size and all(lo==0 and hi==0 for lo,hi in ImageChops.difference(im,other).getextrema())
 out.append({'name':x.get('name'),'mimeType':x.get('mimeType'),'embedded_bytes':len(b),'embedded_sha256':hashlib.sha256(b).hexdigest(),'size':list(other.size),'decoded_RGBA_equal_external_generated_png':equal})
r={'external_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'images':out,'all_embedded_pixels_match':bool(out) and all(x['decoded_RGBA_equal_external_generated_png'] for x in out),'status':'Generated color-region dependency only, NOT original source texture'}
(P/'qa/R04-texture-embedding-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
