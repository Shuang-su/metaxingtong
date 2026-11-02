from PIL import Image
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1];o=r/'versions/R01C';pairs=[('source4k','BV1gttHeGE9Z_53.951826_4k.png'),('front','BV15e4deGE1R_144.009018_1080high.png'),('oblique','BV15e4deGE1R_60.010322_1080high.png')];rows=[]
for n,s in pairs:
 sp=r/'sources'/s;src=Image.open(sp).convert('RGB');ren=Image.open(o/(n+'-low-material.png')).convert('RGB');out=o/(n+'-direct50-derived960.png');Image.blend(src.resize(ren.size,Image.Resampling.LANCZOS),ren,.5).save(out);rows.append({'view':n,'source':s,'source_native':src.size,'source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'display_size':ren.size,'resize':'Lanczos source only','mix':'.5 direct blend, no warp; low diagnostic not native formal overlay','output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(o/'overlay-provenance.json').write_text(json.dumps(rows,indent=2))
