from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
P=Path(__file__).resolve().parents[1];O=P/'renders/R08-comparisons';O.mkdir(exist_ok=True);records=[]
for name,roi in [('DIAG_spot_mount',(100,90,1100,530)),('DIAG_sign_profile',(350,50,1070,620))]:
 paths=[P/'renders/R08'/f'{stage}_white_{name}.png'for stage in ['R07','R08']];ims=[Image.open(f).convert('RGB').crop(roi)for f in paths];w,h=ims[0].size;canvas=Image.new('RGB',(w,2*(h+28)),(25,25,25));draw=ImageDraw.Draw(canvas)
 for i,im in enumerate(ims):canvas.paste(im,(0,i*(h+28)+28));draw.text((8,i*(h+28)+7),['R07 BEFORE / SAME SYNTHETIC DIAGNOSTIC VIEW','R08 AFTER / HIDDEN MOUNTING CAPS EXTENDED'][i],fill='white')
 f=O/f'{name}_same_pixels_before_after.png';canvas.save(f);records.append({'files':[str(z.relative_to(P))for z in paths],'source_hashes':[hashlib.sha256(z.read_bytes()).hexdigest()for z in paths],'crop_xyxy':roi,'resample':False,'output':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'scope':'technical synthetic macro only; not source matching/physical installation measurement'})
(P/'qa/R08-crop-records.json').write_text(json.dumps(records,indent=2))
