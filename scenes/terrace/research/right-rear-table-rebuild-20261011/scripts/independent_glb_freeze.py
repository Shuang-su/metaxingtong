import json,struct,pathlib,hashlib,collections
P=(pathlib.Path(__file__).resolve().parents[2] if pathlib.Path(__file__).resolve().parent.name=='scripts' else pathlib.Path(__file__).resolve().parent);D=P/'delivery'
def read(p):
 data=p.read_bytes();n=struct.unpack_from('<I',data,12)[0];j=json.loads(data[20:20+n]);o=20+n;ln=struct.unpack_from('<I',data,o)[0];return j,data[o+8:o+8+ln],hashlib.sha256(data).hexdigest()
a,ab,ah=read(next((P/'baseline').rglob('*.glb')));b,bb,bh=read(D/'Terrace_CompleteSpace_RightRearTable_Rebuilt.glb');exclude=set(json.loads((D/'table_names.json').read_text()))
def norm(n,doc):
 d=dict(n)
 if 'children'in d:d['children']=[doc['nodes'][i].get('name') for i in d['children']]
 return d
an={n.get('name'):norm(n,a) for n in a['nodes'] if n.get('name') not in exclude};bn={n.get('name'):norm(n,b) for n in b['nodes'] if n.get('name') not in exclude}
# Node children referring to the removed table should disappear; all other relationships remain.
for n in an.values():
 if 'children'in n:n['children']=[x for x in n['children'] if x not in exclude]
for n in bn.values():
 if 'children'in n:n['children']=[x for x in n['children'] if x not in exclude]
out={'baseline_glb_sha256':ah,'candidate_full_glb_sha256':bh,'unrelated_node_count':len(an),'unrelated_node_differences':[k for k in set(an)|set(bn) if an.get(k)!=bn.get(k)],'duplicate_unrelated_node_names_baseline':len(an)!=sum(n.get('name') not in exclude for n in a['nodes']),'existing_mesh_descriptors_preserved':a['meshes']==b['meshes'][:len(a['meshes'])],'existing_accessor_descriptors_preserved':a['accessors']==b['accessors'][:len(a['accessors'])],'existing_buffer_view_descriptors_preserved':a['bufferViews']==b['bufferViews'][:len(a['bufferViews'])],'existing_binary_buffer_prefix_preserved':bb[:len(ab)]==ab,'asset_definitions_preserved':{k:a.get(k)==b.get(k) for k in ('materials','images','textures','samplers','cameras')},'note':'Old table mesh resources may remain unreferenced in the binary for exact unrelated-resource preservation. Removed table nodes are absent from scene graph.'}
out['old_curved_cage_nodes_absent']=not any(n.get('name','').startswith('Side_table_curved_cage_leg') for n in b['nodes']);out['new_flat_rib_nodes_count']=sum(n.get('name','').startswith('Side_table_flat_rib_') for n in b['nodes'])
(D/'independent_glb_freeze_qa.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
