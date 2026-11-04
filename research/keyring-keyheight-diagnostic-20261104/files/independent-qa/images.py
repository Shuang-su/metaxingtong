from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,statistics
R=Path('/workspace/scratch/fa58bfcf0425/keyring-keyheight-diagnostic-20261104');O=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();arr=lambda p:np.array(Image.open(p).convert('RGB'));d=json.loads((R/'results/conditional-edge-metrics.json').read_text());out={'manifest':[],'overlays':[],'crops':[],'metrics':[]}
for r in json.loads((R/'results/image-manifest.json').read_text()):
 p=R/r['path'];out['manifest'].append({'path':r['path'],'match':sha(p)==r['sha256'] and p.stat().st_size==r['bytes'] and list(Image.open(p).size)==r['dimensions'],'sha256':sha(p)})
for t in ['baseline','height060','height082']:
 st=json.loads((R/f'results/{t}/state.json').read_text());row={'trial':t,'sources':{}}
 for src,ids in d['groups'].items():
  boxes=[r['bbox_xyxy'] for r in st['projected_geometry_boxes'][src] if r['id'] in [f'white-key-{i:02}' for i in ids]];rec=next(x for x in d['trials'] if x['trial']==t)['sources'][src];top=statistics.mean(b[1] for b in boxes);bot=statistics.mean(b[3] for b in boxes);row['sources'][src]={'top':top,'bottom':bot,'top_residual':top-statistics.mean(rec['source_rough_visible_top_band']),'bottom_residual':bot-statistics.mean(rec['source_rough_visible_bottom_band']),'metric_matches':top==rec['top_box_mean_y'] and bot==rec['bottom_box_mean_y']};a=arr(R/f'inputs/{src}.webp').astype(np.uint16);b=arr(R/f'results/{t}/source{src}.png').astype(np.uint16);c=arr(R/f'results/{t}/source{src}-direct50.png');out['overlays'].append({'trial':t,'source':src,'max_error':int(abs(((a+b)//2).astype(int)-c.astype(int)).max())})
 out['metrics'].append(row)
for src,box in d['native_crop_xyxy'].items():
 x1,y1,x2,y2=box;w=x2-x1;a=arr(R/f'results/compare-source{src}-native-crop.png');paths=[R/f'inputs/{src}.webp']+[R/f'results/{t}/source{src}.png' for t in ['baseline','height060','height082']];out['crops'].append({'source':src,'all_four_panes_exact':all(np.array_equal(a[24:,i*w:(i+1)*w],arr(p)[y1:y2,x1:x2]) for i,p in enumerate(paths)),'sha256':sha(R/f'results/compare-source{src}-native-crop.png')})
out['input_model_sha']=sha(R/'inputs/r06-material-frozen.blend');(O/'image-integrity.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['metrics'],indent=2))
