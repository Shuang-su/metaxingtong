"""Deterministic synthetic PBR texture suggestions, NOT sampled source textures."""
from PIL import Image
from pathlib import Path
import numpy as np, json, hashlib
R=Path(__file__).resolve().parents[1];T=R/'textures';T.mkdir(exist_ok=True)
n=512;y,x=np.mgrid[0:n,0:n];rng=np.random.default_rng(20261029)
v=np.where((x//64)%2==0,x+y,x-y)
ridge=(np.cos(v*2*np.pi/16)*.5+.5)
weft=(np.sin((x-y)*2*np.pi/4)*.5+.5)
grain=rng.normal(0,1,(n,n))
carbon=np.clip(37+ridge*16+weft*4+grain*1.8,0,255).astype('uint8')
fine=np.clip(120+rng.normal(0,11,(n,n)),0,255).astype('uint8')
rough=np.clip(158+ridge*20+grain*2,0,255).astype('uint8')
for name,a in [('woven_basecolor.png',carbon),('woven_roughness.png',rough),('fine_grain_height.png',fine)]:
 im=Image.fromarray(np.stack([a,a,a],axis=2));im.save(T/name)
manifest={'provenance':'Procedurally synthesized approximate materials, no source texture extraction or image retouching','size':[n,n],'files':[]}
for p in sorted(T.glob('*.png')):manifest['files'].append({'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(T/'texture-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
