from PIL import Image
import numpy as np,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent.parent;W,H=8192,256;cols,rows=1024,4
y,x=np.mgrid[:H,:W];fx=((x+.5)/W*cols)%1;fy=((y+.5)/H*rows)%1
# Fixed author parameters, no image fitting; rectangular softened spots.
mask=np.minimum(np.clip((.25-abs(fx-.5))/.12,0,1),np.clip((.33-abs(fy-.5))/.10,0,1))
base=np.array([.12,.85,.59]);linear=mask[:,:,None]*base
srgb=np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055)
a=np.uint8(np.clip(np.round(srgb*255),0,255));Image.fromarray(a,'RGB').save(P/'textures/outer-band-emission.png')
baselin=base*(.025+.25*mask[:,:,None]);b=np.where(baselin<=.0031308,12.92*baselin,1.055*baselin**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(np.round(b*255),0,255)),'RGB').save(P/'textures/outer-band-basecolor.png')
q=a/255.;decoded=np.where(q<=.04045,q/12.92,((q+.055)/1.055)**2.4);means=decoded.mean((0,1));luma=np.array([.2126,.7152,.0722]);strength=float((2*base@luma)/(means@luma));result={'author_parameters':{'width':W,'height':H,'columns':cols,'rows':rows,'phase':[.5,.5],'horizontal_halfwidth':.25,'vertical_halfwidth':.33,'softness':[.12,.10]},'not_recovered_physical_LED_count':True,'original_emission_linear_rgb':base.tolist(),'original_strength':2,'emission_png_mean_linear_rgb':means.tolist(),'candidate_strength_luminance_matched':strength,'mean_emission_rgb':(means*strength).tolist(),'original_mean_emission_rgb':(base*2).tolist(),'mean_rgb_error':(means*strength-2*base).tolist(),'mask_mean':float(mask.mean()),'basecolor_change':'linear original basecolor multiplied by (.025+.25*mask), dark substrate; metallic.2 roughness.3 retained','files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'textures-v2').glob('*.png')}};(P/'textures/pattern-recipe.json').write_text(json.dumps(result,indent=2));print(result)
