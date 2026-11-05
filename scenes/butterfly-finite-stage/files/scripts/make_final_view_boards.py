from PIL import Image,ImageDraw,ImageFont,ImageStat
import pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
labels=['左前：膜和脉络','右前：同一共享几何','左斜侧：有限厚度','右后侧：开放片段','左后：推断闭合','右后：非来源背面','高俯：有限台板','低前：台厚代理']
out=P/'renders/R04D_summary';out.mkdir(exist_ok=True)
report=[]
for tag,zh in [('white','白模'),('material','材质')]:
 fs=sorted((P/'renders/R04D_checks').glob(f'{tag}_CHECK*.png'));assert len(fs)==8
 board=Image.new('RGB',(1192,4*374+85),(20,23,31));d=ImageDraw.Draw(board)
 d.text((18,12),f'有限冷态蝴蝶前侧候选｜{zh}8个模型检查角｜来源FAILED',font=font,fill=(243,244,250))
 d.text((18,47),'侧背厚度/台板边界为推断；不是8个来源角，不证明完整舞台/城市或真实背面。',font=small,fill=(201,210,225))
 for i,f in enumerate(fs):
  im=Image.open(f).convert('RGB');assert im.size==(1192,671)
  report.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':im.size,'rgb_stddev':ImageStat.Stat(im).stddev,'camera_index':i+1,'mode':tag})
  x=i%2*596;y=85+i//2*374;d.text((x+12,y+5),f'{i+1:02d}  {labels[i]}',font=small,fill=(230,234,244));board.paste(im.resize((596,336),Image.Resampling.LANCZOS),(x,y+32))
 board.save(out/f'{tag}-eight-checks.zh.jpg',quality=94)
# Compact source overview. Only this overview is a resized display derivative;
# direct50 PNGs remain unchanged-size 1192x671 with no image registration.
board=Image.new('RGB',(1192,2*374+85),(20,23,31));d=ImageDraw.Draw(board)
d.text((18,12),'冷态蝴蝶前侧有限候选｜可编辑真薄壳｜来源FAILED',font=font,fill=(243,244,250))
d.text((18,47),'源02报道图非原生视频；下列缩图仅概览，原尺寸直接50%叠图另附。',font=small,fill=(201,210,225))
items=[('sources/report-02.png','真实来源02：1192×671报道图'),('renders/R04_source/white_SOURCE02_conditional_front.png','白模：共享3D、条件相机'),('renders/R04_source/material_SOURCE02_conditional_front.png','材质近似：生成色区，不是原纹理'),('renders/R04_direct_comparison/source02_white_direct50.png','直接50%：无配准/扭曲，仍FAILED')]
for i,(name,label) in enumerate(items):
 im=Image.open(P/name).convert('RGB');x=i%2*596;y=85+i//2*374;d.text((x+12,y+5),label,font=small,fill=(230,234,244));board.paste(im.resize((596,336),Image.Resampling.LANCZOS),(x,y+32))
board.save(out/'finite-candidate-overview.zh.jpg',quality=94)
(out/'formal-image-check.json').write_text(json.dumps(report,indent=2))
print('FORMAL16_BOARDS_COMPLETE',len(report))
