import bpy,json,math,struct,hashlib
from pathlib import Path
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];O=R/'checkpoint_r05c'
def snapshot():
 out={};mats={}
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if n:mats[m.name]={'color':list(n.inputs['Base Color'].default_value),'textured':n.inputs['Base Color'].is_linked,'transmission':n.inputs['Transmission Weight'].default_value,'roughness':n.inputs['Roughness'].default_value,'roughness_textured':n.inputs['Roughness'].is_linked}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  me=o.data;me.calc_loop_triangles();vs=[o.matrix_world@v.co for v in me.vertices];area=sum((vs[t.vertices[1]]-vs[t.vertices[0]]).cross(vs[t.vertices[2]]-vs[t.vertices[0]]).length*.5 for t in me.loop_triangles)
  out[o.name]={'vs':vs,'area':area,'triangles':len(me.loop_triangles),'uv_layers':len(me.uv_layers),'material_names':[m.name for m in me.materials if m]}
 return out,mats
frozen=next(x for x in json.loads((O/'checkpoint_manifest.json').read_text())['blends'] if x['kind']=='white');assert hashlib.sha256(Path(frozen['file']).read_bytes()).hexdigest()==frozen['sha256'];bpy.ops.wm.open_mainfile(filepath=frozen['file']);original,om=snapshot()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'train_r05c_white_candidate.glb'));imp,im=snapshot();rows=[]
for name,a in original.items():
 b=imp.get(name)
 if b is None:rows.append({'name':name,'missing':True});continue
 errs=[]
 for p,q in [(a['vs'],b['vs']),(b['vs'],a['vs'])]:
  kd=KDTree(len(q))
  for i,v in enumerate(q):kd.insert(v,i)
  kd.balance();errs.append(max(kd.find(v)[2] for v in p))
 rows.append({'name':name,'max_vertex_error_both_directions':errs,'area_difference':abs(a['area']-b['area']),'triangles_match':a['triangles']==b['triangles'],'uv_present_both':a['uv_layers']>0 and b['uv_layers']>0,'material_names_match':a['material_names']==b['material_names']})
colors=[]
for n,a in om.items():
 if n not in im:continue
 b=im[n];e=max(abs(x-y) for x,y in zip(a['color'],b['color']))
 colors.append({'name':n,'source':a,'reimport':b,'max_factor_error':e,'status':'texture-backed compare resources separately' if a['textured'] else 'matched' if e<1e-5 else 'DIFFERENT'})
report={'source_blend_sha256':frozen['sha256'],'source':'checkpoint white blend','export':'train_r05c_white_candidate.glb','actual_reimport':True,'mesh_count_original':len(original),'mesh_count_import':len(imp),'missing_names':sorted(set(original)-set(imp)),'extra_names':sorted(set(imp)-set(original)),'max_bidirectional_vertex_error':max(max(r['max_vertex_error_both_directions']) for r in rows if 'max_vertex_error_both_directions'in r),'max_area_difference':max(r['area_difference'] for r in rows if 'area_difference'in r),'all_triangle_counts_match':all(r.get('triangles_match',False) for r in rows),'all_uv_present':all(r.get('uv_present_both',False) for r in rows),'color_factor_mismatches':[r for r in colors if r['status']=='DIFFERENT'],'materials':colors,'per_object':rows,'limitations':'Vertex sets and surface area/count checked; does not certify semantic fidelity. glTF area lights are not exported; reimport preview appends original lights/world explicitly.'}
(O/'white_roundtrip_detail.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['per_object','materials']},indent=2))
