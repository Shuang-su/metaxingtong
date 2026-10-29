from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'c31';a=json.load(open(P/'build_verification.json'));m=json.load(open(P/'render_manifest.json'));assert len(m['renders'])==4
geo={}
for k,v in a.items():
 for n,c in v['changes'].items():
  for side in ['min','max']:
   assert max(abs(c['before'][side][i]-c['after'][side][i]) for i in [0,1])<1e-6
  h=c['after']['max'][2]-c['after']['min'][2];center=(c['after']['max'][2]+c['after']['min'][2])/2;assert abs(h/v['aperture_height']-c['target_height_over_hole_height'])<1e-5;assert abs(center-v['aperture_center_z'])<1e-6
  assert v['before_state'][n]['faces_sha256']==v['after_state'][n]['faces_sha256']
 geo[k]={'only_two_expected_meshes_changed':v['changed_objects'],'x_y_bounds_and_topology_preserved':True,'relative_target_heights_confirmed':True,'reopen_equal':v['reopen_equal']}
rows=json.load(open(P/'renders/direct50_manifest.json'));assert len(rows)==4
for v in rows:
 x=np.asarray(Image.open(R/v['source']).convert('RGB'),dtype=np.uint16);y=np.asarray(Image.open(P/'renders'/v['render']).convert('RGB'),dtype=np.uint16);z=np.asarray(Image.open(P/'renders'/v['direct50']).convert('RGB'));assert x.shape==y.shape==z.shape==(1080,1920,3);assert np.array_equal((x+y)//2,z)
out={'version':'C31 central recess conditional candidate from C29','geometry':geo,'four_full_1920x1080_renders':m,'four_exact_50_percent_overlays':True,'same_column_actual_full_G_pixels':json.load(open(P/'full_G_pixel_check.json')),'review':'Independent region review supports local improvement, not exact pixel match; full material G observed transitions match region values. Full H/G white/material visually checked before delivery.','limits':['1801/1804 are uncalibrated proportional evidence, not full camera calibration','G is partial-slot fixed-camera check; H/665 cannot validate a slot they do not show','outer top lip not reliably measurable; no invented external height score','C30/C30B remain rejected; bed geometry still C29','16-sample noise and bright white lighting inherited; no retouching','no authenticated remote push']};(P/'QA_C31.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('C31 full-image, exact-overlay, geometry invariants verified')
