from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
R=Path(__file__).parent;O=R/'diagnostic_outputs'; src={x['view']:Path(x['file']) for x in json.load(open(R/'source_recovery_checks.json'))};checks=[]
for e in json.load(open(O/'render_manifest.json')):
 p=O/e['file']
 if not p.exists():continue
 a=np.asarray(Image.open(src[e['view']]).convert('RGB'),dtype=np.uint16);b=np.asarray(Image.open(p).convert('RGB'),dtype=np.uint16);assert a.shape==b.shape==(1080,1920,3)
 z=((a+b)//2).astype(np.uint8);f=O/(p.stem+'_source_direct50_UNREGISTERED.png');Image.fromarray(z).save(f);got=np.asarray(Image.open(f))
 checks.append({'file':f.name,'source_view':e['view'],'source_sha256':hashlib.sha256(src[e['view']].read_bytes()).hexdigest(),'render_file':p.name,'render_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'dimensions':[1920,1080],'formula':'floor((source uint16 + raw_render uint16)/2)','pixels_equal':bool(np.array_equal(z,got)),'max_pixel_error':int(abs(z.astype(np.int16)-got.astype(np.int16)).max()),'resized':False,'cropped':False,'registered':False,'warped':False,'source_edited':False,'candidate_status':'REJECTED_DIAGNOSTIC'})
(O/'direct50_pixel_checks.json').write_text(json.dumps(checks,indent=2));print(len(checks),'native direct overlays verified')
