from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1];out=P/'renders/R08-comparisons';out.mkdir(exist_ok=True);source=P/'sources/report/15.png';s=np.array(Image.open(source).convert('RGB'),dtype=np.uint16);records=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for version in ['R07','R08']:
 for mode in ['material','white']:
  path=P/'renders/R08'/f'{version}_{mode}_SOURCE15.png';r=np.array(Image.open(path).convert('RGB'),dtype=np.uint16);a=((s+r)//2).astype(np.uint8);dest=out/f'{version}_{mode}_SOURCE15_direct50.png';Image.fromarray(a).save(dest);records.append({'source':str(source.relative_to(P)),'source_sha256':sha(source),'render':str(path.relative_to(P)),'render_sha256':sha(path),'overlay':str(dest.relative_to(P)),'overlay_sha256':sha(dest),'formula':'floor((source_RGB+render_RGB)/2), original1192x671 no transform','max_error':int(np.abs(np.array(Image.open(dest)).astype(int)-a.astype(int)).max())})
(P/'qa/R08-overlay-records.json').write_text(json.dumps(records,indent=2))
