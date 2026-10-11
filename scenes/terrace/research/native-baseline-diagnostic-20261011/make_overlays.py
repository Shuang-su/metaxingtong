from PIL import Image,ImageDraw
import numpy as np,json,pathlib,hashlib,sys
P=pathlib.Path(__file__).resolve().parent
keys=sys.argv[1:] or ['main','low']
sources={'main':'terrace-main-front-BV1g64y1P7VV-t5586.011739-native.png','low':'terrace-autumn-low-BV1g64y1P7VV-t2751.636134-native.png'}
for k in keys:
 out=P/'renders'/k;sp=P/'source/native/terrace/frames'/sources[k];source=Image.open(sp).convert('RGB');a=np.array(source,dtype=np.uint16);checks=[]
 for v in ['raw','oidn']:
  rp=out/f'render_{v}.png';r=Image.open(rp).convert('RGB');assert source.size==r.size==(1920,1080);b=np.array(r,dtype=np.uint16);expected=((a+b)//2).astype(np.uint8);op=out/f'overlay_50_source_{v}.png';Image.fromarray(expected).save(op,optimize=True);actual=np.array(Image.open(op),dtype=np.int16);error=np.abs(actual-expected.astype(np.int16));checks.append({'source':str(sp.relative_to(P)),'render':rp.name,'overlay':op.name,'formula':'uint8(floor((uint16(source RGB) + uint16(render RGB))/2))','blend_space':'display-encoded RGB, exact 50% blend; no registration, warp, crop or resample','max_channel_error':int(error.max()),'nonzero_channel_errors':int(np.count_nonzero(error)),'overlay_sha256':hashlib.sha256(op.read_bytes()).hexdigest()})
 (out/'overlay_validation.json').write_text(json.dumps(checks,indent=2))
 sheet=Image.new('RGB',(1920,406),(30,30,30));draw=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate([(source,'SOURCE native 1920x1080'),(Image.open(out/'render_oidn.png'),'FIXED legacy camera / OIDN display copy'),(Image.open(out/'overlay_50_source_raw.png'),'50% SOURCE + RAW / no registration')]):
  sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(i*640,36));draw.text((i*640+12,12),label,fill='white')
 sheet.save(out/'comparison_preview.jpg',quality=94,subsampling=0)
 print(k,checks)
