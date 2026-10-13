import bpy,bmesh,pathlib,json,hashlib,struct,math
from mathutils import Vector
P=(pathlib.Path(__file__).resolve().parents[2] if pathlib.Path(__file__).resolve().parent.name=='scripts' else pathlib.Path(__file__).resolve().parent);D=P/'delivery';blend=D/'Terrace_RightRearTable_Rebuilt_20261011.blend';glb=D/'Terrace_CompleteSpace_RightRearTable_Rebuilt.glb'

def bd(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();ps=[o.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return {'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]}
def tp(o,weld=False):
 bm=bmesh.new();bm.from_mesh(o.data)
 if weld:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume_world':bm.calc_volume(signed=True)*o.matrix_world.determinant()};bm.free();return r
bpy.ops.wm.open_mainfile(filepath=str(blend));bounds={o.name:bd(o) for o in bpy.data.collections['07_Moon_Side_Table'].all_objects if o.type=='MESH'}
structural={o.name for o in bpy.data.collections['07_Moon_Side_Table'].all_objects if o.name.startswith('Side_table_') or o.name=='White_sphere_under_table'}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb),merge_vertices=True);bpy.context.view_layer.update()
out={'full_glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'candidate_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'reimported_object_count':len(bpy.data.objects),'table_bounds':{},'structural_topology':{},'note':'Importer merge_vertices=True; weld QA is a temporary in-memory diagnostic only, with tolerance 0.000001. No candidate file changes.'}
for name,ref in bounds.items():
 o=bpy.data.objects.get(name)
 if o is None:out['table_bounds'][name]={'missing':True};continue
 got=bd(o);out['table_bounds'][name]={'expected':ref,'actual':got,'max_error':max(abs(ref[k][i]-got[k][i]) for k in ('min','max') for i in range(3))}
 if name in structural:out['structural_topology'][name]={'imported':tp(o),'welded_for_analysis':tp(o,True)}
out['all_table_bounds_match_within_0_00001']=all('max_error'in v and v['max_error']<1e-5 for v in out['table_bounds'].values())
out['all_structural_welded_manifold_outward']=all(x['welded_for_analysis']['nonmanifold_edges']==0 and x['welded_for_analysis']['inconsistent_winding_edges']==0 and x['welded_for_analysis']['signed_volume_world']>0 for x in out['structural_topology'].values())
(D/'independent_glb_reimport_qa.json').write_text(json.dumps(out,indent=2));print('GLB_RESULT',json.dumps({k:v for k,v in out.items() if k not in ('table_bounds','structural_topology')}),flush=True)
