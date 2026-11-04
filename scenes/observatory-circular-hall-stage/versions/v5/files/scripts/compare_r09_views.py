from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[1];out=P/'renders/R09-comparisons';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[];sources={'SOURCE_13_high':'13','SOURCE_14_front':'14','SOURCE_15_exterior':'15','SOURCE_21_high':'21'}
for mode in ['material','white']:
 for cam,n in sources.items():
  src=P/'sources/report'/f'{n}.png';r=P/'renders/R09'/f'{mode}_{cam}.png';a=np.array(Image.open(src).convert('RGB'),dtype=np.uint16);b=np.array(Image.open(r).convert('RGB'),dtype=np.uint16);assert a.shape==b.shape==(671,1192,3);f=out/f'{mode}_{cam}_direct50.png';Image.fromarray(((a+b)//2).astype(np.uint8)).save(f);records.append({'source':str(src.relative_to(P)),'source_sha256':sha(src),'render':str(r.relative_to(P)),'render_sha256':sha(r),'overlay':str(f.relative_to(P)),'overlay_sha256':sha(f),'formula':'floor((source_RGB+render_RGB)/2), original dimensions; no warp or resize'})
 names=list(sources)+['CHECK_01','CHECK_03','CHECK_05','CHECK_07'];board=Image.new('RGB',(1192,4*(336+24)),(25,25,25));d=ImageDraw.Draw(board)
 for i,n in enumerate(names):
  r=P/'renders/R09'/f'{mode}_{n}.png';im=Image.open(r).convert('RGB').resize((596,336),Image.Resampling.LANCZOS);x=(i%2)*596;y=(i//2)*360;board.paste(im,(x,y+24));d.text((x+5,y+5),n,fill=(255,255,255))
 f=out/f'{mode}_eight-model-views_CONTACTSHEET.png';board.save(f)
(P/'qa/R09-overlay-records.json').write_text(json.dumps(records,indent=2));(P/'qa/R09-contactsheet-scope.json').write_text(json.dumps({'cameras':list(sources)+['CHECK_01','CHECK_03','CHECK_05','CHECK_07'],'scope':'Eight current model viewing angles:4 source-camera hypotheses and4 synthetic check angles; not8 real source views or full acceptance. Contactsheet only uses labeled LANCZOS thumbnails, originals retained. Main excluded.'},indent=2))
