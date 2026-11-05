from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parents[1];out=P/'renders/R06-comparisons';out.mkdir(exist_ok=True);box=(650,315,855,430);rec=[]
for mode in ['material','white']:
 paths=[P/'renders'/v/f'{mode}_MANNEQUIN_local.png' for v in ['R05','R06']];ims=[Image.open(p).convert('RGB').crop(box) for p in paths];dst=Image.new('RGB',(ims[0].width*2,ims[0].height));dst.paste(ims[0],(0,0));dst.paste(ims[1],(ims[0].width,0));f=out/f'{mode}_hip_same_pixel_before_after.png';dst.save(f);rec.append({'output':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'sources':[{'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'crop_box':box,'order':['R05 failed','R06 candidate'],'method':'same native pixels, no resizing or image retouch; diagnostic angle not source registration'})
(P/'qa/R06-crop-records.json').write_text(json.dumps(rec,indent=2))
