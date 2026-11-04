import struct,json,hashlib
from pathlib import Path
R=Path('forest-diagnostic-replay-20261104');out={}
def load(p):
 b=p.read_bytes();l,t=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+l]);off=20+l;bl,bt=struct.unpack_from('<II',b,off);return j,b[off+8:off+8+bl],hashlib.sha256(b).hexdigest()
def acc(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];size={5126:4,5125:4,5123:2,5121:1}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size);return b''.join(b[off+k*stride:off+k*stride+size] for k in range(a['count']))
for mode in ['material','white']:
 a,ab,ash=load(R/f'models/R10_support-diagnostic_{mode}.glb');b,bb,bsh=load(R/f'models/R11_support-diagnostic_{mode}.glb');am={m['name']:m for m in a['meshes']};bm={m['name']:m for m in b['meshes']};changed=[];uv=[]
 for n,m in am.items():
  for p,q in zip(m['primitives'],bm[n]['primitives']):
   for k in ['POSITION','NORMAL']:
    if acc(a,ab,p['attributes'][k])!=acc(b,bb,q['attributes'][k]):changed.append(n+':'+k)
   if acc(a,ab,p['indices'])!=acc(b,bb,q['indices']):changed.append(n+':indices')
   if '_inferred_stems' in n:
    raw=acc(b,bb,q['attributes']['TEXCOORD_0']);vals=struct.unpack('<'+'f'*(len(raw)//4),raw);uv.append({'mesh':n,'uv_pairs':len(vals)//2,'all_finite':all(__import__('math').isfinite(x) for x in vals),'range':[min(vals),max(vals)],'had_uv_r10':'TEXCOORD_0'in p['attributes']})
 out[mode]={'r10_sha256':ash,'r11_sha256':bsh,'geometry_accessor_changes':changed,'camera_json_equal':a['cameras']==b['cameras'],'nodes_json_equal':a['nodes']==b['nodes'],'mesh_names_equal':am.keys()==bm.keys(),'stem_uv':uv,'materials_json_equal':a['materials']==b['materials'],'embedded_image_bytes_equal':all(ab[x['byteOffset']:x['byteOffset']+x['byteLength']]==bb[y['byteOffset']:y['byteOffset']+y['byteLength']] for x,y in [(a['bufferViews'][im['bufferView']],b['bufferViews'][jm['bufferView']]) for im,jm in zip(a.get('images',[]),b.get('images',[]))])}
Path('independent-forest-replay-qa-20261104/R11-glb-payload-check.json').write_text(json.dumps(out,indent=2));print([(k,v['geometry_accessor_changes'],len(v['stem_uv']),v['camera_json_equal'],v['nodes_json_equal'])for k,v in out.items()])
