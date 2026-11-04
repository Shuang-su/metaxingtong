from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];im=Image.new('RGB',(1024,640),(27,25,22));d=ImageDraw.Draw(im)
# Explicit diagrammatic regions, not a photograph, scan, readable dial, or grille geometry.
d.rectangle((20,20,1003,619),outline=(90,83,69),width=9)
d.rectangle((52,106,498,570),fill=(15,17,17),outline=(54,52,46),width=7)
d.line((520,88,520,575),fill=(75,69,57),width=6)
d.rectangle((553,80,858,213),fill=(58,53,43),outline=(100,91,71),width=7)
f=P/'textures/R11_device_front_proxy.png';im.save(f)
(P/'qa/R11-texture-method.json').write_text(json.dumps({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':[1024,640],'method':'Pillow RGB flat regions, deterministic manual proxy, no source pixels copied or photogrammetry. Outer bezel, left grille category, divider and horizontal dial region only. No invented readable labels, weave slots or third knob.','limits':'Diagrammatic appearance only; exact spacing/physical color uncalibrated; it does not represent recessed geometry or solve old bottle-body intersections.'},indent=2))
