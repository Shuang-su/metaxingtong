"""Pixel-exact 50% blends/crops; source PNGs untouched. No warps, masks or inpainting."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'renders/source';Q=R/'qa';C=Q/'object-crops';C.mkdir(exist_ok=True)
sources=json.loads((R/'sources/source-manifest.json').read_text())['sources']
renders=['S01_render_closed.png','S02_render_open.png','S03_render_closed.png','S04_context_only_render.png']
out=[];images={}
for src,r in zip(sources,renders):
 a=Image.open(R/src['path']).convert('RGB');b=Image.open(O/r).convert('RGB');assert a.size==b.size==(1920,1080)
 over=Image.blend(a,b,.5);p=O/(src['id']+'_direct_50percent_overlay.png');over.save(p)
 images[src['id']]=(a,b,over)
 out.append({'source':src['path'],'render':str((O/r).relative_to(R)),'overlay':str(p.relative_to(R)),'alpha':.5,'operation':'PIL.Image.blend(source RGB, render RGB, 0.5), no mask/warp/crop','dimensions':[1920,1080],'status':'uncalibrated diagnostic; no source fit acceptance','source_sha256':src['sha256'],'render_sha256':hashlib.sha256((O/r).read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 # Viewer panel: labeled display only; original 1920 PNG trio remains authoritative.
 panel=Image.new('RGB',(1440,306),(24,27,34));d=ImageDraw.Draw(panel)
 for i,(im,title) in enumerate(zip([a,b,over],['NATIVE SOURCE','UNCALIBRATED RENDER','DIRECT 50% BLEND'])):
  panel.paste(im.resize((480,270)),(i*480,36));d.text((i*480+12,11),src['id']+' / '+title,fill='white')
 panel.save(O/(src['id']+'_comparison_panel.jpg'),quality=92)
crop_specs=[('C01_round_vent','S03',(270,600,470,800),'D02-D06; vent center/diameter remain mismatched'),('C02_pillar_mirror','S03',(0,160,860,600),'A01,P14-P17; pillar inclination and mirror visibility uncalibrated'),('C03_woven_strip','S03',(400,555,990,680),'P02,P03; center occluded by character'),('C04_armrest','S03',(460,715,920,880),'P05,P06; character intersects crop; shape inferred'),('C05_seat_edge','S01',(1580,475,1920,1080),'S01,S02; only visible outer edge, not whole seat'),('C06_opening_sill','S02',(900,630,1130,1000),'B02,P01; door angle and character occlusion unresolved'),('C07_visor','S01',(275,0,1020,235),'A03,A05; visor footprint/thickness uncalibrated')]
crops=[]
for name,src,box,note in crop_specs:
 paths=[]
 for im,role in zip(images[src],['source','render','overlay']):
  p=C/(name+'_'+role+'.png');im.crop(box).save(p);paths.append(str(p.relative_to(R)))
 crops.append({'id':name,'source':src,'box_xyxy_native':box,'display_scale':1,'note':note,'paths':paths,'comparison':'Same image coordinates in native source and corresponding render; no realignment or local warping'})
(Q/'comparison-manifest.json').write_text(json.dumps({'full_frame':out,'object_crops':crops},indent=2)+'\n')
# Required JPEG preview keeps full original render dimensions.
p=R/'renders/main/car_passenger_cabin_main.png';im=Image.open(p).convert('RGB');dest=p.with_suffix('.jpg')
for quality in [94,92,90,88,85,82,78,74,70]:
 im.save(dest,quality=quality,optimize=True)
 if dest.stat().st_size<900*1024:break
assert dest.stat().st_size<900*1024
(Q/'preview-manifest.json').write_text(json.dumps({'source_png':str(p.relative_to(R)),'jpeg':str(dest.relative_to(R)),'dimensions':im.size,'resized':False,'quality':quality,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2)+'\n')
# All arbitrary views shown in labeled contact sheet, each scaled for inspection only.
checks=sorted((R/'renders/checks').glob('*.png'));sheet=Image.new('RGB',(1280,3*350),(23,26,32));d=ImageDraw.Draw(sheet)
for i,p in enumerate(checks):
 im=Image.open(p).convert('RGB');im.thumbnail((420,315));x=(i%3)*426;y=(i//3)*350
 sheet.paste(im,(x,y+30));d.text((x+8,y+8),p.stem+' / DIAGNOSTIC',fill='white')
sheet.save(Q/'arbitrary_views_contact_sheet.jpg',quality=94)
