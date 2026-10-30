"""Portable emission maps derived only from prior authored radial intensity."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];T=R/'textures/r11';T.mkdir(parents=True,exist_ok=True)
p=R/'textures/r09/paper_emission.png';red=np.asarray(Image.open(p).convert('RGB')).astype(float)[...,0]/255
linear=np.where(red<=.04045,red/12.92,((red+.055)/1.055)**2.4)
rows=[]
for name,power,color in [('paper_exitance.png',1.65,(1,.40,.065)),('paper_inner_exitance.png',1,(1,.55,.12))]:
 rgb=linear[...,None]**power*np.array(color)
 srgb=np.where(rgb<=.0031308,rgb*12.92,1.055*np.maximum(rgb,0)**(1/2.4)-.055)
 dest=T/name;Image.fromarray(np.uint8(np.clip(srgb,0,1)*255+.5)).save(dest)
 rows.append({'name':name,'input_power':power,'linear_color':color,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(T/'emission-manifest.json').write_text(json.dumps({'input':'textures/r09/paper_emission.png','input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'decode existing authored sRGB red intensity; power; multiply linear RGB color; encode sRGB. No source pixels, no AI, no UV changes.','files':rows},indent=2)+'\n')
