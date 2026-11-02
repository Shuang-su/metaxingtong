from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path('metaxingtong-lantern-full-remake-20261102');O=Path('review-lantern-full-rebuild-20261102')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with Image.open(p) as im:im.load();return np.array(im.convert('RGB')),list(im.size),im.mode
sp=R/'sources/BV1dh8t6SEog_16.241415_4k.png';S,sz,mode=read(sp);results=[]
for typ in ['material','white']:
 rp=R/f'renders/FR04b_AUG23_native4k_{typ}.png';op=R/f'renders/FR04b_AUG23_native4k_{typ}_direct50.png';a,asz,am=read(rp);b,bsz,bm=read(op);assert sz==asz==bsz==[3840,2160];expected=(S.astype(np.uint16)+a.astype(np.uint16))//2;delta=np.abs(b.astype(np.int16)-expected.astype(np.int16));results.append({'type':typ,'source_sha256':sha(sp),'render_sha256':sha(rp),'overlay_sha256':sha(op),'decoded_sizes':[sz,asz,bsz],'png_modes':[mode,am,bm],'formula':'floor((unchanged source RGB + unchanged render RGB)/2) on full native arrays, no resize/warp/crop','pixel_count':int(delta.shape[0]*delta.shape[1]),'channel_count':int(delta.size),'max_channel_error':int(delta.max()),'mismatch_channels':int(np.count_nonzero(delta)),'mismatch_pixels':int(np.count_nonzero(np.any(delta!=0,axis=2)))})
visuals=[]
paths=[R/f'renders/FR04b_CHECK{i}_{t}.png' for t in ['material','white'] for i in range(8)]+[R/f'renders/FR04b_{n}_{t}.png' for n in ['LOW_FRONT','LOW_INSIDE'] for t in ['material','white']]+[R/f'renders/FR04b_{t}_8angle_contact.png' for t in ['material','white']]
for p in paths:
 a,sz,m=read(p);visuals.append({'file':str(p),'sha256':sha(p),'size':sz,'actual_visual_review':'viewed individually this delivery pass; contact additionally viewed'})
models=[]
prior=json.load(open(O/'independent-FR04b-final.json'))
for t in ['material','white']:
 p=R/f'models/FR04b_{t}.blend';models.append({'file':str(p),'sha256':sha(p),'same_as_independently_geometry_audited_file':sha(p)==prior[t]['sha256']})
out={'scope':'bounded final delivery visual and native-direct50 arithmetic check only; no reconstruction/camera/source refit','native_blends':models,'native_direct50_full_pixel_check':results,'visual_inputs':visuals,'visual_conclusion':['All16 CHECK originals plus4 LOW originals and2 contacts actually viewed; 8 distinct azimuths, no all-occluding backboard used as view count','No obvious reversed-face black patch on corrected roof top/edge surfaces; underside remains shadowed and low-sample noisy, not assumed source-match','LOW_FRONT reveals step/ring/column bases; LOW_INSIDE reveals underside, hanging connections and geometric lamp bodies, not a source view','Reviewed both native4k direct50 images: stage lip near condition fit but outside pool and roof radial extent remain plainly mismatched'],'source_gate':'FAILED / unaccepted candidate. One Aug23 conditional camera only. Sep12 three source inputs not native same-camera aligned. FR05 rejected feasibility, no FR05 model accepted. Depth outputs not independently re-inferred in this bounded final check.'}
(O/'independent-final-delivery-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({'native_blends':models,'pixel_results':results},ensure_ascii=False,indent=2))
