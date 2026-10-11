import struct,json,io,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c';p=O/'train_r05c_material_candidate.glb';b=p.read_bytes();ln=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+ln]);bn=20+ln;blen=struct.unpack_from('<I',b,bn)[0];binary=b[bn+8:bn+8+blen];replacements={};rows=[]
for im in j.get('images',[]):
 idx=im['bufferView'];v=j['bufferViews'][idx];raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];img=Image.open(io.BytesIO(raw));img.load();buf=io.BytesIO();img.save(buf,format='PNG',optimize=True,compress_level=9);new=buf.getvalue();same=Image.open(io.BytesIO(new));same.load();assert same.mode==img.mode and same.size==img.size and same.tobytes()==img.tobytes()
 if len(new)<len(raw):replacements[idx]=new
 rows.append({'name':im.get('name'),'bytes_before':len(raw),'bytes_after':min(len(new),len(raw)),'decoded_mode':img.mode,'decoded_size':img.size,'decoded_pixel_sha256':hashlib.sha256(img.tobytes()).hexdigest(),'exact_pixels_equal':True})
out=bytearray();lastend=0
for idx,v in sorted(enumerate(j['bufferViews']),key=lambda kv:kv[1].get('byteOffset',0)):
 off=v.get('byteOffset',0);assert off>=lastend;lastend=off+v['byteLength'];raw=replacements.get(idx,binary[off:lastend]);out.extend(b'\0'*((-len(out))%4));v['byteOffset']=len(out);v['byteLength']=len(raw);out.extend(raw)
j['buffers'][0]['byteLength']=len(out);out.extend(b'\0'*((-len(out))%4));jb=json.dumps(j,separators=(',',':'),ensure_ascii=False).encode();jb+=b' '*((-len(jb))%4);result=struct.pack('<4sII',b'glTF',2,12+8+len(jb)+8+len(out))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(out),b'BIN\0')+out
rawpath=R/'analysis/material_unoptimized_18064800.glb';rawpath.write_bytes(b);p.write_bytes(result);report={'operation':'Lossless PNG recompression only; geometry and accessor data unchanged; JSON compacted and bufferView offsets rebuilt with4-byte alignment','unoptimized_sha256':hashlib.sha256(b).hexdigest(),'optimized_sha256':hashlib.sha256(result).hexdigest(),'bytes_before':len(b),'bytes_after':len(result),'under18MB':len(result)<18_000_000,'images':rows};(O/'lossless_resource_compression.json').write_text(json.dumps(report,indent=2));print(len(b),'->',len(result),'saved',len(b)-len(result));assert len(result)<18_000_000
