from PIL import Image,ImageDraw,ImageFont
import numpy as np,pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');Q=pathlib.Path(__file__).resolve().parents[1]
p=P/'sources/report-05.png';im=Image.open(p).convert('RGB');a=np.asarray(im);d=ImageDraw.Draw(im);rows=[]
# Broad visual search windows, not a fitted curve. Left and right independently extracted.
for side,lo,hi in [('L',475,575),('R',615,715)]:
 for y in range(125,276):
  candidates={}
  for threshold in [220,225,235]:
   xs=np.flatnonzero(a[y,lo:hi].min(axis=1)>threshold)+lo;runs=[]
   for x in xs:
    if not runs or x>runs[-1][-1]+1:runs.append([int(x)])
    else:runs[-1].append(int(x))
   runs=[r for r in runs if len(r)>=3]
   # Choose the main thick run in the manually isolated window. If ties/merges,
   # keep observations but don't infer a hidden S-only boundary.
   if runs:
    r=max(runs,key=len);candidates[str(threshold)]={'left':r[0],'right':r[-1],'width_core_px':len(r)}
  r=candidates.get('225');ambiguous=175<=y<=205
  use=bool(r) and not ambiguous
  rec={'side':side,'y':y,'threshold_brackets':candidates,'use_for_planar_shape_diagnostic':use,'center_proxy_xy':[(r['left']+r['right'])/2,y] if use else None,'exclusion':'thin outer arc merger; cannot assign full S-only outline or center' if ambiguous else None}
  rows.append(rec)
  if r:
   col=(255,128,0) if ambiguous else (0,255,255);d.point((r['left'],y),fill=col);d.point((r['right'],y),fill=col)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
b=Image.new('RGB',(1192,713),(18,22,30));b.paste(im,(0,42));dd=ImageDraw.Draw(b);dd.text((10,9),'原05像素亮带边诊断：青=连续可归属候选；橙=外细弧汇入，中心/完整S外边不补',font=font,fill='white');b.save(Q/'observations/source05-visible-band-edges.png')
out={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Per-original-pixel row RGB minimum threshold 220/225/235 within manually inspected broad side-specific windows. Bright cores are not physical boundaries; uncertainty/bracket retained. Left/right independently measured, no forced mirror.','used_segments_y':[[125,174],[206,275]],'nulls':['175..205 main S and outer thin arc merge: center and S-only outer edge null','below275 and lower joint/terminal: not extrapolated','source02 upper/lower caps remain independent annotation null'],'rows':rows}
(Q/'observations/source05-visible-strips.json').write_text(json.dumps(out,indent=2));print('OBSERVATIONS_ONLY',sum(r['use_for_planar_shape_diagnostic'] for r in rows))
