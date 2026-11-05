import json,hashlib,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent/'seaside-arch-local-panel-study-20261105';P=O.parent/'seaside-arch-candidate-20261105';own=json.loads((O/'check.json').read_text());scan=json.loads((R/'qa/scanline.json').read_text());out={'diagnosis_head':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),'scanline_max_diff':0,'files':[]}
for a in own['cases']:
 match=[r for r in scan['rows'] if r['shift_x']==a['dx']]
 if not match:continue
 for name,lines in a['scanlines'].items():
  for b in match[0]['objects'][name]['scanlines']:
   if lines[str(b['y'])] is None or b['model_bounds'] is None:
    assert lines[str(b['y'])] is None and b['model_bounds'] is None
    continue
   out['scanline_max_diff']=max(out['scanline_max_diff'],max(abs(x-y) for x,y in zip(lines[str(b['y'])],b['model_bounds'])))
for r in json.loads((R/'qa/final-originals-unchanged.json').read_text()):
 p=P/r['path'];h=hashlib.sha256(p.read_bytes()).hexdigest();out['files'].append({'path':r['path'],'sha256':h,'matches_frozen_record':h==r['sha256']})
assert all(r['matches_frozen_record'] for r in out['files'])
assert all(r['producer_hit_count_exact'] and r['producer_surface_pairs_exact'] for r in own['cases'])
(O/'comparison.json').write_text(json.dumps(out,indent=2));print(out['diagnosis_head'],out['scanline_max_diff'],len(out['files']))
