from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent.parent
source=Image.open(P/'sources/11.webp').convert('RGB');assert source.size==(1192,671)
for variant in ['material','white']:
 im=Image.open(P/'renders'/f'v3-{variant}-source11-32s.png').convert('RGB');Image.blend(source,im,.5).save(P/'renders'/f'v3-{variant}-source11-direct50.png')
def contact(path,files,labels):
 out=Image.new('RGB',(1192,len(files)*701),(10,10,10));d=ImageDraw.Draw(out)
 for i,(f,label) in enumerate(zip(files,labels)):
  im=Image.open(f).convert('RGB');assert im.size==(1192,671);out.paste(im,(0,i*701+30));d.text((8,i*701+8),label,fill='white')
 out.save(P/'renders'/path)
contact('source11-comparison.png',[P/'sources/11.webp',P/'renders/baseline-source11-8s.png',P/'renders/v3-material-source11-32s.png'],['SOURCE11 non-native / unknown timestamp','BASELINE a055 / 8 samples / original lighting','v3 MATERIAL / 32 samples / only outer LED surface changed / SOURCE FAILED'])
contact('close-material-white-comparison.png',[P/'renders/baseline-close-8s.png',P/'renders/v3-material-close-32s.png',P/'renders/v3-white-close-32s.png'],['BASELINE original continuous edge / 8 samples / author diagnostic view','v3 MATERIAL point-matrix surface / 32 samples / author diagnostic view','v3 WHITE shared geometry / no pattern by design / 32 samples'])
rows=[]
for f in sorted((P/'renders').glob('*.png')):
 im=Image.open(f);rows.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'size':list(im.size)})
(P/'renders/final-image-manifest.json').write_text(json.dumps(rows,indent=2))
