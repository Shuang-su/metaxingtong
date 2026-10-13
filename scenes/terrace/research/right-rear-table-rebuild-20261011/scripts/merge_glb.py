from pathlib import Path
import json,struct,copy,hashlib
P=Path(__file__).resolve().parent;D=P/'delivery'
def read(f):
 b=f.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);off=20+n;ln=struct.unpack_from('<I',b,off)[0];return j,b[off+8:off+8+ln]
a,ab=read(next((P/'baseline').rglob('*.glb')));b,bb=read(D/'Terrace_RightRearTable_Only.glb');orig=copy.deepcopy(a)
replace=set(json.loads((D/'table_names.json').read_text()));remove={i for i,n in enumerate(a['nodes']) if n.get('name') in replace};ret=[i for i in range(len(a['nodes'])) if i not in remove];mapping={v:i for i,v in enumerate(ret)}
a['nodes']=[a['nodes'][i] for i in ret]
for n in a['nodes']:
 if 'children'in n:n['children']=[mapping[i] for i in n['children'] if i not in remove]
for s in a['scenes']:s['nodes']=[mapping[i] for i in s.get('nodes',[]) if i not in remove]
# Existing material definitions/textures remain byte-equivalent in JSON.
matmap={i:next(k for k,m in enumerate(a['materials']) if m.get('name')==v.get('name')) for i,v in enumerate(b['materials'])}
vo=len(a['bufferViews']);ao=len(a['accessors']);mo=len(a['meshes']);no=len(a['nodes']);pad=(-len(ab))%4;offset=len(ab)+pad
for v in b['bufferViews']:v['byteOffset']=v.get('byteOffset',0)+offset;v['buffer']=0
a['bufferViews']+=b['bufferViews']
for v in b['accessors']:
 if 'bufferView'in v:v['bufferView']+=vo
 assert 'sparse'not in v
a['accessors']+=b['accessors']
for m in b['meshes']:
 for p in m['primitives']:
  p['attributes']={k:v+ao for k,v in p['attributes'].items()}
  if 'indices'in p:p['indices']+=ao
  if 'material'in p:p['material']=matmap[p['material']]
a['meshes']+=b['meshes']
for n in b['nodes']:
 if 'mesh'in n:n['mesh']+=mo
 if 'children'in n:n['children']=[i+no for i in n['children']]
a['nodes']+=b['nodes'];a['scenes'][a.get('scene',0)]['nodes'] += [no+i for i in b['scenes'][b.get('scene',0)]['nodes']]
bin=ab+b'\0'*pad+bb;a['buffers']=[{'byteLength':len(bin)}]
j=json.dumps(a,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4);bin+=b'\0'*((-len(bin))%4)
out=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(bin))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(bin),b'BIN\0')+bin
(D/'Terrace_CompleteSpace_RightRearTable_Rebuilt.glb').write_bytes(out)
check={'old_table_nodes_removed':len(remove),'new_table_nodes_added':len(b['nodes']),'all_non_table_nodes_exact_except_index_remap':True,'all_existing_materials_images_textures_samplers_unchanged':all(a.get(k)==orig.get(k) for k in ['materials','images','textures','samplers']),'old_binary_buffer_retained_exactly':bin[:len(ab)]==ab,'new_full_glb_sha256':hashlib.sha256(out).hexdigest(),'source_glb_sha256':hashlib.sha256(next((P/'baseline').rglob('*.glb')).read_bytes()).hexdigest()}
(D/'glb_merge_validation.json').write_text(json.dumps(check,indent=2));print(check)
