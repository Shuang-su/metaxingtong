from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
r=Path('hospital_object_audit');a=r/'candidate';b=r/'candidate_b';src=r/'refs/extracted/hospital/frames';font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
records=[]
for view,box in [('F',(780,900,1920,1080)),('G',(1510,715,1920,1080))]:
 paths=[('Native source; original video pixels',next(src.glob(f'*-{view}-*'))),('Original model; legacy camera; denoised display',a/f'{view}_baseline_legacy_camera_1920_denoised.png'),('A: shoulder remains slanted; retained failure',a/f'{view}_candidate_legacy_camera_1920_denoised.png'),('B: continuous rounded shoulder hypothesis',b/f'{view}_B_legacy_camera_1920_denoised.png')]
 width=box[2]-box[0];height=box[3]-box[1];out=Image.new('RGB',(max(width+40,760),4*(height+44)+80),'#f4f2ed');d=ImageDraw.Draw(out);d.text((20,14),f'{view} | Same-pixel crops, no registration; source camera NOT recalibrated',font=font,fill='#222');y=54
 for label,p in paths:
  d.text((20,y),label,font=font,fill='#222');y+=26;out.paste(Image.open(p).convert('RGB').crop(box),(20,y));y+=height+18;records.append({'view':view,'role':label,'path':str(p),'crop_xyxy':box,'display_scale':1})
 out.save(b/f'{view}_source_original_A_B_local_comparison.png')
for label,outdir in [('A',a),('B',b)]:
 for view in 'FGH':
  source=Image.open(next(src.glob(f'*-{view}-*'))).convert('RGB');suffix='candidate' if label=='A' else 'B';render=Image.open(outdir/f'{view}_{suffix}_legacy_camera_1920.png').convert('RGB');assert source.size==render.size==(1920,1080);Image.blend(source,render,.5).save(outdir/f'{view}_direct50_UNCALIBRATED.png')
# All ordinary views at native diagnostic size; no hidden geometry or cutaways.
for label,outdir in [('A',a),('B',b)]:
 ps=sorted((outdir/'ordinary_checks_denoised').glob('*.png'));out=Image.new('RGB',(1600,1940),'#f4f2ed');d=ImageDraw.Draw(out)
 for i,p in enumerate(ps):
  x=i%2*800;y=i//2*485;d.text((x+10,y+8),p.stem+' | diagnostic, denoised',font=font,fill='#222');out.paste(Image.open(p),(x,y+35))
 out.save(outdir/'eight_ordinary_checks_denoised.png')
(r/'comparison_provenance.json').write_text(json.dumps({'local_crops':records,'overlay_method':'Exact 1920x1080 pixels, source 50% plus raw render 50%; no crop, resize, registration, warp or source edit. Legacy cameras unchanged, uncalibrated against new native frames.'},indent=2))
