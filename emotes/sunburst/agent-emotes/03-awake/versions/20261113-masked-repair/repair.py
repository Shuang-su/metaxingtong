from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from openai import OpenAI
import json,base64,hashlib,time,sys,subprocess
from io import BytesIO
ROOT=Path('/Volumes/Extreme SSD/metaxingtong');D=Path(__file__).parent;BASE=D.parents[1]
def run(n):
 target=D/f'{n:02}';target.mkdir(exist_ok=True)
 if (target/'result.json').exists() or (target/'started').exists():return
 im=Image.open(BASE/'frames'/f'{n:02}.png').convert('RGBA');size=im.size
 mask=Image.new('RGBA',size,(255,255,255,255));draw=ImageDraw.Draw(mask)
 # The only editable regions are duplicate knee arm and stray shoulder fingers.
 boxes=[]
 if 8<=n<=34:boxes.append((477,528,563,635))
 if n<=26:boxes.append((259,454,311,509))
 for box in boxes:draw.rounded_rectangle(box,radius=8,fill=(255,255,255,0))
 im.save(target/'input.png');mask.save(target/'mask.png')
 key=next(l.partition('=')[2].strip().strip('"').strip("'") for l in (ROOT/'.env.local').read_text().splitlines() if l.startswith('OPENAI_API_KEY='))
 # Existing curl supports the configured SOCKS proxy; do not alter proxy settings.
 prompt='''Inpaint ONLY the transparent mask holes. Two small anatomical cleanups, no redesign. In the knee hole on the brown-haired girl at RIGHT, DELETE the redundant resting hand and redundant downward sleeve because her real right arm is ALREADY extended horizontally toward the left girl. Fill that hole with continuous cream-white skirt/dress and natural folds, matching surrounding dress texture. There must be NO skin-colored hand and NO separate cuff in that hole. Keep her real extended arm and her other hand on her other knee untouched. In the small LEFT girl's shoulder hole, DELETE the stray extra fingers/hand sitting on her shoulder, reconstruct dark navy shoulder sleeve and white collar with continuous edges. Leave the actual approaching hand outside that hole untouched. Absolutely preserve faces, eyes, hair, expressions, positions and all pixels outside the masked holes. Two girls, exactly two hands each. Return the same scene and fixed framing on white background. Do not delete the reaching gesture. Do not repaint the whole illustration.'''
 req=dict(model='gpt-image-2.6-sunburst',size='1024x1024',quality='medium',output_format='png',n=1,prompt=prompt)
 (target/'request.json').write_text(json.dumps({**req,'boxes':boxes,'source_frame':n,'input_sha256':hashlib.sha256((target/'input.png').read_bytes()).hexdigest()},indent=2));(target/'started').write_text(str(time.time()))
 try:
  cfg=['url = "https://api.openai.com/v1/images/edits"','request = "POST"','header = "Authorization: Bearer '+key+'"','header = "OpenAI-Project: proj_DSZR8ZQewzllgZPBQcXUSh9c"','max-time = 400','silent','show-error']
  args=['curl','--config','-','--form','image=@'+str(target/'input.png'),'--form','mask=@'+str(target/'mask.png')]
  for k,v in req.items():args.extend(['--form-string',str(k)+'='+str(v)])
  proc=subprocess.run(args,input='\n'.join(cfg),text=True,capture_output=True)
  if proc.returncode:raise RuntimeError('curl_transport_failed_'+str(proc.returncode))
  result=json.loads(proc.stdout)
  if 'error' in result:
   error=result['error'];(target/'result.json').write_text(json.dumps({'status':'api_error','type':error.get('type'),'code':error.get('code'),'message':error.get('message')},indent=2));print(n,'API_ERROR',error.get('type'),error.get('code'),flush=True);return
  data=base64.b64decode(result['data'][0]['b64_json']);(target/'api.png').write_bytes(data)
  out=Image.open(BytesIO(data)).convert('RGBA').resize(size,Image.Resampling.LANCZOS)
  # Hard protect every pixel outside the explicit original mask, irrespective of model drift.
  a=Image.eval(mask.getchannel('A'),lambda x:255-x);final=Image.composite(out,im,a).convert('RGB');final.save(target/'candidate.png')
  u=result.get('usage') or {};details=u.get('input_tokens_details',{});est=(8*details.get('image_tokens',0)+5*details.get('text_tokens',0)+30*u.get('output_tokens',0))/1e6
  record={'request_id':result.get('id'),'transport':'curl_existing_proxy','usage':u,'estimated_usd_historical_rates':est,'candidate_sha256':hashlib.sha256((target/'candidate.png').read_bytes()).hexdigest(),'status':'pending_visual_review'};(target/'result.json').write_text(json.dumps(record,indent=2));print(n,json.dumps(record),flush=True)
 except Exception as e:
  err={'status':'failed','error_type':type(e).__name__,'status_code':getattr(e,'status_code',None)};(target/'result.json').write_text(json.dumps(err));print(n,err,flush=True)
if __name__=='__main__':
 for n in map(int,sys.argv[1:]):run(n)
