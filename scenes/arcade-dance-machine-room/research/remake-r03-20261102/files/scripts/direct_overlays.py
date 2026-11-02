from pathlib import Path
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parents[1];out=[]
for label,t,cam in [('old_front','2490.12261','SRC_front'),('old_oblique','2560.58535','SRC_oblique'),('new_front_UNCALIBRATED','2490.361500','SRC_front'),('new_oblique_UNCALIBRATED','2560.507406','SRC_oblique')]:
 src=next((D/'sources').glob('*'+t+'*'));a=Image.open(src).convert('RGB')
 for kind in ['material','white']:
  render=D/f'renders/R02_delivery_{kind}_{cam}.png'
  if not render.exists():continue
  b=Image.open(render).convert('RGB');assert a.size==b.size==(1920,1080)
  path=D/f'renders/R02_{label}_{kind}_direct50.png';Image.blend(a,b,.5).save(path)
  out.append({'output':str(path.relative_to(D)),'source':str(src.relative_to(D)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render':str(render.relative_to(D)),'render_sha256':hashlib.sha256(render.read_bytes()).hexdigest(),'formula':'0.5 original RGB + 0.5 render RGB; no warp, crop or resize','status':'FAIL uncalibrated hypothesis. New source time overlays are diagnostic only, not a newly fitted camera.'})
(D/'qa/direct_overlay_manifest.json').write_text(json.dumps(out,indent=2))
