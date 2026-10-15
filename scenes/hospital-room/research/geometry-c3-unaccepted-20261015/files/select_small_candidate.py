import json,numpy as np
from pathlib import Path
R=Path(__file__).parent
text=(R/'fit_local_candidate.py').read_text();exec(text[:text.index('sol=least_squares(fun')])
old=json.load(open(R/'local_fit_candidate.json'));cams['N640']=json.load(open(R/'N640_relative_camera.json'))['camera'];q=np.r_[old['geometry_parameters'][names[0]],[0,0,0]]
res={'status':'CONDITIONAL_SMALL_STEP_CANDIDATE_NOT_ACCEPTED','base':'D','name':'C2','geometry_parameters':{n:q[3*i:3*i+3].tolist() for i,n in enumerate(names)},'cameras':cams,'rejected_experiments':{'right_cushion':'unconstrained six-parameter fit drove right cushion X to -0.08 bound; rejected rather than applying it','N640_vertical_lines_only_camera':'rejected as underconstrained; furniture residual ~49 px and no independent pitch constraint'},'N640_camera_method':'static image correspondence camera rotation/focal fit; no source/render warp; see N640_relative_camera.json','branches':[]}
for br in records:
 b=residual_record(br,np.zeros(6));a=residual_record(br,q);res['branches'].append({'branch_id':br['branch_id'],'mesh':br['mesh_name'],'frame':br['frame'],'branch':br['contour_branch'],'source_uncertainty_px':br['uncertainty_px'],'excluded_rounded_transition_samples':br['excluded_samples'],'before':b,'after':a})
for frame in ['G','H','N640']:
 for mode in ['before','after']:
  v=[t['residual'] for b in res['branches'] if b['frame']==frame for t in b[mode] if t['residual'] is not None];print(frame,mode,'MAE',np.mean(np.abs(v)),'max',np.max(np.abs(v)))
(R/'C2_selected_parameters.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
