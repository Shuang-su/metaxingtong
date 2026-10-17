"""Combine already-completed read-only checks and a fixed composite ownership ledger."""
import json,hashlib,copy,math
from pathlib import Path
O=Path(__file__).resolve().parent
material=json.load(open(O/'C25_v1_scene_state.json'));white=json.load(open(O/'C25_v1_white_scene_state.json'));diff=[]
def walk(x,y,path):
 if type(x)!=type(y):diff.append({'path':path,'before':x,'after':y});return
 if isinstance(x,dict):
  for k in sorted(x.keys()|y.keys()):
   if k not in x or k not in y:diff.append({'path':path+'/'+k,'before':x.get(k),'after':y.get(k)})
   else:walk(x[k],y[k],path+'/'+k)
 elif x!=y:diff.append({'path':path,'before':x,'after':y})
walk(material,white,'')
def permitted(d):return d['path'].startswith('/materials/')or ('/mesh/'in d['path']and d['path'].split('/mesh/',1)[1]in ['materials','face_materials'])
allowed=[d for d in diff if permitted(d)];unexpected=[d for d in diff if not permitted(d)]
wr={'status':'PASS'if not unexpected else'FAIL','material_sha256':json.load(open(O/'C25_v1_geometry_report.json'))['sha256_before'],'white_sha256':json.load(open(O/'C25_v1_white_geometry_report.json'))['sha256_before'],'scope':'Exact saved-state comparison of all object raw geometry, topology, matrices/transforms, cameras, visibility, collections, world, scene render/color settings, modifiers and constraints as serialized by verify_geometry.py. Only the intentionally replaced material datablocks, mesh material slots, and face material indices are exempted.','object_count':len(material['objects']),'camera_count':sum(x['type']=='CAMERA'for x in material['objects'].values()),'allowed_material_difference_count':len(allowed),'unexpected_difference_count':len(unexpected),'unexpected_differences':unexpected,'allowed_difference_paths':[d['path']for d in allowed],'material_input_unchanged':json.load(open(O/'C25_v1_geometry_report.json'))['input_unchanged'],'white_input_unchanged':json.load(open(O/'C25_v1_white_geometry_report.json'))['input_unchanged']}
(O/'C25_v1_white_match_report.json').write_text(json.dumps(wr,ensure_ascii=False,indent=2))
old=json.load(open(O/'C23_silhouette_report.json'));new=json.load(open(O/'C25_v1_silhouette_report.json'));op=old['return_object_diagnostics'][0];os=next(b for b in old['support_branches']if b['id']=='H_C_L_RETURN_OUTER');ns=next(b for b in new['support_branches']if b['id']=='H_C_L_RETURN_OUTER');rows=[]
for i in range(8):
 ob=op if i<6 else os;p=ob['points'][i];q=ns['points'][i];assert p['source_xy']==q['source_xy'];assert p['selected_boundary']['fullscene_visible']and q['selected_boundary']['fullscene_visible']
 rows.append({'source_xy':p['source_xy'],'C23_declared_owner':ob['target'],'C25_v1_declared_owner':ns['target'],'C23_absolute_x_error_px':p['absolute_x_error_px'],'C25_v1_absolute_x_error_px':q['absolute_x_error_px'],'C23_fullscene_visible':True,'C25_v1_fullscene_visible':True})
def metric(k):
 d=[r[k]for r in rows];return {'original_source_count':8,'scored_count':8,'rms_px':math.sqrt(sum(x*x for x in d)/8),'max_px':max(d),'within_3px_count':sum(x<=3 for x in d),'all_points_within_tolerance':all(x<=3 for x in d)}
composite={'branch_id':'H_C_L_RETURN_OUTER','status':'SOURCE_UNACCEPTED','tolerance_px':3,'fixed_ownership_ledger':{'C23':'First six original observations, y=906..1020: panel. Last two, y=1048 and 1070: left support.','C25_v1':'All eight original observations: continuous left frame/support object.'},'method':'Predeclared fixed construction ownership, followed by directed outer (leftmost x) boundary at each original source y and full-scene visibility probes. No per-point nearest-object or best-any-object choice. Existing per-object diagnostics are retained unchanged.','interpretation':'Conditional whole-chair composite-return comparison across changed construction. The image does not independently establish the panel/frame split; ownership is explicitly declared, not inferred by minimizing error.','points':rows,'C23':metric('C23_absolute_x_error_px'),'C25_v1':metric('C25_v1_absolute_x_error_px')}
(O/'C25_v1_composite_return.json').write_text(json.dumps(composite,ensure_ascii=False,indent=2))
comparison=json.load(open(O/'C25_v1_comparison.json'));comparison['fixed_composite_return']=composite;comparison['white_material_invariance']=wr;contact=json.load(open(O/'C25_v1_fullscene_contacts.json'));comparison['fullscene_nonchair_contacts']={'new_collision_pairs':contact['new_collision_pairs'],'inherited_collision_pairs':contact['inherited_collision_pairs'],'C23_scanned_pairs':contact['results']['C23']['scanned_pair_count'],'C25_v1_scanned_pairs':contact['results']['C25_v1']['scanned_pair_count'],'artifact':'C25_v1_fullscene_contacts.json'};(O/'C25_v1_comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2))
text=(O/'C25_v1_INDEPENDENT_REVIEW.md').read_text();marker='\n## Supplemental white-copy and non-chair collision checks\n';text=text.split(marker)[0];text+=marker+'\n'
text+=f"White copy: {wr['status']}. {wr['object_count']} objects and {wr['camera_count']} cameras compared. Geometry, transforms, visibility, and other serialized scene state match exactly after exempting intentional material replacements. Unexpected differences: {len(unexpected)}.\n\n"
text+=f"Full-scene scan: {contact['results']['C25_v1']['scanned_pair_count']} panel/frame versus non-chair pairs per model, including hidden geometry. No numerical surface intersections or sampled containment were found in either C23 or C25 v1. Therefore no new room/sofa collisions were found. AABB-overlapping pairs were further tested with BVH, triangle narrow phase and three-direction parity probes. This is bounded numerical evidence, not exact certification.\n"
text+='\n## Fixed composite left-return comparison\n\n'
text+='C23 ownership is fixed to the panel for the first six source records (y=906–1020), and the left support for the last two (y=1048/1070). C25 v1 ownership is fixed to the continuous left frame/support for all eight. This is a declared construction ledger, with no per-point best-object selection. The per-object diagnostics above remain valid; their unequal visible coverage must not be compared as if they scored the same eight points.\n\n'
text+='| Original source point | C23 owner | C23 error px | C25 v1 owner | C25 v1 error px |\n|---|---|---:|---|---:|\n'
for i,r in enumerate(rows):text+=f"| {r['source_xy']} | {'panel'if i<6 else'left support'} | {r['C23_absolute_x_error_px']:.3f} | left frame/support | {r['C25_v1_absolute_x_error_px']:.3f} |\n"
text+=f"\nAll 8/8 points are geometrically visible under this ledger. C23 RMS/max: {composite['C23']['rms_px']:.3f}/{composite['C23']['max_px']:.3f} px, {composite['C23']['within_3px_count']}/8 within 3 px. C25 v1 RMS/max: {composite['C25_v1']['rms_px']:.3f}/{composite['C25_v1']['max_px']:.3f} px, {composite['C25_v1']['within_3px_count']}/8 within 3 px. Both fail the unchanged source tolerance.\n"
(O/'C25_v1_INDEPENDENT_REVIEW.md').write_text(text)
print(json.dumps({'white':wr,'composite_C23':composite['C23'],'composite_C25_v1':composite['C25_v1'],'nonchair_collision_scan':comparison['fullscene_nonchair_contacts']},ensure_ascii=False,indent=2))
