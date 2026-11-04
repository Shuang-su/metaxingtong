import pathlib,json,hashlib,numpy as np
from PIL import Image
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-window-qa-20261104')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
R={'renders':[],'overlays':[]}
for x in json.loads((P/'qa/R09-render-records.json').read_text()):
 p=P/x['file'];R['renders'].append({'file':x['file'],'sha256':sha(p),'sha_match':sha(p)==x['sha256'],'bytes_match':p.stat().st_size==x['bytes'],'size':Image.open(p).size,'model_sha_match':sha(P/x['model'])==x['model_sha256'],'model_sha256':sha(P/x['model']),'samples_recorded':x['samples'],'denoise_recorded':x['denoise']})
for x in json.loads((P/'qa/R09-overlay-records.json').read_text()):
 a,b,c=[np.array(Image.open(P/x[k]).convert('RGB'))for k in ['source','render','overlay']];expected=((a.astype(np.uint16)+b.astype(np.uint16))//2).astype(np.uint8)
 R['overlays'].append({'file':x['overlay'],'sha256':sha(P/x['overlay']),'all_hashes_match':all(sha(P/x[k])==x[k+'_sha256']for k in ['source','render','overlay']),'same_dimensions':a.shape==b.shape==c.shape,'max_pixel_error':int(np.abs(c.astype(int)-expected.astype(int)).max()),'formula':'floor((source_RGB+render_RGB)/2)'})
R['render_count']=len(R['renders']);R['overlay_count']=len(R['overlays']);(Q/'R09-final-image-integrity.json').write_text(json.dumps(R,indent=2));print(R['render_count'],R['overlay_count'],all(x['sha_match']and x['bytes_match']and x['model_sha_match']for x in R['renders']),all(x['all_hashes_match']and x['max_pixel_error']==0 for x in R['overlays']))
