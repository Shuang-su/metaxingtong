import bpy,bmesh,pathlib,json,hashlib
P=(pathlib.Path(__file__).resolve().parents[2] if pathlib.Path(__file__).resolve().parent.name=='scripts' else pathlib.Path(__file__).resolve().parent);D=P/'delivery';f=D/'Terrace_RightRearTable_Rebuilt_20261011.blend'
bpy.ops.wm.open_mainfile(filepath=str(f));out={'candidate_blend_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'components':{}}
for o in bpy.data.collections['07_Moon_Side_Table'].all_objects:
 if not (o.name.startswith('Side_table_') or o.name=='White_sphere_under_table'):continue
 bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);components=[]
 while unseen:
  stack=[unseen.pop()];cnt=0
  while stack:
   v=stack.pop();cnt+=1
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in unseen:unseen.remove(n);stack.append(n)
  components.append(cnt)
 out['components'][o.name]={'connected_components':len(components),'component_vertex_counts':components,'world_transform_positive_determinant':o.matrix_world.determinant()>0};bm.free()
out['all_structural_meshes_single_connected_shell']=all(v['connected_components']==1 for v in out['components'].values());(D/'independent_connected_components_qa.json').write_text(json.dumps(out,indent=2));print('COMPONENTS',out['all_structural_meshes_single_connected_shell'])
