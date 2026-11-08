from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
root=Path(__file__).resolve().parents[1];qa=root/'qa/r08';src=root/'sources/native/BV1CY411k7Co_t6766.766366_native.png';old=root/'qa/r07/source_N6766.png';new=qa/'source_N6766.png'
s,r0,r=[Image.open(p).convert('RGB') for p in [src,old,new]];assert s.size==r0.size==r.size==(1920,1080)
o=Image.blend(s,r,.5);o.save(qa/'overlay50_N6766.png')
contact=Image.new('RGB',(1600,260),'#18212a');d=ImageDraw.Draw(contact);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
for i,(im,label) in enumerate([(s,'N6766 native source'),(r0,'R07 retained render'),(r,'R08 camera-only candidate'),(o,'Direct 50% blend / no warp')]):
 contact.paste(im.resize((400,225)),(i*400,35));d.text((i*400+7,9),label,font=font,fill='white')
contact.save(qa/'N6766-camera-comparison.jpg',quality=92)
r.save(qa/'N6766_display_preview.jpg',quality=92,optimize=True,subsampling=0)
record={'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'retained_r07_render':str(old.relative_to(root)),'r08_render':str(new.relative_to(root)),'overlay':'qa/r08/overlay50_N6766.png','exact_comparison_dimensions':[1920,1080],'operation':'PIL.Image.blend(source RGB, render RGB, 0.5)','warp_registration_mask':'none','contact_sheet_display_resize_only':[400,225],'camera_status':'closer framing candidate, calibration not passed; upper cheek and trim residual remains'}
(qa/'overlay-manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print('N6766 comparison complete')
