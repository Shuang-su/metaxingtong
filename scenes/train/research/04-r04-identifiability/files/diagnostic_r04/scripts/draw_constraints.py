from PIL import Image,ImageDraw
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];data=json.loads((R/'analysis/constraints.json').read_text())
for k,v in data.items():
 im=Image.open(R.parents[1]/'train_hd_recapture_20261010'/v['source_file']).crop(v['crop']).convert('RGB');d=ImageDraw.Draw(im)
 for p in v['points']:
  x,y=p['source'];c='lime' if p['split']=='fit' else 'cyan';d.ellipse((x-4,y-4,x+4,y+4),outline=c,width=2);d.text((x+6,y),p['name'],fill=c)
 for l in v['lines']:
  q=l['source'];c='lime' if l['split']=='fit' else 'cyan';d.line([tuple(a) for a in q],fill=c,width=2);d.text(tuple(q[0]),l['name'],fill=c)
 im.save(R/'review'/f'{k}_annotation.png')
