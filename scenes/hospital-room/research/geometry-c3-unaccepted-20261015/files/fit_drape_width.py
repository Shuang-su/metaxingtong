import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
R=Path(__file__).parent
text=(R/'diagnose_contours.py').read_text();exec(text[:text.index('out=[]\nfor k,n')])
cat=json.load(open(R.parent/'hospital_anchor_preparation_20261014/source_anchor_catalog.json'))
obs={a['frame']:a['source_points'] for a in cat['anchors'] if a['anchor_id'] in ['G:curtain_outer_right','H:curtain_outer_right','F:curtain_outer_right']}
# H y900 intersects sofa arm/background junction, not an unobstructed drape boundary.
# Keep it as an excluded legacy sample, do not drive a cloth fit with furniture pixels.
excluded={'H':[[1840,900]],'G':[[1151,100]]};obs['H']=[p for p in obs['H'] if p[1]<900];obs['G']=[p for p in obs['G'] if p[1]>100]
M=D['meshes']['Curtain • rebuilt uniform eight-fold drape'];V=np.array(M['vertices']);E=edges(M);cams={'G':D['cameras']['MATCH_G_Sofa_And_Bed'],'H':D['cameras']['MATCH_H'],'F':D['cameras']['MATCH_F_Turning_Right']}
xmin=V[:,0].min()
def vv(q,y):
 z=V.copy();z[:,0]=xmin+(z[:,0]-xmin)*q;z[:,1]+=y;return z

def records(q,y,k):return directed(project(vv(q,y),cams[k]),E,obs[k],1,'max')
def fun(q):return [t['residual']/3 for k in ['G','H'] for t in records(q[0],-.04011060774326324,k)]
sol=least_squares(fun,[1.],bounds=([.75],[1.1]),loss='soft_l1')
res={'status':'CONDITIONAL_DERIVED_FROM_VERIFIED_SOURCE_BRANCH_NEEDS_MODEL_VISIBILITY_CHECK','scale_x':float(sol.x[0]),'fixed_left_x':xmin,'global_y_delta':-.04011060774326324,'fit':['G','H'],'conditional_holdout':['F'],'excluded_legacy_samples':excluded,'views':{}}
for k in obs:
 res['views'][k]={'D':records(1,0,k),'P0':records(1,-.04011060774326324,k),'width_candidate':records(sol.x[0],-.04011060774326324,k)}
(R/'drape_width_screen.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print(json.dumps(res,ensure_ascii=False,indent=2))
