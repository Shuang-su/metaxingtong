from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[1];O=P/'renders/R07-comparisons';O.mkdir(exist_ok=True);r=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=P/'sources/report/08.png'
for mode in ['material','white']:
 f=P/'renders/R07'/f'{mode}_SOURCE_08_wide.png'
 if not f.exists():continue
 a=np.asarray(Image.open(s).convert('RGB'));b=np.asarray(Image.open(f).convert('RGB'));assert a.shape==b.shape
 out=O/f'{mode}_SOURCE_08_wide_direct50.png';Image.fromarray(((a.astype('uint16')+b.astype('uint16')+1)//2).astype('uint8')).save(out)
 r.append({'source':str(s.relative_to(P)),'source_sha256':sha(s),'render':str(f.relative_to(P)),'render_sha256':sha(f),'overlay':str(out.relative_to(P)),'overlay_sha256':sha(out),'formula':'floor((sourceRGB+renderRGB+1)/2)','resample':False,'source_validation':'FAILED'})
a=P/'renders/R06/white_CHECK_05.png';b=P/'renders/R07/white_CHECK_05.png'
if b.exists():
 roi=(400,120,800,520);ims=[Image.open(z).convert('RGB').crop(roi)for z in [a,b]];out=O/'white_grid_same_pixel_before_after.png';canvas=Image.new('RGB',(800,430),(25,25,25));d=ImageDraw.Draw(canvas)
 for i,(im,label) in enumerate(zip(ims,['R06 SAME PIXELS / COPLANAR ARTIFACT','R07 SAME PIXELS / LOCAL TECHNICAL REPAIR'])):canvas.paste(im,(400*i,30));d.text((400*i+5,8),label,fill='white')
 canvas.save(out);(P/'qa/R07-local-crop.json').write_text(json.dumps({'source_files':[str(z.relative_to(P))for z in [a,b]],'source_hashes':[sha(z)for z in[a,b]],'crop_xyxy':roi,'resample':False,'output':str(out.relative_to(P)),'sha256':sha(out),'scope':'same synthetic CHECK05, not source-match acceptance'},indent=2))
(P/'qa/R07-overlay-records.json').write_text(json.dumps(r,indent=2))
print('overlays',len(r))
