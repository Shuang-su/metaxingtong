from pathlib import Path
from PIL import Image
import json,hashlib,re
root=Path(__file__).resolve().parents[1];r=root/'versions/R06';rows=[]
for d in ['renders','comparisons']:
 for p in sorted((r/d).glob('*.png')):
  n=p.stem;role='diagnostic derivative';source=None;inspection=None
  if 'source' in n:
   m=re.search(r'source(17|20|21)',n)
   if m:source=int(m.group(1))
  if 'inspection-' in n:
   m=re.search(r'inspection-(\d+)',n)
   if m:inspection=int(m.group(1))
  if d=='renders':role='model inspection render' if inspection else 'conditional source-camera render'
  if 'direct50' in n:role='direct 50% same-grid overlay, no warp/mask'
  elif 'source-render-overlay' in n:role='unscaled left-to-right source/render/direct50 strip'
  if n.startswith('crop-'):role='source-coordinate crop strip; not independent source baseline'
  if 'contact' in n:role='50%-scaled 8-model-angle contact sheet; not source angles'
  if n=='main-material':role='normal main image; byte-identical alias of material inspection-05, not source camera';inspection=5
  with Image.open(p) as im:size=im.size
  rows.append({'path':str(p.relative_to(root)),'role':role,'source_id':source,'model_inspection_id':inspection,'variant':'white' if 'white' in n else 'material','dimensions':size,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'docs/image-role-manifest.json').write_text(json.dumps({'model_commit':'130b5632b838729af6b97059849972d60640b924','source_baselines':'17 near frontal;20 low angle;21 high; not 8 source views','images':rows},indent=2))
print(len(rows),'image-role records')
