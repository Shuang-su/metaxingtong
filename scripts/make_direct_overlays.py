"""Direct native-grid integer 50% RGB overlays, with no registration or warping."""
from PIL import Image,ImageDraw
import numpy as np,pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1]
M={'SOURCE_A_high':'2956.48091','SOURCE_B_side':'2966.475632','SOURCE_C_low':'2988.177427','SOURCE_D_floating_wide':'2992.479275','SOURCE_E_under':'3047.185491','SOURCE_F_top':'3050.458712'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
O=R/'comparisons/R08';O.mkdir(parents=True,exist_ok=True);records=[]
for mode in ['material','white']:
 for cam,t in M.items():
  s=R/'sources'/('forest-native-'+t+'.png');r=R/'renders'/('R08_'+mode)/(cam+'.png')
  a=np.array(Image.open(s).convert('RGB'));b=np.array(Image.open(r).convert('RGB'));assert a.shape==b.shape,(s,r,a.shape,b.shape)
  dest=O/(mode+'_'+cam+'_direct50.png');Image.fromarray(((a.astype(np.uint16)+b.astype(np.uint16))//2).astype(np.uint8)).save(dest)
  records.append(dict(source=str(s.relative_to(R)),render=str(r.relative_to(R)),output=str(dest.relative_to(R)),source_sha256=sha(s),render_sha256=sha(r),output_sha256=sha(dest),size=[a.shape[1],a.shape[0]],formula='floor((native RGB8 + rendered RGB8) / 2)',warping=False,camera=cam,source_time=float(t),geometry_acceptance='FAILED',temporal_note='single frozen floating candidate; early A/B are state/layout auxiliary, no common world-pose proof'))
 for prefix in ['CHECK_']:
  files=sorted((R/'renders'/('R08_'+mode)).glob(prefix+'*.png'));assert len(files)==8
  out=Image.new('RGB',(1600,510),(25,25,25));d=ImageDraw.Draw(out)
  for i,p in enumerate(files):
   im=Image.open(p);im.thumbnail((400,225));x=i%4*400;y=i//4*255;out.paste(im,(x,y+25));d.text((x+6,y+5),p.stem+' / '+mode,fill='white')
  out.save(O/(mode+'_eight-checks.jpg'),quality=95)
(O/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
