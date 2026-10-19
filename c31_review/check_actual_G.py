from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import numpy as np,json
P=Path(__file__).resolve().parent;B=P.parent
files={'source':B/'inputs/hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','C29':B/'c29/renders/G_C29_MATERIAL_RAW_1920x1080.png','C31':B/'c31/region_tests/G_C31_REGION_ONLY.png'}
r={};out=Image.new('RGB',(1170,355))
for i,(key,p) in enumerate(files.items()):
 im=Image.open(p).convert('RGB');a=np.array(im).mean(2);r[key]={}
 for x in [1700,1900]:
  r[key][str(x)]={}
  for sigma,w in [(1,2),(2,4)]:
   s=gaussian_filter1d(a[:,x-w:x+w+1].mean(1),sigma);g=np.gradient(s);q,_=find_peaks(abs(g[790:1030]),prominence=1,distance=8)
   r[key][str(x)][f'sigma{sigma}_columns{w*2+1}']=[[int(t+790),float(g[t+790])] for t in q]
 crop=im.crop((1530,725,1920,1080));out.paste(crop,(390*i,0));ImageDraw.Draw(out).text((390*i+5,5),key,fill='red')
json.dump({'method':'Appearance gradients with manual contextual edge identity; all peaks retained as audit, not all peaks are object boundaries','profiles':r,'reviewed_measurements':{'source':{'inner_transition':[823,881],'left_hole':[822,880],'outer_boundary':[818,885]},'C29':{'inner_transition':[852,978],'left_hole':[824,890],'outer_top_low_confidence':[825,835],'outer_bottom_approx':1014},'C31':{'inner_transition':[827,896],'left_hole':[824,890],'outer_top':'Not reliably separable from broad shadow/noise','outer_bottom_shadow_exit':908}},'uncertainty':{'source_each_boundary_px':3,'render_strong_inner_or_hole_px':3,'render_outer_shadow_exit_px':4,'render_outer_top':'unresolved'}},open(P/'actual_G_measurements.json','w'),indent=2)
out.save(P/'G_source_C29_C31_native_comparison.png')
