from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
V={}
files={'A':'A2_clean_HD_viewport.jpg','B':'B2_clean_HD_viewport.jpg','D':'D2_clean_HD_viewport.jpg','F':'F_endwall_performance_HD_viewport.jpg','H':'H_clean_side_aisle_HD_viewport.jpg','I':'I_warm_endwall_HD_viewport.jpg','J':'J_final_side_luggage_HD_viewport.jpg'}
for k,f in files.items():V[k]={'source_file':f,'crop':[0,27,1180,691],'points':[],'lines':[],'notes':[]}
def point(v,n,p,q,split='fit',sigma=3):V[v]['points'].append(dict(name=n,world=p,source=[q[0],q[1]-27],split=split,sigma_px=sigma))
def line(v,n,x,z,qs,split='check',sigma=4):V[v]['lines'].append(dict(name=n,world=[[x,-4,z],[x,5.3,z]],source=[[q[0],q[1]-27] for q in qs],split=split,sigma_px=sigma))
# Endwall landmarks all refer to rigid OUTER sign housing, not luminous text or the dark glazing.
# World dimensions are candidate coordinates, not measurements of source.
for v,top,bot,door in [
 ('A',[(618,405),(687,404)],[(618,417),(687,416)],[(616,422),(693,420)]),
 ('D',[(742,318),(813,318)],[(742,331),(813,331)],[(740,335),(819,334)]),
 ('H',[(994,124),(1078,123)],[(994,139),(1078,137)],[(986,145),(1084,143)]),
 ('I',[(478,139),(716,138)],[(478,185),(716,184)],[(465,201),(729,201)]),
 ('F',[(486,92),(660,93)],[(486,126),(660,127)],[(477,137),(669,137)])]:
 for j,s in enumerate([-1,1]):
  point(v,'sign_outer_top_'+str(s),[s*.445,5.4345,2.545],top[j])
  point(v,'sign_outer_bottom_'+str(s),[s*.445,5.4345,2.405],bot[j],split='check')
  point(v,'jamb_outer_top_'+str(s),[s*.5,5.456,2.32],door[j])
for v,qs in {'A':{'left':[(182,28),(593,380)],'right':[(618,29),(695,377)]},'B':{'left':[(208,28),(447,293)],'right':[(510,28),(539,264)]},'D':{'left':[(493,28),(725,301)],'right':[(889,28),(818,297)]},'H':{'left':[(897,28),(995,111)],'right':[(1110,28),(1097,107)]},'I':{'left':[(408,28),(439,98)],'right':[(781,28),(762,98)]}}.items():
 for side,s in [('left',-1),('right',1)]:line(v,'ceiling_'+side,s*.575,2.575,qs[side],split='fit',sigma=4)
for v,side,qs in [
 ('A',-1,[(26,309),(551,434)]),('A',1,[(1138,226),(756,435)]),
 ('D',-1,[(15,210),(682,352)]),('D',1,[(1154,209),(867,351)]),
 ('B',-1,[(15,220),(399,321)]),('B',1,[(908,29),(639,281)]),
 ('H',-1,[(258,91),(914,164)]),
 ('I',-1,[(20,150),(277,255)]),('I',1,[(1159,152),(927,245)]),
 ('F',-1,[(52,43),(333,172)]),('F',1,[(1155,52),(811,175)])]:line(v,'rack_inner_'+str(side),side*.88,2.19,qs)
# Rounded frame extrema, not nonexistent sharp glass corners. Some remain occluded and are omitted.
for v,pairs in {'D':[('top',[0,5.448,2.10],[777,354]),('bottom',[0,5.448,1.26],[777,422]),('left',[-.275,5.448,1.68],[755,387]),('right',[.275,5.448,1.68],[799,386])], 'A':[('top',[0,5.448,2.10],[652,440]),('right',[.275,5.448,1.68],[676,475])], 'H':[('top',[0,5.448,2.10],[1032,165]),('bottom',[0,5.448,1.26],[1030,238]),('left',[-.275,5.448,1.68],[1005,201]),('right',[.275,5.448,1.68],[1057,199])], 'F':[('top',[0,5.448,2.10],[572,184]),('left',[-.275,5.448,1.68],[521,266])], 'I':[('left',[-.275,5.448,1.68],[521,380]) ]}.items():
 for n,p,q in pairs:point(v,'door_frame_'+n,p,q,'check',4)
# Previous lamp/seat correspondences are now CHECK ONLY, never used to assert longitudinal scale.
old=R.parent/'analysis'
for v in ['A','B','D']:
 d=json.loads((old/f'{v}_camera_fit.json').read_text())
 for p in d['landmarks']:
  if p['name'].startswith('round') or p['name'] in ['nearR','midR']:
   V[v]['points'].append(dict(name='legacy_hypothesis_'+p['name'],world=p['world'],source=p['source'],split='check',sigma_px=6,identity='lamp index / seat bay provisional'))
V['B']['notes']=['Endwall and lower structure occluded by performer and near seat. Roof lines alone insufficient for unique camera; no structure fitting from B alone.']
V['F']['notes']=['No usable long central ceiling edges. Door plane only; focal/depth ambiguous. Performance lighting excluded from geometry constraints.']
V['I']['notes']=['Short ceiling edges are weak focal constraint; performer occludes frame and floor; outer door bottom unavailable.']
V['J']['notes']=['Prior glass-corner annotation withdrawn: curtain edges and person conceal actual aperture. Bay and side correspondence unresolved. No aperture optimization allowed. Visible horizontal sash/sill can support future plane rectification only.']
for v in V:V[v]['notes']+=['Pixel picks manually estimated on the original 1180x757 screenshot; source y minus27. No claim of subpixel precision.','No full door four-corner quadrilateral visible with confidence; bottom corners are omitted rather than fabricated.']
(R/'analysis/constraints.json').write_text(json.dumps(V,indent=2,ensure_ascii=False))
print({k:(len(x['points']),len(x['lines'])) for k,x in V.items()})
