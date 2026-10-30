from PIL import Image,ImageDraw
import json
from pathlib import Path
D=Path('/workspace/shared/arcade-header-local-20261030');im=Image.open(D/'qa/source_header_native_crop.png').convert('RGB');dr=ImageDraw.Draw(im)
pts=[['L1',44,16,5],['L2',34,37,7],['L3',35,66,8],['L4',55,84,11],['L5',86,110,15],['R1',510,12,13],['R2',482,49,18]]
for label,x,y,r in pts:dr.ellipse((x-r-2,y-r-2,x+r+2,y+r+2),outline='cyan',width=1);dr.text((x+r+3,y),label,fill='cyan')
im.save(D/'qa/observed_gold_dot_annotations.png');(D/'qa/observed_gold_dots.json').write_text(json.dumps({'native_crop_origin':[520,0],'points_manual_approximate_px':pts,'error_bound_px':3,'count_visible_only':7,'above_frame':'unknown; do not infer missing count','physical_circle_radii':'not measured; perspective affects ellipse dimensions'},indent=2))
