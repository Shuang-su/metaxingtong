from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parents[1];out=P/'renders/R08-comparisons';out.mkdir(exist_ok=True);box=(180,390,1030,520);rec=[]
for mode in ['material','white']:
 paths=[P/'renders/R08'/f'{v}_{mode}_DIAG_bottle_mount.png' for v in ['R07','R08']];ims=[Image.open(p).convert('RGB').crop(box) for p in paths];dst=Image.new('RGB',(ims[0].width,ims[0].height*2));dst.paste(ims[0],(0,0));dst.paste(ims[1],(0,ims[0].height));f=out/f'{mode}_bottle_mount_same_pixel_before_after.png';dst.save(f);rec.append({'output':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'sources':[{'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'crop_box':box,'order':['top R07 baseline','bottom R08 candidate'],'method':'same original pixels, no rescaling or retouch; not source registration'})
(P/'qa/R08-crop-records.json').write_text(json.dumps(rec,indent=2))
