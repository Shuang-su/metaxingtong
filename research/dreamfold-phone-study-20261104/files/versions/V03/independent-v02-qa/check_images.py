from PIL import Image
import numpy as np,pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/dreamfold-phone-study-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-dreamfold-phone-v02-qa-20261104');R={}
s=Image.open(P/'sources/reta2-7.img').convert('RGB');r=Image.open(P/'renders/source7-conditional.png').convert('RGBA');bg=Image.new('RGBA',r.size,(0,0,0,255));flat=Image.alpha_composite(bg,r).convert('RGB');expected=Image.blend(s,flat,.5);actual=Image.open(P/'renders/source7-direct-50pct.png').convert('RGB');a=np.array(actual).astype(int);b=np.array(expected).astype(int);R['overlay_max_error_black_composite_then_floor_average']=int(abs(a-b).max());R['overlay_changed_values']=int(np.count_nonzero(a-b));R['alpha_range']=[int(np.array(r)[:,:,3].min()),int(np.array(r)[:,:,3].max())];R['images']={}
for f in (P/'renders').glob('*.png'):
 im=Image.open(f);im.load();arr=np.array(im);R['images'][f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':im.size,'mode':im.mode}
 if im.mode=='RGBA':
  al=arr[:,:,3];yy,xx=np.where(al>0);R['images'][f.name]['nonzero_alpha_bounds']=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())];R['images'][f.name]['alpha_touches_edge']=bool(al[0].any()or al[-1].any()or al[:,0].any()or al[:,-1].any())
(Q/'images.json').write_text(json.dumps(R,indent=2));print(R)
