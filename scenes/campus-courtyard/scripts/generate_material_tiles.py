from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parents[1];t=R/'textures';t.mkdir(exist_ok=True)
rng=np.random.default_rng(42)
a=np.clip(rng.normal(162,3,(512,512,1))+np.array([0,3,5]),0,255).astype('uint8');im=Image.fromarray(a);d=ImageDraw.Draw(im)
for x in [0,256]:
    d.rectangle([x,0,x+4,511],fill=(68,73,76));d.line([(x+5,0),(x+5,511)],fill=(188,190,191),width=2)
for y in [0,256]:
    d.rectangle([0,y,511,y+4],fill=(68,73,76));d.line([(0,y+5),(511,y+5)],fill=(188,190,191),width=2)
im.save(t/'pavers.png')
rng=np.random.default_rng(211);v=gaussian_filter(rng.normal(0,1,(512,512)),(1,2));v=v/v.std()*18
ridge=gaussian_filter(rng.normal(0,1,(512,512)),(24,1));ridge=ridge/ridge.std()*11;val=v+ridge
im=np.stack([90+val,69+val*.84,51+val*.65],2);Image.fromarray(np.clip(im,0,255).astype('uint8')).save(t/'bark.png')
