from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[2];P=R/'c29';manifest=json.load(open(P/'render_manifest.json'));assert len(manifest['renders'])==5
checks=[]
for a in json.load(open(P/'renders/direct50_manifest.json')):
 src=np.asarray(Image.open(R/'inputs'/a['source']).convert('RGB'),dtype=np.uint16);ren=np.asarray(Image.open(P/'renders'/a['render']).convert('RGB'),dtype=np.uint16);ov=np.asarray(Image.open(P/'renders'/a['overlay']).convert('RGB'));assert np.array_equal((src+ren)//2,ov);checks.append({'file':a['render'],'dimensions':list(ov.shape),'direct50_exact':True})
assert len(checks)==5
out={'scope':'C29 local curtain frequency candidate, not calibrated room acceptance','final_images':checks,'geometry_checks':['actual exported 65 front/back cross sections: no crossings','independent closed450-edge sections including endpoint and collinear contacts: no crossings','29250 vertices,29248 faces,58496 edges; all edge incidences2','all recorded non-curtain scene and camera state unchanged','H/G/N642/665 full-row projected convex bounds unchanged; not all-pixel invariant'], 'visual_review':'Full H/G material and H white inspected; lower sampling noise and bright inherited white lighting remain. Interior folds less dense, left phase and right return errors remain. Top connection remains unverified. G white inspected separately before delivery.', 'thickness_caveat':'Back shell reconstructed; paired thickness not normal thickness, 0.00254 to0.01862 LOCAL units, world scale1.25, no metric calibration','photometric':json.load(open(P/'final_photometric_metrics.json')),'validation665':json.load(open(P/'validation665_metrics.json')),'blind_test':False,'failed_trials':'All TEST models rejected; retain for actual reproducibility, not deliverable candidates'}
(P/'QA_C29.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('5 full renders and exact overlays verified')
