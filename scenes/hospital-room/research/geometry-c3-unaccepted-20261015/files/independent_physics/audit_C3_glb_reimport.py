"""Read-only C2->C3 delta audit and actual fresh-scene GLB reimport audit.
No .blend or GLB writes. JSON outputs are uncompressed original reports.
"""
import bpy,json,hashlib,struct,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent/'models'
ns={'__file__':str(OUT/'audit_physics.py')}
exec(Path(ns['__file__']).read_text().split('for s in sys.argv[sys.argv.index')[0],ns)
extract,record_pair=ns['extract'],ns['record_pair'];CN=ns['CURTAIN'];SN='Sofa • reclined back cushion 1'
P2=ROOT/'hospital_C2_small_shared_geometry_UNACCEPTED.blend';P3=ROOT/'hospital_C3_width_refinement_UNACCEPTED.blend';GLB=ROOT/'hospital_C3_width_refinement_UNACCEPTED.glb'
SCALE=.7533634597251563;LEFT=1.6446596384048462

def snapshot():
 dg=bpy.context.evaluated_depsgraph_get();rr={o.name:extract(o,dg) for o in bpy.data.objects if o.type=='MESH'}
 cams={o.name:{'matrix_world':[list(r) for r in o.matrix_world],'projection_1920x1080':[list(r) for r in o.calc_matrix_camera(dg,x=1920,y=1080,scale_x=1,scale_y=1)],'lens':o.data.lens,'sensor_fit':o.data.sensor_fit,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end} for o in bpy.data.objects if o.type=='CAMERA'}
 vis={o.name:{'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'visible_camera':o.visible_camera,'visible_shadow':o.visible_shadow} for o in bpy.data.objects if o.type=='MESH'}
 return rr,cams,vis

def same(a,b):return len(a['verts'])==len(b['verts']) and a['triangles']==b['triangles'] and all(p==q for p,q in zip(a['verts'],b['verts']))
def matrixdiff(a,b):return max(abs(x-y) for r,s in zip(a,b) for x,y in zip(r,s))
def pointset_distance(a,b):
 k=KDTree(len(b));[k.insert(p,i) for i,p in enumerate(b)];k.balance();ds=[k.find(p)[2] for p in a]
 return {'maximum':max(ds,default=0),'mean':sum(ds)/len(ds) if ds else 0,'rms':math.sqrt(sum(x*x for x in ds)/len(ds)) if ds else 0}
def pair_focus(rr,names):
 pairs=[];seen=set()
 for n in names:
  if n not in rr:continue
  for other,r in rr.items():
   if other==n:continue
   key=tuple(sorted((n,other)))
   if key in seen:continue
   seen.add(key);p=record_pair(rr[n],r)
   if p:pairs.append(p)
 return pairs

hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P2,P3,GLB)}
bpy.ops.wm.open_mainfile(filepath=str(P2));r2,c2,v2=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(P3));r3,c3,v3=snapshot()
changed=[n for n in set(r2)&set(r3) if not same(r2[n],r3[n])];added=sorted(set(r3)-set(r2));removed=sorted(set(r2)-set(r3))
expected_errors=[]
for p,q in zip(r2[CN]['verts'],r3[CN]['verts']):expected_errors.append((Vector((LEFT+(p.x-LEFT)*SCALE,p.y,p.z))-q).length)
delta={'C2':str(P2),'C3':str(P3),'changed_meshes':sorted(changed),'added_meshes':added,'removed_meshes':removed,'only_changed_mesh_is_curtain':changed==[CN],'curtain_expected_affine_transform':{'fixed_left_x':LEFT,'scale_x':SCALE,'preserve_world_y_z':True},'maximum_expected_affine_vertex_error':max(expected_errors),'C2_curtain_bounds':r2[CN]['meta']['bounds'],'C3_curtain_bounds':r3[CN]['meta']['bounds'],'all_camera_parameters_unchanged':c2==c3,'object_visibility_unchanged':v2==v3,'source_fidelity_accepted':False}
(OUT/'C3_vs_C2_geometry_delta.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2));print('DELTA',delta,flush=True)
raw=GLB.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);length,kind=struct.unpack_from('<II',raw,12);gltf=json.loads(raw[20:20+length].decode('utf8').rstrip('\x00 '))
# Actual importer, in an empty scene. This is not a GLB header-only validation.
bpy.ops.wm.read_factory_settings(use_empty=True)
t=time.time();result=bpy.ops.import_scene.gltf(filepath=str(GLB));ri,ci,vi=snapshot();seconds=time.time()-t
missing=sorted(set(r3)-set(ri));extra=sorted(set(ri)-set(r3));checks=[]
for n in sorted(set(r3)&set(ri)):
 a,b=r3[n],ri[n];ab=pointset_distance(a['verts'],b['verts']);ba=pointset_distance(b['verts'],a['verts']);bd=matrixdiff(a['meta']['bounds'],b['meta']['bounds'])
 checks.append({'name':n,'source_vertex_count':len(a['verts']),'imported_vertex_count':len(b['verts']),'source_triangles':len(a['triangles']),'imported_triangles':len(b['triangles']),'source_to_imported_nearest_vertex':ab,'imported_to_source_nearest_vertex':ba,'maximum_bounds_component_error':bd,'within_5e_minus_6_scene_units':max(ab['maximum'],ba['maximum'],bd)<=5e-6,'source_bounds':a['meta']['bounds'],'imported_bounds':b['meta']['bounds'],'imported_nonmanifold_edge_count':b['meta']['nonmanifold_edge_count']})
focus=[CN,SN]+[n for n in ri if 'inferred beige column' in n or 'inferred rail end' in n];pairs=pair_focus(ri,focus);cp=[p for p in pairs if CN in (p['a'],p['b'])]
camchecks=[{'name':n,'maximum_world_matrix_error':matrixdiff(c3[n]['matrix_world'],ci[n]['matrix_world']),'maximum_1920x1080_projection_matrix_error':matrixdiff(c3[n]['projection_1920x1080'],ci[n]['projection_1920x1080']),'source_camera':c3[n],'imported_camera':ci[n]} for n in sorted(set(c3)&set(ci))]
report={'glb':str(GLB),'actual_reimport_completed':result=={'FINISHED'},'import_result':sorted(result),'import_seconds':seconds,'glb_header':{'magic':magic.decode(),'version':version,'declared_length':total,'actual_file_bytes':len(raw)},'gltf_extensions_used':gltf.get('extensionsUsed',[]),'source_mesh_count':len(r3),'imported_mesh_count':len(ri),'missing_meshes':missing,'extra_meshes':extra,'all_matched_mesh_world_vertex_sets_and_bounds_within_5e_minus_6':all(x['within_5e_minus_6_scene_units'] for x in checks),'maximum_bidirectional_nearest_vertex_world_error':max(max(x['source_to_imported_nearest_vertex']['maximum'],x['imported_to_source_nearest_vertex']['maximum']) for x in checks),'mesh_checks':checks,'source_camera_count':len(c3),'imported_camera_count':len(ci),'missing_cameras':sorted(set(c3)-set(ci)),'extra_cameras':sorted(set(ci)-set(c3)),'camera_checks':camchecks,'existing_object_visibility_changes':{n:{'source':v3[n],'imported':vi[n]} for n in set(v3)&set(vi) if v3[n]!=vi[n]},'curtain_strict_crossing_objects':sum(p['strict_transverse_crossing_pairs']>0 for p in cp),'curtain_contacts':cp,'global_y_clearance_curtain_to_blinds_and_cords':min(r['meta']['bounds'][0][1] for n,r in ri.items() if n.startswith('Blind'))-ri[CN]['meta']['bounds'][1][1],'focus_contacts':pairs,'source_fidelity_accepted':False,'limits':['This is evaluated world geometry, contact, and camera import QA; source silhouette/occlusion is still unaccepted.','Bidirectional nearest-vertex and triangle-count comparison does not claim byte-identical topology: glTF may split vertices at normals/UV seams.','Material appearance, texture/color conversion, shadows and source-view photometry were not rendered or accepted here.','All units are arbitrary D scene units, not recovered metric dimensions.'],'inputs_sha256':hashes,'all_input_files_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())}
(OUT/'C3_actual_GLB_reimport_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('GLB',{'meshes':len(ri),'missing':missing,'extra':extra,'max_world_error':report['maximum_bidirectional_nearest_vertex_world_error'],'curtain_crossings':report['curtain_strict_crossing_objects'],'clearance':report['global_y_clearance_curtain_to_blinds_and_cords'],'cameras':len(ci),'max_camera_pose_error':max(x['maximum_world_matrix_error'] for x in camchecks),'max_camera_projection_error':max(x['maximum_1920x1080_projection_matrix_error'] for x in camchecks)},flush=True)
