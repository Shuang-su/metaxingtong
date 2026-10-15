"""Direct 50% sRGB byte blending at identical 1920x1080 pixels. No registration, crop, warp, resize or denoising."""
from PIL import Image
from pathlib import Path
import hashlib,json
R=Path(__file__).parent
sources={'G':R.parent/'hospital_anchor_preparation_20261014/restored/hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','H':R.parent/'hospital_anchor_preparation_20261014/restored/hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','F':R.parent/'hospital_anchor_preparation_20261014/restored/hospital-F-tv-BV1GqXMByE1s-t1823.678156-native.png','N640':R.parent/'hospital_empty_frame_annotation_20261014/source_views/BV1GqXMByE1s_640.406589_empty_hospital_native.png'}
rec=[]
for stage,directory in [('D','renders_D_baseline'),('C2','renders_C2'),('C3','renders_C3')]:
 for k,src in sources.items():
  raw=R/directory/f'{k}_{stage}_RAW_1920x1080.png'
  if not raw.exists():continue
  a=Image.open(src).convert('RGB');b=Image.open(raw).convert('RGB');assert a.size==b.size==(1920,1080);out=R/directory/f'{k}_{stage}_direct_50pct_overlay_1920x1080.png';Image.blend(a,b,.5).save(out)
  rec.append({'stage':stage,'view':k,'source':str(src.relative_to(R.parent)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_file':str(raw.relative_to(R)),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'overlay_file':str(out.relative_to(R)),'overlay_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':[1920,1080],'alpha':.5,'algorithm':'PIL.Image.blend RGB source * 0.5 + raw render * 0.5, 8-bit rounding','source_transform':'none','render_transform':'none'})
(R/'direct_overlay_manifest.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print('OVERLAYS',len(rec))
