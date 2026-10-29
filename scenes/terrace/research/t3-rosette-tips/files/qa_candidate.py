import bpy,bmesh,json,hashlib,array
R='/workspace/scratch/fa58bfcf0425/terrace_table_candidate_v2'
records=[]
for o in bpy.data.collections['T2_Visible_Table_Decor_CANDIDATE'].objects:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 # Validate topology only. No candidate changes are saved.
 records.append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume_after_consistent_normals':bm.calc_volume(signed=True),'purpose':'surface marking, intentionally open' if 'Motif' in o.name else 'closed plant/pot geometry'})
 bm.free()
json.dump({'objects':records,'all_nonmarking_closed':all(r['nonmanifold_edges']==0 for r in records if 'Motif' not in r['name']),'not_a_multiview_fidelity_pass':True},open(R+'/new_geometry_qa.json','w'),indent=2)
print('QA',len(records))
