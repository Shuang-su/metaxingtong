from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parents[1];source=D/'sources/BV1dh8t6SEog_16.241415_4k.png';src=Image.open(source).convert('RGB');a=np.asarray(src,dtype=np.uint16);report={'native_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'size':[3840,2160],'source_resized_or_warped':False,'model':'FR04b face-winding-corrected material/white','source_condition':'f4000 fixed illustrative circle training, NOT calibration; scene radial mismatch FAIL','native_samples':4,'denoise':False,'exposure':-1.3,'results':{}}
for typ in ['material','white']:
 r=D/f'renders/FR04b_AUG23_native4k_{typ}.png';im=Image.open(r).convert('RGB');assert im.size==src.size==(3840,2160);o=D/f'renders/FR04b_AUG23_native4k_{typ}_direct50.png';Image.blend(src,im,.5).save(o);b=np.asarray(im,dtype=np.uint16);c=np.asarray(Image.open(o),dtype=np.uint16);delta=np.abs(c.astype('int32')-((a+b)//2).astype('int32'));report['results'][typ]={'pixel_count':int(a.shape[0]*a.shape[1]),'formula':'floor((sourceRGB+renderRGB)/2)','max_error':int(delta.max()),'mismatch_channels':int(np.count_nonzero(delta)),'render_sha256':hashlib.sha256(r.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(o.read_bytes()).hexdigest()}
 contact=Image.new('RGB',(1280,360))
 for i in range(8):q=Image.open(D/f'renders/FR04b_CHECK{i}_{typ}.png').resize((320,180));contact.paste(q,((i%4)*320,(i//4)*180))
 contact.save(D/f'renders/FR04b_{typ}_8angle_contact.png')
(D/'qa/FR04b-native-direct50-full-pixel-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
