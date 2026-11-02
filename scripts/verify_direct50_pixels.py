from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parents[1];f=D/'sources/native-nov2/BV1mT411V72s_1842.088867_4k.png';a=np.asarray(Image.open(f).convert('RGB'),dtype=np.uint16);r={'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_size':[a.shape[1],a.shape[0]],'formula':'floor((source_uint16+render_uint16)/2), every RGB channel every pixel','results':{}}
for typ in ['material','white']:
 b=np.asarray(Image.open(D/f'renders/NOV2_CP02_near_bay_{typ}_native4k.png').convert('RGB'),dtype=np.uint16);c=np.asarray(Image.open(D/f'renders/NOV2_CP02_near_bay_{typ}_native4k_direct50.png').convert('RGB'),dtype=np.uint16);expected=(a+b)//2;delta=np.abs(c.astype('int32')-expected.astype('int32'));r['results'][typ]={'equal_all_pixels_all_rgb':bool(np.all(delta==0)),'max_channel_error':int(delta.max()),'mismatch_channel_count':int(np.count_nonzero(delta)),'tested_pixels':int(a.shape[0]*a.shape[1])}
(D/'qa/native4k-direct50-full-pixel-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
