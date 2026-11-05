from PIL import Image,ImageDraw
from pathlib import Path
import json
P=Path(__file__).resolve().parent.parent;scan=json.loads((P/'results/taper-only-scan.json').read_text());ann=json.loads((P/'sources/independent-contour/annotations-v1.json').read_text())
for h in [.74,.55,.57]:
 row=next(r for r in scan['rows'] if r['h']==h)
 for n in ['11','10']:
  im=Image.open(P/'sources'/f'{n}.webp').convert('RGB');d=ImageDraw.Draw(im)
  for b in ann['source'+n]['segments']:
   if 'x_interval' in b:d.rectangle((b['x_interval'][0],b['y_interval'][0],b['x_interval'][1],b['y_interval'][1]),outline='yellow',width=1)
  if n=='11':
   for p in ann['source11']['points']:
    if p['xy'] is None:continue
    x,y=p['xy'];d.ellipse((x-4,y-4,x+4,y+4),outline='red',width=2)
   for p in row['points']:
    x,y=p['projected'];d.ellipse((x-3,y-3,x+3,y+3),outline='cyan',width=2)
    a,b=p['source_xy'];d.line((x,y,a,b),fill='cyan',width=1)
  for band in row['lower_envelopes'][n]:
   for p in band['three_samples']:
    x,y=p['x'],p['y'];d.rectangle((x-2,y-2,x+2,y+2),fill='lime')
  d.rectangle((5,635,1187,666),fill=(10,10,10));d.text((10,644),f'h={h}: RED source conditional points; CYAN model points; GREEN projected shell/rib envelope; YELLOW coarse source bands. No model applied.',fill='white')
  im.save(P/'results'/f'source{n}-taper-{h}-projection.png')
# Original pixel crops, not rescaled, retain every diagnostic source area.
out=Image.new('RGB',(1192,900),(20,20,20));dr=ImageDraw.Draw(out)
for i,h in enumerate([.74,.55,.57]):
 im=Image.open(P/'results'/f'source11-taper-{h}-projection.png');dr.text((8,i*300+5),f'h={h}; source11 full-width crop y0..275; conditional point comparison, not new render',fill='white');out.paste(im.crop((0,0,1192,275)),(0,i*300+25))
out.save(P/'results/taper-source11-contact.png')
