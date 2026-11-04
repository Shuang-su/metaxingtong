from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
p=Path(__file__).resolve().parent;s=p.parent/'source-newscene-20261104'
# ROIs in inspected 462x260 thumbnail coordinates, scaled exactly to original grid.
rows=[('forest','3047.185491',[(1,[(291,40),(329,40),(329,95),(291,95)]),(3,[(0,72),(180,72),(180,260),(0,260)]),(4,[(179,96),(417,96),(365,174),(306,219),(257,182)])]),('forest','3050.458712',[(1,[(231,83),(283,83),(283,166),(231,166)]),(3,[(0,0),(126,0),(126,260),(0,260)])]),('lakeleaf','92.142973',[(1,[(196,114),(239,114),(239,203),(196,203)]),(3,[(0,0),(462,0),(462,166),(390,165),(214,183),(76,144),(0,160)]),(2,[(0,170),(77,156),(97,194),(214,227),(335,211),(398,180),(462,185),(462,260),(0,260)])]),('lakeleaf','100.762992',[(2,[(0,0),(218,0),(218,260),(0,260)]),(2,[(250,0),(462,0),(462,260),(250,260)]),(2,[(218,0),(250,0),(250,82),(218,82)]),(2,[(218,157),(250,157),(250,260),(218,260)]),(1,[(224,111),(242,111),(242,146),(224,146)])]),('lakeleaf','108.755584',[(3,[(0,0),(462,0),(462,126),(0,126)]),(2,[(0,126),(36,121),(178,190),(410,260),(462,260),(462,126)]),(1,[(160,78),(232,78),(232,259),(160,259)])])]
labels={1:'Moving performer conservative ROI, includes background, not precise segmentation',2:'Dynamic water/reflection or reflected forest; not reliable solid geometry',3:'Background foliage/fog, alpha boundaries and occlusion; not certified solid surface',4:'Dark continuous inverted island underside silhouette; material and local shape unresolved, NOT empty roots or absence of surface'}
for kind,t,regions in rows:
 src=(s if kind=='forest' else s/'lakeleaf')/f'{kind}-native-{t}.png'; w,h=Image.open(src).size
 cap=json.loads(src.with_suffix('.json').read_text())
 ex=[{'shape':'polygon','points':[[round(x*w/462),round(y*h/260)] for x,y in points],'class':cls,'description':labels[cls]} for cls,points in regions]
 bv='BV1ic12BMEk6' if kind=='forest' else 'BV1JqCeBMEAb'
 m={'BV':bv,'url':f'https://www.bilibili.com/video/{bv}/','uploader':'星瞳_Official','time_seconds':float(t),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'capture_record':cap,'quality':'1080P 高码率, highest offered official source' if kind=='forest' else '4K 超高清, highest offered and actual decoded3840x2160; upstream upscale history unknown','exclusions':ex,'mask_classes':labels,'scene_cautions':['Conservative incomplete manual ROIs, unlabelled does not imply valid','Dark continuous underside does not imply void; bright canopy is not floor','Water reflections and screen overlap cannot establish contact','Native4K is not raw4K depth; raw grid924x518','No absolute distance, hidden geometry or motion inference; no later-date replay verification'],'dark_rgb_max_threshold':25}
 meta=p/'provenance'/f'{kind}-{t}-metadata.json';meta.write_text(json.dumps(m,ensure_ascii=False,indent=2))
 with (p/'provenance'/f'{kind}-{t}.log').open('w') as log:subprocess.run([str(p/'venv/bin/python'),str(p/'run_depth_frame.py'),'--source',str(src),'--metadata',str(meta),'--out',str(p/f'{kind}-{t}')],stdout=log,stderr=subprocess.STDOUT,check=True)
 print(kind,t,'complete',flush=True)
