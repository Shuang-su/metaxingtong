from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import os,json,zipfile,hashlib
R=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
def label(im,text):
 im=im.copy().convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,im.width,35),fill='#142530');d.text((12,4),text,fill='white',font=font);return im
ref=Image.open(R/'references/season_1786.jpg').convert('RGB').crop((0,46,1188,714));ref.save(R/'qa/Source_Crop_29m46s.jpg')
a=Image.open(R/'renders/Final_Textured_Match_A_clean.png').convert('RGB');b=Image.open(R/'renders/Final_White_Match_A_clean.png').convert('RGB')
Image.blend(ref,a,.5).save(R/'qa/Final_Overlay.png')
canvas=Image.new('RGB',(1188*3,703),'#142530')
for k,(im,t) in enumerate([(ref,'SOURCE 29:46 - character and UI not reconstructed'),(b,'WHITE - identical geometry / matched camera'),(a,'TEXTURED - matched camera')]):canvas.paste(label(im,t),(k*1188,35))
canvas.resize((2376,469)).save(R/'qa/Reference_White_Textured.jpg',quality=94)
canvas=Image.new('RGB',(1188*2,703*2),'#142530')
for k,n in enumerate([1,2,3,4]):
 im=Image.open(R/f'renders/Iteration_{n:02}.png').resize((1188,668));canvas.paste(label(im,['INITIAL: sparse tree / incomplete pergola','REFINE: pergola / tree silhouette','POLISH: individual leaves / cratered disk','FINAL: source crop / arch extent / sun'][k]),(k%2*1188,k//2*703))
canvas.resize((1782,1054)).save(R/'qa/Iteration_Comparison.jpg',quality=94)
for n in [1,2,3,4]:
 im=Image.open(R/f'renders/Iteration_{n:02}.png').resize((1188,668)).convert('RGB');Image.blend(ref,im,.5).save(R/f'qa/Iteration_{n:02}_Overlay.jpg',quality=91)
packages={
 '01_Seasonal_Terrace_White.zip':[R/'models/Xingtong_Seasonal_Terrace_White.blend',R/'models/Xingtong_Seasonal_Terrace_White.glb'],
 '02_Seasonal_Terrace_Textured.zip':[R/'models/Xingtong_Seasonal_Terrace_Textured.blend',R/'models/Xingtong_Seasonal_Terrace_Textured.glb'],
 '03_Seasonal_Terrace_Review_Source_Textures.zip':list((R/'textures').glob('*'))+list((R/'references').glob('*'))+list((R/'scripts').glob('*.py'))+list((R/'qa').glob('*.jpg'))+list((R/'qa').glob('*.json'))+[R/'qa/Final_Overlay.png']+list((R/'renders').glob('*_clean.png'))}
manifest={}
for name,files in packages.items():
 p=R/'delivery'/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,6) as z:
  for f in files+[R/'README.txt']:z.write(f,str(f.relative_to(R)))
 assert p.stat().st_size<45_000_000
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 manifest[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
json.dump(manifest,open(R/'delivery/delivery_manifest.json','w'),indent=2);print(json.dumps(manifest,indent=2))
