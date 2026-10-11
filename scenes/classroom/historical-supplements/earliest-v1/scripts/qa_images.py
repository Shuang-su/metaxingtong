from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F=ImageFont.truetype(font,20);Fs=ImageFont.truetype(font,14)
pairs=[('A_Front','class_919.jpg','Final_Textured_Match_A_clean.png','00:15:19 front teaching wall'),('B_Window','class_2123.jpg','Final_Textured_Match_B_clean.png','00:35:23 window side'),('C_Wide','class_4284.jpg','Final_Textured_Match_C_Wide_clean.png','01:11:24 complete classroom')]
manifest=[]
for name,ref,ren,title in pairs:
 a=Image.open(R/'references'/ref).convert('RGB').crop((0,27,1190,696)).resize((1280,720),Image.Resampling.LANCZOS)
 b=Image.open(R/'renders'/ren).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
 ov=Image.blend(a,b,.5);ov.save(R/'qa'/('Overlay50_'+name+'.jpg'),quality=94)
 panel=Image.new('RGB',(1280,790),'#172029');panel.paste(a.resize((640,360)),(0,60));panel.paste(b.resize((640,360)),(640,60));panel.paste(ov.resize((640,360)),(320,430));d=ImageDraw.Draw(panel);d.text((18,14),title+' | source / reconstruction / 50% overlay',font=F,fill='white');d.text((8,424),'Global crop + resize only; no local warps. Performer is intentionally omitted.',font=Fs,fill='white');panel.save(R/'qa'/('Comparison_'+name+'.jpg'),quality=93)
 manifest.append({'view':name,'reference':ref,'render':ren,'reference_crop_xyxy':[0,27,1190,696],'render_resolution':[1280,720],'overlay_render_alpha':.5,'local_warp':False,'limitations':'Performer and moving props omitted; source 360p, camera fit approximate. Outdoor geometry is a disclosed generic interpretation.'})
for v in ['Level_Front','Level_Windows']:
 a=Image.open(R/'renders'/('Final_Textured_'+v+'_clean.png')).convert('RGB');b=Image.open(R/'renders'/('Final_White_'+v+'_clean.png')).convert('RGB')
 pan=Image.new('RGB',(1280,760),'#172029');pan.paste(a.resize((640,360)),(0,40));pan.paste(b.resize((640,360)),(640,40));d=ImageDraw.Draw(pan);d.text((18,8),'Identical geometry | textured / white | '+v,font=F,fill='white');pan=pan.crop((0,0,1280,400));pan.save(R/'qa'/('Paired_'+v+'.jpg'),quality=94)
json.dump(manifest,open(R/'qa/image_comparison_manifest.json','w'),indent=2)
# Compact delivery copies preserve all views while full PNGs remain locally available.
D=R/'delivery_views';D.mkdir(exist_ok=True)
for p in (R/'renders').glob('Final_*_clean.png'):Image.open(p).convert('RGB').save(D/(p.stem.replace('_clean','')+'.jpg'),quality=94)
print('QA_IMAGES_COMPLETE')
