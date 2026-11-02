from PIL import Image
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1];src=r/'sources/BV1gttHeGE9Z_53.951826_4k.png';ren=r/'versions/R01A/platform-fit-material-960.png';out=r/'versions/R01A/platform-fit-direct50-derived960.png'
a=Image.open(src).convert('RGB').resize((960,540),Image.Resampling.LANCZOS);b=Image.open(ren).convert('RGB');Image.blend(a,b,.5).save(out)
(r/'versions/R01A/overlay-provenance.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_native':[3840,2160],'display_resize':'Lanczos to960x540 only for rapid conditional diagnostic','render_size':[960,540],'mix':'direct 0.5 source resized +0.5 actual render; no warp/translation','not_native_overlay':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
