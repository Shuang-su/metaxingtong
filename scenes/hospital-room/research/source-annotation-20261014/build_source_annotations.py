"""Source-only semantic branches. No projection, camera fitting, model edit or render."""
from pathlib import Path
import json,hashlib,os
from PIL import Image
R=Path(__file__).parent;W=R.parent;old=W/'hospital_anchor_preparation_20261014/restored'
source_paths={'N640':W/'hospital_expanded_video_20261014_0315/native_frames/BV1GqXMByE1s_640.406589_empty_hospital_native.png','H':old/'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','G':old/'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png'}
times={'N640':640.406589,'H':1101.728114,'G':1116.180816}
expected={'N640':'9f56d9774d8745b832917a3923b43a24a99488e5eee2cc443161edf0b4c3e79c','H':'129345eb1e17ff78b3c20e86c9bbfb301730f2c660036b52168ae2214db4fd48','G':'5df9bc480c81c8fbcb8ea0ee7292c4799c8106cf5a0d231264215b276e432474'}
frames={};checks=[];(R/'source_views').mkdir(exist_ok=True)
for k,p in source_paths.items():
 data=p.read_bytes();sha=hashlib.sha256(data).hexdigest()
 with Image.open(p) as im:im.load();size=im.size;mode=im.mode
 assert sha==expected[k] and size==(1920,1080)
 frames[k]={'frame_id':k,'source_sha256':sha,'source_filename':p.name,'actual_dimensions':{'width_px':1920,'height_px':1080},'coordinate_transform':'none','native_decode_status':'native_decoded','pixel_coordinate_convention':'top_left_x_right_y_down'}
 dest=R/'source_views'/p.name
 if not dest.exists():os.link(p,dest)
 checks.append({'frame':k,'seconds':times[k],'source_bv':'BV1GqXMByE1s','sha256':sha,'dimensions':list(size),'mode':mode,'full_png_decode_passed':True,'original_file_unchanged':True})
branches=[]
def add(frame,obj,part,branch,points,uncertainty=4,identity='verified',note='',legacy=None):
 branches.append({'branch_id':f'{frame}:{obj}:{part}:{branch}','frame':frame,'object_id':obj,'semantic_part':part,'contour_branch':branch,'source_points':points,'uncertainty_px':uncertainty,'source_identity_state':identity,'visibility':'visible','geometry_use_allowed':False,'same_3d_points_across_views':False,'candidate_instance_across_times':'conditional_only','note':note,'legacy_source_id':legacy})
# New native frame: uppermost exterior boundaries, not the stronger inner dark line of bright upholstery piping.
add('N640','sofa_back_left','backrest_outer','upper',[[900,765],[950,762],[1000,758],[1050,755],[1100,754],[1150,753],[1200,752]],4,note='Outer skyline of the left cushion; bright piping creates a second stronger inner gradient 3–8px lower. Sample positions are not material vertices.')
add('N640','sofa_back_left','backrest_outer','left',[[880,787],[883,817],[890,850],[896,870]],5,note='Short exterior side above left arm; do not extend below arm overlap.')
add('N640','sofa_back_right','backrest_outer','upper',[[1250,754],[1300,749],[1350,746],[1400,745],[1450,743],[1500,742]],4,note='Separate right cushion. Do not bridge the center cushion notch or use the dark diagonal seam.')
add('N640','sofa_back_right','backrest_outer','right',[[1515,752],[1522,771],[1536,803],[1548,824]],5,note='Ends where the arm overlaps. Not a physical rectangular corner chain.')
add('N640','sofa_arm_right','arm_exterior_to_background','upper',[[1560,825],[1600,829],[1650,833],[1700,838],[1750,842],[1800,846],[1830,848]],4,note='Against window/gray-fold background; this is an exterior edge, unlike highlights on the left arm.')
add('N640','sofa_arm_right','arm_exterior_to_background','right',[[1854,860],[1859,900],[1863,940],[1865,960]],6,note='Stop before pale foreground bedding occludes the bottom; rounded shoulder split from upper branch.')
add('N640','sofa_arm_left','short_rear_upper_run','upper',[[847,869],[858,869],[870,871],[882,882]],6,identity='conditional',note='Only short exposed run between chair and backrest. Chair hides left/front boundary; attribution at cushion/arm junction still conditional. Never expand this into the sunlight patch.')
add('N640','chair_back_assembly','backrest_outer','upper',[[450,867],[475,861],[500,856],[550,851],[600,846],[650,842],[700,839],[750,839],[800,839],[825,841]],4,note='Green chair upper silhouette; curved corners are omitted, no rectangular-corner inference.')
add('N640','chair_back_assembly','backrest_outer','right',[[842,875],[841,900],[834,925],[828,940],[823,950]],4,note='Chair occludes the sofa behind it. Do not use this as a sofa contour.')
add('N640','chair_back_assembly','backrest_outer','left',[[420,895],[420,910],[412,930],[412,950],[412,975]],6,note='Exterior of assembly including narrow side support; panel-to-support seam is not separately identified.')
add('N640','chair_back_panel','panel_bottom_to_visible_background','lower',[[475,1009],[500,1003],[550,993],[600,984],[650,977],[700,970],[750,963],[790,958]],4,note='Bottom edge of green back panel, with background below. Excludes chair uprights at its ends; not sofa lower edge.')
# H: retain reviewed branch subsets of old native annotations, without restoring withdrawn arm metrics.
add('H','sofa_back_left','backrest_outer','upper',[[882,804],[963,798],[1080,795],[1196,793]],5,legacy='H_sofa_back_upper_and_right_outer',note='Explicit left-cushion upper subset; old compound curve is not reused whole.')
add('H','sofa_back_left','backrest_outer','left',[[855,824],[859,847],[862,868]],5,legacy='H_sofa_back_upper_and_right_outer',note='Stop before green-chair occlusion; no inferred lower continuation.')
add('H','sofa_back_right','backrest_outer','upper',[[1228,798],[1332,791],[1440,787],[1481,788]],5,legacy='H_sofa_back_upper_and_right_outer',note='Separate right cushion, not whole sofa hull.')
add('H','sofa_back_right','backrest_outer','right',[[1493,793],[1506,826],[1527,867]],5,legacy='H_sofa_back_upper_and_right_outer')
add('H','sofa_arm_right','arm_exterior_to_background','upper',[[1527,868],[1612,876],[1723,884],[1806,889]],5,legacy='H_sofa_right_arm_visible_outer')
add('H','sofa_arm_right','arm_exterior_to_background','right',[[1840,918],[1842,958],[1844,1000]],6,note='Rounded corner and mattress occlusion excluded. No arm-depth metric asserted.')
add('H','chair_back_assembly','backrest_outer','upper',[[475,891],[500,885],[550,878],[600,874],[650,870],[700,868],[750,868],[800,867],[850,868]],4,note='New explicit chair branch review of the old H native source.')
add('H','chair_back_assembly','backrest_outer','right',[[873,900],[872,925],[868,940],[866,950],[863,960],[856,975],[851,985]],5,note='Ends before lower panel/support junction.')
add('H','chair_back_panel','panel_bottom_to_visible_background','lower',[[475,1052],[500,1043],[550,1032],[600,1022],[650,1014],[700,1008],[750,1001],[790,995],[810,992]],5,note='Panel bottom only. Chair upright silhouettes and pale foreground bedding are different boundaries.')
# G: visible fragments only. Person masks the middle; absence is not zero error.
add('G','sofa_back_left','backrest_outer','upper',[[227,894],[309,885],[422,879],[528,875],[588,877]],5,legacy='G_sofa_left_back_outer_visible',note='No continuation into x604–803 person occlusion; left rounding separated.')
add('G','sofa_back_left','backrest_outer','left',[[196,916],[205,977],[217,1025]],5,legacy='G_sofa_left_back_outer_visible')
add('G','sofa_back_right','backrest_outer','upper',[[802,868],[839,864],[868,866]],5,legacy='G_sofa_right_back_outer_visible',note='Only small right-side fragment is exposed; it is not homologous point-for-point with H/N640 samples.')
add('G','sofa_back_right','backrest_outer','right',[[879,870],[893,916],[908,966]],5,legacy='G_sofa_right_back_outer_visible')
add('G','sofa_arm_right','arm_exterior_to_background','upper',[[907,941],[972,946],[1070,951],[1149,955]],5,legacy='G_sofa_right_arm_upper_outer')
add('G','sofa_arm_right','arm_exterior_to_background','right',[[1163,975],[1164,1020],[1164,1065]],6,legacy='G_sofa_right_arm_upper_outer')
add('G','sofa_arm_left','short_rear_upper_run','upper',[[145,1014],[184,1020],[193,1030]],6,identity='conditional',legacy='G_sofa_left_arm_visible',note='Only short rear run; no reuse of withdrawn sunlight-contaminated front-arm group.')
add('G','chair_back_assembly','backrest_outer','upper',[[0,978],[50,978],[100,976],[132,976]],6,note='Mostly left-clipped chair: only a fragment, no inferred corners or panel bottom.')
add('G','chair_back_assembly','backrest_outer','right',[[142,991],[145,1006],[141,1030],[130,1053],[114,1077]],6,note='Image-local visible fragment; cannot assert sample-wise cross-frame correspondence.')
exclusions=[{'frame':'N640','object_id':'sofa_arm_left','sample_xy':[970,910],'reason':'Bright sunlight patch region, not a physical surface corner or external silhouette.'},{'frame':'H','object_id':'sofa_arm_left','sample_xy':[970,950],'reason':'Bright sunlight patch; old H arm aggregate withdrawn, not restored by this review.'},{'frame':'G','object_id':'sofa_arm_left','sample_xy':[302,1049],'reason':'Bright sunlight patch; old G front-arm aggregate withdrawn.'},{'frame':'all','object_id':'sofa','reason':'Central diagonal cushion seam and seat/back contact boundaries excluded from whole-object external envelope.'},{'frame':'N640','object_id':'bed_or_bedding_foreground','reason':'Only clipped pale foreground boundary is visible; no two mattress long sides, near/far endpoint ownership, pillow or rail joint. It cannot define a mattress footprint or patient-eye location.'}]
family={'sofa_back_left':'Sofa • reclined back cushion 1','sofa_back_right':'Sofa • reclined back cushion 2','sofa_arm_left':['Sofa • broad padded arm','Sofa • broad padded arm.001'],'sofa_arm_right':['Sofa • broad padded arm','Sofa • broad padded arm.001'],'chair_back_assembly':['Chair • narrow curved wraparound back','Chair • slim back support','Chair • slim back support.001'],'chair_back_panel':'Chair • narrow curved wraparound back'}
# Object names are only family candidates; never assign .001 to image-right by naming alone.
cat={'status':'SOURCE_ONLY_BRANCH_ANNOTATION_NO_FIT','frames':[{**f,'seconds':times[k],'source_bv':'BV1GqXMByE1s'} for k,f in frames.items()],'branches':branches,'exclusions':exclusions,'mesh_family_candidates':family,'camera_constraint_conclusion':'New furniture contour checks, not a new bed-eye anchor. H was already unoccluded. Cross-time camera/intrinsics/layout equality is unverified.','point_identity':'No named physical 3D vertices and no cross-frame point pairing are asserted.','source_annotation_policy':'Manual full-native review plus local RGB profiles. Record approximate border with 4–6px uncertainty; do not choose strongest inner piping/shading gradient as outer silhouette.','old_states':{'D':'NOT_ACCEPTED','J1':'REJECTED','H85px':'WITHDRAWN'}}
(R/'source_contour_branches_N640_G_H.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2))
obs=[]
for b in branches:
 for i,xy in enumerate(b['source_points']):
  obs.append({'observation_id':b['branch_id']+f':s{i}','source':frames[b['frame']],'object_id':b['object_id'],'semantic_part':b['semantic_part'],'contour_branch':b['contour_branch'],'evidence_kind':'silhouette','identity_state':b['source_identity_state'],'identity_evidence':'Image-space object/branch reviewed only. '+b['note'],'geometry_use_allowed':False,'source_xy':xy,'uncertainty_px':b['uncertainty_px'],'visibility':'visible','sample_order':i,'point_identity':{'state':'not_asserted','physical_point_id':None,'evidence':None}})
strict={'schema_version':'1.0','dataset_id':'N640_G_H_source_only_branch_review_20261014','dataset_kind':'real_observations','frames':list(frames.values()),'observations':obs,'projections':[],'comparisons':[]}
(R/'source_only_validator_input.json').write_text(json.dumps(strict,ensure_ascii=False,indent=2));(R/'source_checks.json').write_text(json.dumps({'sources':checks,'branches':len(branches),'point_observations':len(obs),'all_geometry_use_false':True,'no_projection_or_comparison_supplied':True},ensure_ascii=False,indent=2));print(len(branches),'branches',len(obs),'source-only points')
