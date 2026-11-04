from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,statistics
r=Path(__file__).resolve().parents[1];trials=['baseline','height060','height082'];groups={'17':[13,14,15],'20':[10,11,12],'21':[21,22,23]};bands={'17':{'top':[337,341],'bottom':[445,451]},'20':{'top':[532,535],'bottom':[589,600]},'21':{'top':[350,357],'bottom':[406,414]}};out=[];allimgs=[]
for t in trials:
 d=json.loads((r/'results'/t/'state.json').read_text());summary={'trial':t,'ratio':d['white_ratio'],'top_black_below_white_world_gap':d['white_minus_black_top_world_z_min'],'bottom_fixed_max_error':d['bottom_vertex_world_max_error'],'sources':{}}
 for src,ids in groups.items():
  box=[x['bbox_xyxy'] for x in d['projected_geometry_boxes'][src] if x['id'] in ['white-key-%02d'%i for i in ids]];top=statistics.mean(b[1] for b in box);bottom=statistics.mean(b[3] for b in box);ref=bands[src];summary['sources'][src]={'baseline_screen_region_representative_ids':ids,'top_box_mean_y':top,'bottom_box_mean_y':bottom,'source_rough_visible_top_band':ref['top'],'source_rough_visible_bottom_band':ref['bottom'],'conditional_top_delta_to_source_band_mid':top-statistics.mean(ref['top']),'conditional_bottom_delta_to_source_band_mid':bottom-statistics.mean(ref['bottom']),'warning':'geometry bbox vs source visible edge, same-screen region only, not identity or silhouette correspondence'}
  p=r/'results'/t/f'source{src}.png';im=Image.open(p).convert('RGB');srcim=Image.open(r/'inputs'/f'{src}.webp').convert('RGB');assert im.size==srcim.size==(1192,671);op=r/'results'/t/f'source{src}-direct50.png';Image.blend(srcim,im,.5).save(op)
  for q,role in [(p,'8sample original fixed-camera trial'),(op,'direct same-grid 50%')]:allimgs.append({'path':str(q.relative_to(r)),'role':role,'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'dimensions':[1192,671]})
 out.append(summary)
# Source + baseline + .60 + .82 at exact native crops; no resizing.
crops={'17':(140,240,440,490),'20':(80,485,300,671),'21':(660,280,820,440)}
for src,box in crops.items():
 w,h=box[2]-box[0],box[3]-box[1];sheet=Image.new('RGB',(w*4,h+24));draw=ImageDraw.Draw(sheet)
 paths=[r/'inputs'/f'{src}.webp']+[r/'results'/t/f'source{src}.png' for t in trials]
 for i,p in enumerate(paths):sheet.paste(Image.open(p).convert('RGB').crop(box),(i*w,24));draw.text((i*w+3,3),['SOURCE','BASELINE 1.0','HEIGHT 0.60','HEIGHT 0.82'][i],fill='white')
 sheet.save(r/'results'/f'compare-source{src}-native-crop.png')
(r/'results/conditional-edge-metrics.json').write_text(json.dumps({'note':'No metric is a geometry acceptance score. Source17/21 give limited shortening signal; source20 bottom mismatch persists. No training or grid search.','groups':groups,'native_crop_xyxy':crops,'trials':out},indent=2));(r/'results/image-manifest.json').write_text(json.dumps(allimgs,indent=2));print(json.dumps(out,indent=2))
