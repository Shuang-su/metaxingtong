"""Pixel QA display products; raw source PNGs are read only, never modified."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageOps
import json,hashlib,numpy as np
R=Path(__file__).resolve().parents[1];Q=R/'qa/r09';font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def info(p):return {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def contact(path,rows,w=480,h=270):
 cols=max(len(row) for row in rows);im=Image.new('RGB',(cols*w,len(rows)*(h+36)),(23,29,38));d=ImageDraw.Draw(im)
 for y,row in enumerate(rows):
  for x,(p,label) in enumerate(row):
   pic=p if isinstance(p,Image.Image) else Image.open(p)
   pic=ImageOps.contain(pic.convert('RGB'),(w,h));im.paste(pic,(x*w+(w-pic.width)//2,y*(h+36)+36+(h-pic.height)//2));d.text((x*w+7,y*(h+36)+9),label,font=font,fill='white')
 im.save(path,quality=90)
main=Q/'main.png';im=Image.open(main).convert('RGB');jpeg=Q/'main_preview.jpg'
for quality in [92,90,88,85,82]:
 im.save(jpeg,quality=quality,subsampling=0)
 if jpeg.stat().st_size<900*1024:break
assert jpeg.stat().st_size<900*1024
(Q/'main-preview-provenance.json').write_text(json.dumps({'purpose':'display preview, not pixel comparison','origin':info(main),'output':info(jpeg),'pixels':list(im.size),'resized':False,'jpeg_quality':quality,'subsampling':0,'rerendered_R09':True},indent=2)+'\n')
names=['N4037','N6318','N2518','N2453','N6766'];native={'N4037':'BV1CY411k7Co_00-40-37_native.png','N6318':'BV1CY411k7Co_t6318.457925_native.png','N2518':'BV1CY411k7Co_t2518.167350_native.png','N2453':'BV1CY411k7Co_t2453.795568_native.png','N6766':'BV1CY411k7Co_t6766.766366_native.png'}
rows=[]
for n in names:
 a=Image.open(R/'sources/native'/native[n]).convert('RGB');b=Image.open(Q/f'white_source_{n}.png').convert('RGB');assert a.size==b.size==(1920,1080);o=Image.blend(a,b,.5);o.save(Q/f'white_overlay50_{n}.png');rows.append([(a,n+' native unchanged'),(b,'R09 white / same geometry'),(o,'direct 50% / no registration')])
contact(Q/'white-source-contact.jpg',rows)
contact(Q/'time-state-contact.jpg',[[(Q/f'source_{n}.png',n+' / global S40'),(Q/'alternate_S105'/f'source_{n}.png',n+' / global S105')] for n in names]+[[(Q/'main.png','main / global S40'),(Q/'alternate_S105/main.png','main / global S105')]])
for folder in ['low','trial_a_low']:
 paths=sorted((Q/folder).glob('*.png'));rows=[[(p,p.stem) for p in paths[i:i+3]] for i in range(0,len(paths),3)];contact(Q/(folder+'-contact.jpg'),rows,w=426,h=240)
s=Image.open(R/'sources/native'/native['N2453']).convert('RGB');left=s.crop((505,330,595,452));right=s.crop((1805,785,1915,960))
(Q/'lantern-crop-provenance.json').write_text(json.dumps({'source':'sources/native/'+native['N2453'],'source_pixels':[1920,1080],'crops_xyxy':[[505,330,595,452],[1805,785,1915,960]],'display':'letterboxed resize, aspect retained; two crops of one source, not extra views','model_view':'different diagnostic camera, not a source match'},indent=2)+'\n')
# Separate angles; these are NOT overlays or extra native views.
contact(Q/'lantern-material-diagnostic.jpg',[[(left,'N2453 source crop, display resize'),(right,'N2453 second crop, not new view')],[(Q/'diagnostic_lantern.png','R09 different diagnostic angle'),(Q/'white_diagnostic_lantern.png','R09 same diagnostic, white')]],w=480,h=480)
contact(Q/'main-before-after.jpg',[[(R/'qa/r07/main.png','R07 / same main camera'),(Q/'main.png','R09 / environment candidate')]])
# Source hashes are compared with authoritative manifest values, not inferred timestamps.
manifest=json.loads((R/'sources/source-manifest.json').read_text());received=manifest['native_frames_received'];records=[]
for p in sorted((R/'sources/native').glob('*.png')):
 rec=info(p);matches=[a for a in received if p.name in str(a)]
 assert len(matches)==1,(p.name,len(matches));srec=matches[0];rec['manifest_sha256_matches']=rec['sha256']==srec['sha256'];rec['pixels']=list(Image.open(p).size);assert rec['manifest_sha256_matches'];records.append(rec)
(Q/'native-source-recheck.json').write_text(json.dumps(records,indent=2)+'\n')
if (Q/'glb_reimport_main.png').exists():
 b=Image.open(Q/'glb_reimport_main.png').convert('RGB');a=Image.open(main).convert('RGB');assert a.size==b.size
 diff=np.abs(np.asarray(a,dtype=float)-np.asarray(b,dtype=float));stats={'same_retained_Blender_world_lights_camera':True,'GLB_contains_world':False,'mean_absolute_rgb_8bit_error':float(diff.mean()),'max_absolute_rgb_8bit_error':float(diff.max()),'pixels_with_any_channel_difference_over_8_fraction':float((diff.max(axis=2)>8).mean()),'scope':'appearance comparison in retained Blender environment, not independent viewer sky parity or source acceptance'}
 (Q/'glb-appearance-comparison.json').write_text(json.dumps(stats,indent=2)+'\n');contact(Q/'glb-reimport-contact.jpg',[[(a,'saved material BLEND'),(b,'actual GLB in retained environment')]])
print('R09_DISPLAY_QA_COMPLETE',info(jpeg))
