"""Direct unchanged-size 50% source/model composites. No registration transform."""
from PIL import Image,ImageDraw
import pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];O=P/'renders/R04_direct_comparison';O.mkdir(exist_ok=True)
records=[]
for source,camera in [('02','SOURCE02_conditional_front'),('05','SOURCE05_alternate_tilt_diagnostic')]:
 sp=P/f'sources/report-{source}.png';a=Image.open(sp).convert('RGB')
 for tag in ['white','material']:
  rp=P/f'renders/R04_source/{tag}_{camera}.png';b=Image.open(rp).convert('RGB');assert a.size==b.size==(1192,671)
  op=O/f'source{source}_{tag}_direct50.png';Image.blend(a,b,.5).save(op)
  records.append({'source':str(sp.relative_to(P)),'source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'render':str(rp.relative_to(P)),'render_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'output':str(op.relative_to(P)),'size':list(a.size),'operation':'Pillow Image.blend(sourceRGB, renderRGB, 0.5), no resize/crop/warp/registration/color adjustment','camera':camera,'status':'SOURCE_FAILED; source screenshots not native video frames'})
  board=Image.new('RGB',(1192*3,671+44),(24,24,30));d=ImageDraw.Draw(board)
  for i,(im,title) in enumerate([(a,f'Report {source} source: NOT native video'),(b,f'R04 {tag}: same shared geometry'),(Image.open(op),f'Direct 50% / SOURCE FAILED / {camera}')]):
   board.paste(im,(1192*i,44));d.text((1192*i+12,14),title,fill=(240,240,240))
  board.save(O/f'source{source}_{tag}_comparison-board.jpg',quality=93)
(O/'direct50-provenance.json').write_text(json.dumps(records,indent=2))
print('FOUR_DIRECT_SAME_SIZE_50_PERCENT_COMPOSITES_COMPLETE')
