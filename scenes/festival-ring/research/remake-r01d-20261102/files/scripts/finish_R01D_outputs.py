from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib,numpy as np
r=Path(__file__).resolve().parents[1];o=r/'versions/R01D';pairs=[('source4k','BV1gttHeGE9Z_53.951826_4k.png'),('front','BV15e4deGE1R_144.009018_1080high.png'),('oblique','BV15e4deGE1R_60.010322_1080high.png')];rows=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for view,source in pairs:
 sp=r/'sources'/source;src=Image.open(sp).convert('RGB')
 for mode in ['material','white']:
  rp=o/f'{view}-{mode}-native.png';ren=Image.open(rp).convert('RGB');assert ren.size==src.size,(view,mode,src.size,ren.size)
  dest=o/f'{view}-{mode}-direct50-native.png';Image.blend(src,ren,.5).save(dest)
  actual=np.array(Image.open(dest).convert('RGB'));direct=np.array(Image.blend(src,ren,.5));assert np.array_equal(actual,direct)
  rows.append({'source':str(sp.relative_to(r)),'source_bytes':sp.stat().st_size,'source_sha256':sha(sp),'render':str(rp.relative_to(r)),'render_sha256':sha(rp),'overlay':str(dest.relative_to(r)),'size':src.size,'bytes':dest.stat().st_size,'overlay_sha256':sha(dest),'pixel_max_difference_from_direct_blend':int(np.abs(actual.astype('int16')-direct.astype('int16')).max()),'resize_warp_translation':'NONE; native frame dimensions, same frozen candidate camera','source_status':'conditional training alignment, NOT accepted reconstruction'})
(r/'qa/R01D-six-native-overlay-verification.json').write_text(json.dumps(rows,indent=2))
# Explicitly derived display previews, not added source angles.
for mode in ['material','white']:
 im=Image.open(o/f'source4k-{mode}-native.png').convert('RGB');im.resize((1920,1080),Image.Resampling.LANCZOS).save(o/f'main-{mode}-1920-derived.jpg',quality=92)
check=Image.new('RGB',(1920,1128),(18,22,30));d=ImageDraw.Draw(check);d.text((12,8),'R01D / 8 structural diagnostic cameras / display derivative / SOURCE NOT ACCEPTED',fill='white')
for i in range(1,9):
 im=Image.open(o/f'check_{i:02d}.png').convert('RGB');im=im.resize((480,540),Image.Resampling.LANCZOS) if False else im.resize((480,270),Image.Resampling.LANCZOS)
 x=((i-1)%4)*480;y=32+((i-1)//4)*294;check.paste(im,(x,y+22));d.text((x+4,y),f'CHECK {i:02d} / not source',fill='white')
check.crop((0,0,1920,620)).save(o/'eight-checks-derived.jpg',quality=92)
sheet=Image.new('RGB',(2400,966),(18,22,30));d=ImageDraw.Draw(sheet);d.text((8,6),'R01D / each panel downsampled 480x270 / source alignment NOT ACCEPTED',fill='white')
for row,(view,srcname) in enumerate(pairs):
 files=[r/'sources'/srcname,o/f'{view}-material-native.png',o/f'{view}-material-direct50-native.png',o/f'{view}-white-native.png',o/f'{view}-white-direct50-native.png']
 for col,(f,label) in enumerate(zip(files,['SOURCE','MATERIAL','DIRECT50','WHITE','WHITE DIRECT50'])):
  x=480*col;y=30+row*310;im=Image.open(f).convert('RGB').resize((480,270),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+22));d.text((x+5,y),view+' / '+label,fill='white')
sheet.save(o/'three-source-comparison-derived.jpg',quality=93)
outputs=[]
for p in sorted(o.iterdir()):
 if p.is_file():outputs.append({'path':str(p.relative_to(r)),'bytes':p.stat().st_size,'sha256':sha(p)})
(r/'qa/R01D-output-manifest.json').write_text(json.dumps({'files':outputs,'original_blends_remain_frozen':True,'preview_derivations':'Lanczos native to1920/480, no geometry inference; no new source angles','complete_files_only_not_acceptance':True},indent=2));print('OUTPUT_VALIDATION_COMPLETE',len(outputs))
