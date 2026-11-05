import json,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent;mode=sys.argv[1]if len(sys.argv)>1 else 'white';rs=json.load(open(P/'renders/R04D_checks/render-log.json'));manifest=json.load(open(P.parent/'butterfly-finite-r04d-early-20261105-manifest.json'));frozen={r['path']:r['sha256']for r in manifest['files']};out=[]
for r in rs:
 if mode!='all'and r['material_mode']!=mode:continue
 f=P/r['file'];im=Image.open(f);im.load();a=np.array(im);modelhash=hashlib.sha256((P/r['input']).read_bytes()).hexdigest();out.append({'file':r['file'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'shape':list(a.shape),'alpha_range':[int(a[:,:,3].min()),int(a[:,:,3].max())],'model_sha':modelhash,'model_matches_render_postcompletion_hash':modelhash==r['input_sha256'],'model_matches_prerender_freeze_manifest':modelhash==frozen[r['input']],'samples':r['samples'],'percentage':r['percentage'],'camera':r['camera'],'scope':'Input SHA sampled after each completed render; freeze manifest supplies separate earlier binding, not a pre-load hash attestation.'})
(O/f'{mode}-formal-integrity.json').write_text(json.dumps(out,indent=2));print(len(out),'images',all(r['model_matches_render_postcompletion_hash']and r['model_matches_prerender_freeze_manifest']for r in out))
