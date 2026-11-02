from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parents[1];source=D/'sources/native-nov2/BV1mT411V72s_1842.088867_4k.png';src=Image.open(source).convert('RGB');files=[]
for typ in ['material','white']:
 f=D/f'renders/NOV2_CP02_near_bay_{typ}_native4k.png';im=Image.open(f).convert('RGB');assert im.size==src.size==(3840,2160);o=D/f'renders/NOV2_CP02_near_bay_{typ}_native4k_direct50.png';Image.blend(src,im,.5).save(o)
 for x in [f,o]:files.append({'file':str(x.relative_to(D)),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()})
(D/'qa/native4k-direct-overlay.json').write_text(json.dumps({'dimensions':[3840,2160],'source':str(source.relative_to(D)),'source_not_resampled':True,'source_not_warped':True,'render_native_dimensions':True,'method':'Pillow Image.blend(sourceRGB,renderRGB,0.5), integer rounding only','same_frozen_camera_and_mesh':True,'samples':4,'denoise':False,'status':'FAILED conditional alignment retained, not source acceptance','files':files},indent=2)+'\n')
