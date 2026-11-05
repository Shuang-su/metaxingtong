"""Generate an explicitly hand-described color-region atlas. No source pixels read.
Uses source-visible outline coordinate hypotheses from build_r01.py, not recovered texture.
"""
import ast,pathlib,json,hashlib
from PIL import Image,ImageDraw
P=pathlib.Path(__file__).resolve().parents[1]
t=ast.parse((P/'scripts/build_r01.py').read_text());polys={}
for n in t.body:
 if isinstance(n,ast.Assign):
  for a in n.targets:
   if isinstance(a,ast.Name) and a.id in ['UI','LI']:polys[a.id]=ast.literal_eval(n.value)
def smooth(p):
 out=[]
 for i in range(len(p)):
  a,b,c,d=[p[j%len(p)] for j in [i-1,i,i+1,i+2]]
  for j in range(8):
   t=j/8;out.append(tuple(.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in [0,1]))
 return out
scale=3;im=Image.new('RGB',(1192*scale,671*scale),(124,160,212));d=ImageDraw.Draw(im)
for poly in polys.values():
 p=smooth(poly)
 for mirror in [False,True]:d.polygon([((1192-u if mirror else u)*scale,v*scale) for u,v in p],fill=(199,230,248))
im=im.resize((1192,671),Image.Resampling.LANCZOS)
out=P/'dependencies/R04-generated-color-regions.png';im.save(out)
meta={'file':out.name,'size':[1192,671],'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'method':'Blank RGB canvas plus two explicitly authored closed Catmull region polygons mirrored about x=596. 3x vector supersampling then Lanczos. No source-image read, sampling or projection.','limits':'Color/opacity/roughness are approximation. Region boundaries guided by visible report-02 silhouette, not physical recovered panel seams.','colors_srgb':{'outer':[124,160,212],'inner':[199,230,248]}}
(P/'dependencies/R04-generated-color-regions.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
