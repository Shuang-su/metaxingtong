from pathlib import Path
import json,struct,hashlib,io
import numpy as np
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/cyber-ring-emissive-band-study-20261105');O=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();r={}
for mode,suf in [('material',''),('white','-white')]:
 b=(P/f'export/roof-led-surface-v3{suf}.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);start=20+n;length=struct.unpack_from('<I',b,start)[0];blob=b[start+8:start+8+length];ims=[]
 for im in j.get('images',[]):
  v=j['bufferViews'][im['bufferView']];ib=blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];matched=[]
  for f in (P/'textures-v2').glob('*.png'):
   if ib==f.read_bytes():matched.append(f.name)
  ims.append({'name':im.get('name'),'sha256':sha(ib),'external_exact':matched,'size':list(Image.open(io.BytesIO(ib)).size)})
 r[mode]={'images':ims,'materials':j['materials'],'has_external_buffers':any('uri'in v for v in j['buffers'])}
a=np.asarray(Image.open(P/'textures-v2/outer-band-emission.png'),dtype=float)/255.;lin=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);means=lin.mean((0,1));recipe=json.loads((P/'textures-v2/pattern-recipe.json').read_text());actual=json.loads((O/'check.json').read_text())['band']['strength'];w=np.array([.2126,.7152,.0722]);old=np.array([.24,1.7,1.18]);r['mean']={'linear_rgb':means.tolist(),'actual_strength':actual,'actual_rgb':(means*actual).tolist(),'luminance_ratio':float(means*actual@w/(old@w)),'recipe_linear_max_error':float(np.max(abs(means-recipe['emission_png_mean_linear_rgb'])))}
r['renders']=[]
for view in ['source11','close']:
 f=P/f'renders/v3-material-{view}-8s.png';q=json.loads(f.with_name(f.stem+'-recipe.json').read_text());im=Image.open(f);im.load();r['renders'].append({'path':str(f),'size':list(im.size),'sha_match':sha(f.read_bytes())==q['image_sha256'],'model_sha_match':sha((P/'export/roof-led-surface-v3.blend').read_bytes())==q['input_sha256'],'script_sha_match':sha((P/'scripts/render_saved_v3.py').read_bytes())==q['script_sha256'],'actual_strength_match':actual==q['actual_strength'],'alpha_range':im.getchannel('A').getextrema() if 'A' in im.getbands() else None})
(O/'pixels.json').write_text(json.dumps(r,indent=2));print(r['mean']);print(r['renders']);print([(k,len(r[k]['images']),[i['external_exact'] for i in r[k]['images']]) for k in ['material','white']])
