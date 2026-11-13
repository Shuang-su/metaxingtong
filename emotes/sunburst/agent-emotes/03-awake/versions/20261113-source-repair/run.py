from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import json,base64,hashlib,time
ROOT=Path('/Volumes/Extreme SSD/metaxingtong');DEST=Path(__file__).parent;SRC=DEST.parents[1]/'sources'
def run(job):
 name,size=job;out=DEST/(name+'.png')
 if out.exists() or (DEST/(name+'.started')).exists():return
 key=next(l.partition('=')[2].strip().strip('"').strip("'") for l in (ROOT/'.env.local').read_text().splitlines() if l.startswith('OPENAI_API_KEY='))
 client=OpenAI(api_key=key,project='proj_DSZR8ZQewzllgZPBQcXUSh9c',max_retries=0,timeout=400)
 prompt='''Repair the supplied animation sheet with EXTREMELY LOCAL anatomical corrections. Preserve its exact layout, number of cells, all facial expressions, eyes, hair, clothing design, character positions, scale, background, and pose timing. This is NOT a redesign or a new story. Each cell contains exactly two seated girls, silver-haired Xingtong on the left, brown-haired Nailu on the right. Each girl must have exactly TWO arms and TWO hands total. DEFECT ONE: the brown-haired girl raises her own RIGHT arm (viewer-left arm) to poke the silver-haired girl's cheek. In those cells ONLY, the duplicated resting RIGHT hand and redundant sleeve still visible on her viewer-left knee must be removed and replaced with plausible uninterrupted white/cream dress fabric and knee. Keep her other hand on her viewer-right knee. Preserve the actual reaching sleeve/hand and exact gesture. When she is not reaching, keep both hands naturally resting on knees. DEFECT TWO: remove the extra skin-colored hand/finger-like fragment sitting at the silver-haired girl's viewer-right shoulder in every cell where it appears; reconstruct ONLY her navy sleeve/white collar there. Both of her real hands on her own knees must remain unchanged. Do not erase the brown-haired girl's genuine reaching hand where it touches her cheek. Check each cell independently: two girls, four hands TOTAL, connected arms, anatomically coherent contact. Preserve all other pixels as faithfully as possible, including pupils, lashes, blush, line weight and hair flower attachments. No labels, no new borders, no extra fingers, no additional hand remnants. Return the same complete sheet dimensions as input.'''
 req=dict(model='gpt-image-2.6-sunburst',size=size,quality='medium',output_format='png',n=1,prompt=prompt)
 data=(SRC/(name+'.png')).read_bytes();(DEST/(name+'.request.json')).write_text(json.dumps({**req,'input_sha256':hashlib.sha256(data).hexdigest(),'max_attempts':1},indent=2))
 (DEST/(name+'.started')).write_text(str(time.time()))
 try:
  raw=client.images.with_raw_response.edit(image=(name+'.png',data,'image/png'),**req);res=raw.parse();b=base64.b64decode(res.data[0].b64_json);out.write_bytes(b)
  usage=res.usage.model_dump(mode='json') if res.usage else None
  details=usage.get('input_tokens_details',{}) if usage else {};estimate=(8*details.get('image_tokens',0)+5*details.get('text_tokens',0)+30*usage.get('output_tokens',0))/1e6 if usage else None
  record={'request_id':raw.headers.get('x-request-id'),'usage':usage,'sha256':hashlib.sha256(b).hexdigest(),'estimated_usd_historical_rates':estimate,'rate_note':'Historical project rates: image input8,text input5,image output30 USD/million tokens; not an invoice.','status':'generated_pending_visual_review'}
  (DEST/(name+'.result.json')).write_text(json.dumps(record,indent=2));print(name,json.dumps(record),flush=True)
 except Exception as e:
  safe={'status':'failed','error_type':type(e).__name__,'status_code':getattr(e,'status_code',None)};(DEST/(name+'.result.json')).write_text(json.dumps(safe));print(name,safe,flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[('keys','1536x1536'),('strip-1','1536x2048')]))
