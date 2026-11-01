from PIL import Image
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parents[1];n=2048
u,v=np.meshgrid((np.arange(n)+.5)/n,1-(np.arange(n)+.5)/n);face=(u>.37760419+1/n)&(u<.62239581-1/n)&(v>.75081170+1/n)&(v<.99918830-1/n)
x=.799424946-(v-.75081170)/(.99918830-.75081170)*1.598849892;z=2.8963541+(u-.37760419)/(.62239581-.37760419)*1.5372918
ix=np.rint((x+.80465)/1.6093*511).astype(int).clip(0,511);iy=np.rint((4.45-z)/1.57*511).astype(int).clip(0,511)
for name in ['BASE','STRESS_A','STRESS_B']:
 src=np.array(Image.open(D/f'textures/DERIVED_PARTIAL_POSTER_{name}.png'));valid=face&(src[iy,ix,3]==255);rgb=np.full((n,n,3),[53,60,69],np.uint8);rgb[valid]=src[iy[valid],ix[valid],:3];Image.fromarray(rgb).save(D/f'textures/DERIVED_EXISTING_UV_ATLAS_{name}.png')
(D/'qa/existing_uv_atlas.json').write_text(json.dumps({'resolution':[n,n],'scope':'derived RGB atlas into existing unchanged UVMap; front face only, other UV islands neutral','source_front_polygon_index':0,'front_uv_u':[.37760419,.62239581],'front_uv_v':[.75081170,.99918830],'sampling':'nearest derived rgba, only alpha255; 1 atlas texel inset at face border; all other pixels neutral opaque','geometry_uv_modified':False,'missing_color_srgb':[53,60,69]},indent=2))
