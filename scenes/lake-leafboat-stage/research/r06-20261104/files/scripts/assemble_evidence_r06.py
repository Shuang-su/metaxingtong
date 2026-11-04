from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];Q=R/'qa/r06';Q.mkdir(exist_ok=True,parents=True)
rows=[('92.142973','SOURCE_092142973_SIDE','source fit hypothesis'),('100.762992','SOURCE_100762992_TOP','source fit hypothesis'),('108.755584','SOURCE_108755584_OBLIQUE','partial source fit hypothesis'),('6.585758','AUX_006585758_REAR','auxiliary close rear only; not an additional independent fit baseline')]
manifest={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'3 primary source-fit hypotheses + 1 auxiliary view, all actual 3840x2160 source PNGs; same saved geometry/material/lighting. No image warping or local edits.','source_accepted':False,'overlays':[],'display_derivatives':[]}
contact=Image.new('RGB',(1536,4*304),(24,27,30));d=ImageDraw.Draw(contact)
for i,(t,cam,role) in enumerate(rows):
 src=R/'sources'/f'lakeleaf-native-{t}.png';rnd=R/'renders/r06/source'/f'{cam}.png';a=Image.open(src).convert('RGB');b=Image.open(rnd).convert('RGB');assert a.size==b.size==(3840,2160)
 ov=Image.blend(a,b,.5);out=Q/(cam+'-overlay50.png');ov.save(out)
 manifest['overlays'].append({'source':str(src.relative_to(R)),'render':str(rnd.relative_to(R)),'overlay':str(out.relative_to(R)),'role':role,'size':list(a.size),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(rnd.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'Pillow Image.blend(source.convert(RGB), render.convert(RGB), 0.5), no warp/crop/resize','calibration':'Unsolved, conditional visual estimate'})
 for j,(im,label) in enumerate([(a,'SOURCE'),(b,'RENDER'),(ov,'DIRECT 50%')]):
  contact.paste(im.resize((512,288),Image.Resampling.LANCZOS),(512*j,304*i+16));d.text((512*j+5,304*i+2),f'{t}s {label}'+(' AUX' if i==3 else ''),fill=(255,255,255))
 # Explicit source-coordinate object crops. Same coordinates for source/render/overlay, no local transform.
 crop=(380,910,3340,1890) if i==0 else ((1760,600,2120,1390) if i==1 else (0,820,1800,2160))
 if i<3:
  for kind,im in [('source',a),('render',b),('overlay50',ov)]:im.crop(crop).save(Q/f'{cam}-leaf-crop-{kind}.png')
  manifest['display_derivatives'].append({'camera':cam,'crop_xyxy':crop,'kind':'exact same pixel-coordinate crop for source/render/overlay, no warp, not a new source view'})
contact.save(Q/'source-render-overlay-contact.jpg',quality=92)
files=sorted((R/'renders/r06/checks').glob('*.png'));assert len(files)==8
sheet=Image.new('RGB',(1600,2*474),(24,27,30));d=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
 im=Image.open(p).convert('RGB');assert im.size==(1280,720);im=im.resize((800,450),Image.Resampling.LANCZOS);x=(i%2)*800;y=(i//2)*474
 # four rows, dynamically resized below
 if i==0:sheet=Image.new('RGB',(1600,4*474),(24,27,30));d=ImageDraw.Draw(sheet)
 sheet.paste(im,(x,y+24));d.text((x+10,y+5),p.stem+' | actual shared-scene inspection render; not source',fill='white')
sheet.save(Q/'eight-inspection-views-contact.jpg',quality=91)
inv=json.loads((Q/'material-mesh-inventory.json').read_text());objects=[]
for name,data in inv.items():
 if name.startswith('LEAF_001'):observed='Thin concave elongated double-pointed green leaf outline seen in 92s and 100s';inferred='0.035 model-unit shell thickness; hidden underside; exact curvature and scale';evidence=['92.142973','100.762992','108.755584']
 elif name.startswith('LEAF_002'):observed='Single main vein seen in 100s and 108s';inferred='Vein radius and attachment; exact curve';evidence=['100.762992','108.755584']
 elif name.startswith('LEAF_003'):observed='Branching vein class observed; this numbered branch is not independently identified';inferred='Instance count, local radius and attachment';evidence=['100.762992','108.755584']
 elif name.startswith('LAKE'):observed='Reflective lake water around leaf';inferred='Extent, wave phase, reflection/colour pattern; not lakebed';evidence=['92.142973','100.762992','108.755584','6.585758']
 elif name.startswith('ROCK') or name.startswith('OUTCROP'):observed='One planted rocky corner seen in top source';inferred='Placement, count and hidden geometry uncertain';evidence=['100.762992']
 else:observed='Tropical forest/shore class visible, no reliable individual-instance correspondence';inferred='Each generated instance location, scale, branch topology, count and obscured connections';evidence=['92.142973','108.755584','6.585758']
 objects.append({'id':name,'observed':observed,'inferred':inferred,'source_times_seconds':evidence,'source_bv':'BV1JqCeBMEAb','attributes':{'silhouette':'conditional candidate','metric_scale':'unknown','thickness':'inferred unless intentionally open leaf sheet','support_contact':'not source-confirmed','material':'procedural proxy','lighting':'shared daylight hypothesis'},'world_bounds':data['bounds'],'geometry_sha256':data['geometry_sha256'],'acceptance':'not accepted'})
(Q/'per-object-review.json').write_text(json.dumps({'policy':'Stable IDs are generated model instances, not claimed video matches. No per-camera object hiding. All source correspondence conditional.','objects':objects},ensure_ascii=False,indent=2)+'\n')
(Q/'comparison-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Assembled 4 direct full-resolution overlays, 3 object crop triplets, 8-angle contact, and per-object review.')
