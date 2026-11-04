from PIL import Image
import numpy as np,pathlib,json,hashlib
r=pathlib.Path(__file__).resolve().parents[1];s=r/'sources/forest-official4k-native-503.06141.png';o=r/'comparisons/R09';o.mkdir(exist_ok=True,parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for mode in ['material','white']:
 p=r/('renders/R09_'+mode)/'SOURCE_G_4K_top.png';a=np.array(Image.open(s).convert('RGB'),dtype=np.uint16);b=np.array(Image.open(p).convert('RGB'),dtype=np.uint16);assert a.shape==b.shape==(2160,3840,3)
 d=o/(mode+'_SOURCE_G_4K_top_direct50.png');Image.fromarray(((a+b)//2).astype('uint8')).save(d)
 records.append(dict(source=str(s.relative_to(r)),render=str(p.relative_to(r)),output=str(d.relative_to(r)),source_sha256=sha(s),render_sha256=sha(p),output_sha256=sha(d),size=[3840,2160],formula='floor((sourceRGB8+renderRGB8)/2)',warping=False,acceptance='FAILED',visibility_failure='6/11 hypothesized flower points blocked by FAR_TREE_17 and its branch; new cut/world pose is not reconstructed'))
(o/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
