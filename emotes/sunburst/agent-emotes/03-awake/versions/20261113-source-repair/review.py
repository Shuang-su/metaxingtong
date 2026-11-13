from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).parent;S=D.parents[1]/'sources'
def white(p):
 im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);return bg.convert('RGB')
def cell(im,k):
 x=(k%3)*512;y=(k//3)*512;return im.crop((x,y,x+512,y+512))
canvas=Image.new('RGB',(1024,4*542),'white');draw=ImageDraw.Draw(canvas)
for row,(name,k) in enumerate([('keys',2),('keys',3),('strip-1',0),('strip-1',3)]):
 for col,root in enumerate([S,D]):
  canvas.paste(cell(white(root/(name+'.png')),k),(col*512,row*542+30))
  draw.text((col*512+10,row*542+8),f'{name} cell {k+1} '+('ORIGINAL' if col==0 else 'API TRIAL - REJECTED'),fill='black')
canvas.save(D/'rejected-comparison.jpg',quality=95)
records=[]
for name in ['keys','strip-1']:
 p=D/(name+'.result.json');r=json.loads(p.read_text());r['status']='rejected_visual_review';r['review']='Duplicate knee hands remain in reaching cells.' if name=='keys' else 'Reaching arm removed in cells1-3 and10-12, breaking intended action; duplicate hands remain in cells4-9.';p.write_text(json.dumps(r,indent=2));records.append(r)
(D/'verification.json').write_text(json.dumps({'status':'rejected_do_not_replace_production','api_calls':2,'estimated_total_usd_historical_rates':sum(r['estimated_usd_historical_rates'] for r in records),'usage_input_tokens':sum(r['usage']['input_tokens'] for r in records),'usage_output_tokens':sum(r['usage']['output_tokens'] for r in records),'checks':{'keys_size':[1536,1536],'strip1_size':[1536,2048],'keys_has_unrequested_alpha':True,'original_gifs_modified':False,'visual_acceptance':False},'next_step':'Use tightly bounded edit masks on duplicate knee/shoulder areas, protect the actual reaching arm and all faces. Test one cell before rebuilding transition sheets; needs another approved request batch.'},indent=2))
# Preparation only: a conservative edit mask for a future single-cell test.
# White/opaque = protected; transparent = editable. This does not modify artwork.
original=Image.open(S/'keys.png').convert('RGBA').crop((0,512,512,1024));original.save(D/'next-test-cell04-original.png')
mask=Image.new('RGBA',(512,512),(255,255,255,255));md=ImageDraw.Draw(mask)
md.rounded_rectangle((318,352,375,421),radius=8,fill=(255,255,255,0))
md.rounded_rectangle((173,303,207,338),radius=5,fill=(255,255,255,0))
mask.save(D/'next-test-cell04-mask.png')
(D/'next-test-mask.json').write_text(json.dumps({'status':'prepared_only_not_submitted','input':'next-test-cell04-original.png','mask':'next-test-cell04-mask.png','coordinates':[[318,352,375,421],[173,303,207,338]],'convention':'alpha0 editable;alpha255 protected','note':'Conservative draft mask. Must inspect boundaries at full resolution before any request. No new API call.'},indent=2))
