"""One real Images API edit. No retries, no keys in files/logs, no credential placeholders."""
from pathlib import Path
import os,sys,json,hashlib,base64,io,argparse
from PIL import Image
HERE=Path(__file__).resolve().parent
MODEL='gpt-image-2.6-sunburst'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    src=HERE/'sources';paths=[src/'xingtong-17-1024.png',src/'nailu-17-1024.png',src/'mask-17-1024.png']
    for p in paths:
        with Image.open(p) as im:assert im.format=='PNG' and im.size==(1024,1024)
    with Image.open(paths[2]) as mask:assert mask.mode=='RGBA' and mask.getchannel('A').getextrema()==(0,255)
    # Do not silently substitute a proxy placeholder. A network-secret route
    # requires a separately confirmed binding and its documented client setup.
    configured=bool(os.environ.get('OPENAI_API_KEY'))
    if args.check:
        print(json.dumps({'inputs_valid':True,'model':MODEL,'api_key_present':configured,'request_would_be':'POST https://api.openai.com/v1/images/edits','max_retries':0,'timeout_seconds':180,'size':'1024x1024','quality':'medium','n':1}));return
    if not configured:
        print('BLOCKED: current runtime has no OPENAI_API_KEY binding; no request sent. Configure the existing key in cloud environment settings.',file=sys.stderr);raise SystemExit(2)
    from openai import OpenAI,APIStatusError,APIConnectionError,APITimeoutError
    client=OpenAI(max_retries=0,timeout=180.0,base_url='https://api.openai.com/v1')
    prompt=(HERE/'frame17-prompt.txt').read_text(encoding='utf-8')
    try:
        with open(paths[0],'rb') as main_image,open(paths[1],'rb') as reference,open(paths[2],'rb') as mask:
            reply=client.images.edit(model=MODEL,image=[main_image,reference],mask=mask,prompt=prompt,size='1024x1024',quality='medium',output_format='png',n=1)
    except APIStatusError as exc:
        # Do not print raw response bodies/headers; retain only safe diagnosis.
        print(json.dumps({'status':'failed','http_status':exc.status_code,'request_id':exc.request_id,'retry_attempted':False}));raise SystemExit(3)
    except (APIConnectionError,APITimeoutError) as exc:
        print(json.dumps({'status':'failed','error_type':type(exc).__name__,'retry_attempted':False}));raise SystemExit(4)
    encoded=reply.data[0].b64_json
    if not encoded:raise RuntimeError('Images API did not return PNG bytes')
    raw=base64.b64decode(encoded,validate=True)
    with Image.open(io.BytesIO(raw)) as image:assert image.format=='PNG' and image.size==(1024,1024);image.load()
    out=src/'frame17-api.png';out.write_bytes(raw)
    receipt={'status':'completed','endpoint':'https://api.openai.com/v1/images/edits','model':MODEL,'request_id':reply._request_id,'size':[1024,1024],'quality':'medium','n':1,'input_order':[p.name for p in paths[:2]],'inputs':{p.name:sha(p) for p in paths},'prompt_sha256':sha(HERE/'frame17-prompt.txt'),'output_sha256':sha(out),'output_file':str(out.relative_to(HERE))}
    (HERE/'frame17-api-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
