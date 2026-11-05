from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
O=Path(__file__).parent;P=O.parent/'backstage-pearl-r14-20261105';rs=json.load(open(P/'qa/R14-render-records.json'));out=[]
for r in rs:
 f=P/r['file'];a=np.array(Image.open(f));out.append({'file':r['file'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'hash_ok':hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],'bytes_ok':f.stat().st_size==r['bytes'],'shape':list(a.shape),'alpha_range':[int(a[:,:,3].min()),int(a[:,:,3].max())] if a.shape[2]==4 else None,'model_hash_ok':hashlib.sha256((P/r['model']).read_bytes()).hexdigest()==r['model_sha256']})
keys=['camera_matrix','camera_lens','camera_sensor_fit','camera_sensor_width','clip_start','resolution','samples','denoise','threads'];result={'images':out,'same_recorded_settings':{k:all(r[k]==rs[0][k] for r in rs) for k in keys},'render_script_sha':hashlib.sha256((P/'scripts/render_pearls_r14_resumed4.py').read_bytes()).hexdigest()};(O/'image-integrity.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
