from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parents[1];O=P/'renders/R12-comparisons';O.mkdir(exist_ok=True);box=(120,280,600,671);rec=[]
for mode in ['material','white']:
 ps=[P/'renders/R12'/f'{v}_{mode}_TABLE_high.png' for v in ['R11','R12']];cs=[Image.open(p).convert('RGB').crop(box) for p in ps];im=Image.new('RGB',(480,782));im.paste(cs[0],(0,0));im.paste(cs[1],(0,391));f=O/f'{mode}_left_cluster_same_pixel_before_after.png';im.save(f);rec.append({'output':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'sources':[{'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in ps],'crop_box':box,'order':'top R11 baseline; bottom R12 XY-only candidate','scope':'exact same pixels without scale/retouch; not source registration; nearest bottles are cropped by original camera so cannot visually count all nine'})
(P/'qa/R12-crop-records.json').write_text(json.dumps(rec,indent=2))
