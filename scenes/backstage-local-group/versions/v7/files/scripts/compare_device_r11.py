from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parents[1];O=P/'renders/R11-comparisons';O.mkdir(exist_ok=True);box=(130,130,1020,671);records=[]
for mode in ['material','white']:
 paths=[P/'renders/R10'/f'R09_{mode}_DIAG_device_front.png',P/'renders/R10'/f'R10_{mode}_DIAG_device_front.png',P/'renders/R11'/f'R11_{mode}_DIAG_device_front.png'];crops=[Image.open(p).convert('RGB').crop(box) for p in paths];board=Image.new('RGB',(890,541*3));
 for i,im in enumerate(crops):board.paste(im,(0,i*541))
 f=O/f'{mode}_R09_R10_R11_same_pixel_front.png';board.save(f);records.append({'output':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'sources':[{'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'crop_box':box,'order':'top R09 baseline, middle failed R10 physical panels, bottom R11 diagram on unchanged body surface','method':'same original pixels, no resizing/retouch; one artificial diagnostic camera, not source registration'})
(P/'qa/R11-crop-records.json').write_text(json.dumps(records,indent=2))
