from PIL import Image,ImageDraw,ImageFont
import json,pathlib,csv,hashlib,math
Q=pathlib.Path(__file__).resolve().parents[1];P=pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105')
d=json.loads((Q/'fixed-plane-diagnostic.json').read_text());base=json.loads(pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-s-rail-analysis-20261105/baseline/central-projected-baseline.json').read_text());src=Image.open(P/'sources/report-02.png').convert('RGB')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
summary={'status':'NOT_APPLIED_LIMITED_DIAGNOSTIC','source02_row_checks':[],'distinct_camera_hypothesis_world_separation':{},'measurement_warning':'Brightness threshold core and appearance midline are not physical surface or axis. Subjective +/-3px is not a confidence interval. Small excesses do not robustly disprove shared state or all fixed-plane curves.'}
for c in d['cases']:
 for r in c['source02_diagnostic_rows']:
  rec={k:c[k] for k in ['side','camera','plane','Y']};rec.update(r);rec['threshold_center_x']={}
  for th in ['220','225','235']:
   vals=[]
   for seg in c['segments']:
    for a,b in zip(seg['samples'][:-1],seg['samples'][1:]):
     if th not in a['threshold_brackets'] or th not in b['threshold_brackets']:continue
     aa=a['threshold_brackets'][th];bb=b['threshold_brackets'][th]
     ax=(aa['source02_left'][0]+aa['source02_right'][0])/2;ay=(aa['source02_left'][1]+aa['source02_right'][1])/2
     bx=(bb['source02_left'][0]+bb['source02_right'][0])/2;by=(bb['source02_left'][1]+bb['source02_right'][1])/2
     if (ay-r['y02'])*(by-r['y02'])<=0 and ay!=by:vals.append(ax+(r['y02']-ay)/(by-ay)*(bx-ax))
   rec['threshold_center_x'][th]=vals or None
  summary['source02_row_checks'].append(rec)
for side in ['L','R']:
 cs=[c for c in d['cases'] if c['side']==side and c['plane']=='mean'];maps=[{v['source05_center_proxy'][1]:v['world_center_proxy'] for seg in c['segments'] for v in seg['samples']} for c in cs]
 dist=[math.dist(maps[0][k],maps[1][k]) for k in maps[0]];summary['distinct_camera_hypothesis_world_separation'][side]={'min':min(dist),'max':max(dist),'meaning':'Same observed pixel backprojected to same Y plane under two distinct fixed camera hypotheses. These are not one shared 3D curve.'}
(Q/'summary.json').write_text(json.dumps(summary,indent=2))
with (Q/'source02-row-checks.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['side','source05_camera','plane','Y','row02','target_x','predicted_x','signed_dx','threshold220_x','threshold235_x','null_reason'])
 for r in summary['source02_row_checks']:
  i=r['intersections'];w.writerow([r['side'],r['camera'],r['plane'],r['Y'],r['y02'],r['target_center_proxy_x'],i[0]['center_proxy_x'][0] if i else '',i[0]['signed_center_dx'][0] if i else '',r['threshold_center_x']['220'],r['threshold_center_x']['235'],r['null_reason']])
boards=[]
for name,label in [('SOURCE05_conditional_close','原05条件相机'),('SOURCE05_alternate_tilt_diagnostic','替代05俯角相机')]:
 im=src.copy();dr=ImageDraw.Draw(im)
 for sign in [1,-1]:
  pts=base['objects'][f'CENTRAL_S_visible_{sign}']['projections']['SOURCE02_conditional_front']['centers_pixel'];dr.line([tuple(p) for p in pts],fill=(255,130,30),width=1)
 for c in d['cases']:
  if c['camera']!=name:continue
  for seg in c['segments']:
   color=(0,255,255) if c['plane']=='mean' else (180,80,220)
   dr.line([tuple(p['source02_center_proxy']) for p in seg['samples']],fill=color,width=1)
 for side in ['L','R']:
  for r in next(c for c in d['cases'] if c['camera']==name and c['plane']=='mean' and c['side']==side)['source02_diagnostic_rows']:
   x,y=r['target_center_proxy_x'],r['y02'];dr.line([(x-3,y),(x+3,y)],fill=(255,230,0));dr.line([(x,y-2),(x,y+2)],fill=(255,230,0))
 im.save(Q/f'source02-{name}-planar-overlay-native.png')
 crop=im.crop((445,485,747,615)).resize((906,390),Image.Resampling.BICUBIC);board=Image.new('RGB',(926,480),(18,22,30));board.paste(crop,(10,80));dr=ImageDraw.Draw(board);dr.text((10,8),label+'：02原图裁区显示放大3倍BICUBIC',font=font,fill='white');dr.text((10,34),'橙=旧S中心；青=均值平面；紫=原min/max；黄=02已知短段',font=font,fill='white');boards.append(board)
b=Image.new('RGB',(926,960));b.paste(boards[0],(0,0));b.paste(boards[1],(0,480));b.save(Q/'source02-planar-comparison-display3x.png')
print(json.dumps(summary['distinct_camera_hypothesis_world_separation']))
