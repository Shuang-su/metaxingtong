from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
root=Path('/workspace/scratch/fa58bfcf0425'); src=root/'observatory-candidate-20261104/sources/report';out=root/'observatory-source-diagnosis-20261104'
D={}
def add(n,key,xy,label,status='visible',tol=4):
 D.setdefault(n,[]).append(dict(id=key,xy=xy,label=label,visibility=status,pixel_uncertainty_px=tol))
for key,xy,label in [('S1',[523,353],'四尖星上左外尖'),('S2',[801,410],'四尖星上右外尖'),('S3',[744,614],'四尖星下右外尖'),('S4',[344,510],'四尖星下左外尖'),('C1',[540,439],'左凹角'),('C2',[626,423],'后凹角，附近人物遮挡'),('C3',[687,470],'右凹角'),('C4',[567,499],'前凹角')]:add('13',key,xy,label,tol=4)
for key,xy,label,status in [('D1',[322,155],'左后拱门可见开口','partly_occluded'),('W1',[30,100],'左边裁切长窗/装饰面','cropped'),('W2',[639,84],'后壁长窗/装饰面','cropped'),('W3',[802,83],'后壁长窗/装饰面','cropped'),('W4',[985,97],'右后壁长窗/装饰面','cropped')]:add('13',key,xy,label,status,8)
for i,(x,y) in enumerate([(150,133),(472,124),(708,139),(880,148),(1084,166)],1):add('13','P'+str(i),[x,y],'可见柱带中段；不是该柱3D中心',tol=10)
for key,xy,label in [('S1',[461,280],'四尖星上左外尖'),('S2',[723,277],'四尖星上右外尖'),('S3',[779,410],'四尖星下右外尖'),('S4',[421,414],'四尖星下左外尖'),('C1',[521,336],'左凹角'),('C2',[594,308],'后凹角'),('C4',[594,367],'前凹角')]:add('21',key,xy,label,tol=5)
for i,(x,y) in enumerate([(401,41),(585,37),(749,40)],1):add('21','W'+str(i),[x,y],'后壁长窗可见下端，顶被图边裁切','cropped',9)
for i,(x,y) in enumerate([(296,72),(492,63),(667,66),(822,72)],1):add('21','P'+str(i),[x,y],'窗间柱带可见中段，不是3D中心',tol=10)
for key,xy,label,status in [('D1',[94,111],'左后开口可见片段','cropped'),('D2',[1080,94],'右后开口可见片段','cropped')]:add('21',key,xy,label,status,15)
for key,xy,label,status in [('D1',[595,264],'中心后方多层拱门，人物及发光翼遮挡','partly_occluded'),('A1',[594,97],'后大拱内沿顶点','visible'),('A2',[594,129],'套层拱内沿顶点','visible'),('W1',[19,175],'左裁切长窗/装饰面','cropped'),('W2',[1169,166],'右裁切长窗/装饰面','cropped'),('P1',[207,237],'左柱带中段','visible'),('P2',[989,235],'右柱带中段','visible'),('S1',[77,619],'地面四尖星左尖','visible'),('S2',[1121,619],'地面四尖星右尖','visible')]:add('14',key,xy,label,status,6)
for key,xy,label,status,tol in [('W1',[521,475],'最左窄窗残片，中上至下部可见','foreshortened_partial',6),('W2',[542,476],'左中长窗可见体中心','visible',4),('W3',[582,482],'左内长窗可见体中心','visible',4),('W4',[775,485],'右内长窗可见体中心','visible',4),('W5',[817,481],'右中窄长窗可见体中心','visible',5),('W6',[842,477],'最右窄窗残片','foreshortened_partial',7),('D1',[675,502],'正门可见开口中心，底被前景门环遮','partly_occluded',5),('D2',[499,481],'左侧边拱形细缝；开口性质待核','uncertain',8),('D3',[866,489],'右侧边拱形细缝；开口性质待核','uncertain',8),('P1',[612,473],'正门左宽竖柱带可见中段','visible',5),('P2',[733,476],'正门右宽竖柱带可见中段','visible',5),('R1',[675,280],'屋顶中央尖顶','visible',3),('R2',[517,374],'主屋顶檐左极限','visible',4),('R3',[845,375],'主屋顶檐右极限','visible',4),('B1',[462,391],'左外撑上转折圆节','visible',4),('B2',[423,430],'左外撑中折节','visible',5),('B3',[405,598],'左外撑底部主脚','visible',6),('B4',[902,392],'右外撑上转折圆节','visible',4),('B5',[946,426],'右外撑中折节','visible',5),('B6',[981,615],'右外撑底部主脚','visible',7),('A1',[678,563],'前景独立多层拱上顶','visible',4),('A2',[344,445],'左远平台独立拱顶','visible',4),('A3',[1060,452],'右远平台独立拱顶','visible',4)]:add('15',key,xy,label,status,tol)
notes={'13':'俯斜内景，四外尖均见；金属带有宽度，标外边界尖，不是内孔尖。后凹角近人物脚但不使用人物为地标。只见壁的一部分，不推全圆窗柱数。','14':'正面近景，人物及翼光遮拱下部。只见左右各1裁切面；无法由此计全窗数。星仅左右尖清楚，前尖出画、后尖被人物遮。','15':'前半实体可辨6条长窗：内侧四条较完整、最外两条窄残片。左右更外的黑拱缝另列不计窗；正门1。后半不可见，不推12窗或固定总分区。屋顶放射脊可见但大量重叠，不数全肋；中央尖顶上方/周围细环可见，不能凭单图判断是否独立悬浮。明确2侧外撑；前景3个独立拱组，远侧不可见。','21':'四尖而非五星。右凹角被粉发人物遮不标。三后窗只见下段；人物遮挡地面，不由对称补点。画面有字幕/水印及运动模糊，图像质量与13不同，风格差不能直接认定几何变更。'}
records=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for n,points in D.items():
 p=src/(n+'.png');im=Image.open(p).convert('RGB'); dr=ImageDraw.Draw(im)
 for q in points:
  x,y=q['xy'];color='#ffff00' if q['visibility']=='visible' else '#ff8844';dr.ellipse((x-3,y-3,x+3,y+3),outline=color,width=2);dr.text((x+5,y-15),q['id'],fill=color,font=font,stroke_width=2,stroke_fill='black')
 im.save(out/(n+'-annotated.png'))
 records.append({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size),'classification':'report screenshot; not native decoded frame; clip time unknown','coordinate_system':'original 1192x671 image, origin upper-left, x right y down; approximate manual points','notes':notes[n],'landmarks':points})
(out/'landmarks-v1.json').write_text(json.dumps({'version':1,'usage':'Diagnostic/fitting input, not blinded validation; no asserted 3D correspondences for apparent centers. All first points retained.','images':records},ensure_ascii=False,indent=2)+'\n')
(out/'README.zh.md').write_text('# 观星台来源原图独立诊断 v1\n\n四图均1192×671报道截图，非原生，时刻未知；没有新增视频解码或质量验收。坐标原图左上为0，单位像素；估计误差写在每个点，不能把装饰面可见中心当统一3D点。标注图保持原尺寸，原图SHA见JSON。\n\n'+ '\n\n'.join('## '+n+'\n'+notes[n] for n in ['13','14','15','21'])+'\n\n图案结论：13与21可见四个外尖，14只确认两横尖，不支持“五角星”标签。中心人物、翼光、字幕及截图压缩均不参与几何约束。crop文件仅为裁图后2倍最近检查视图，不是新增原生，也不用于坐标尺寸或分辨率声明。没有从对称性补不可见后墙、窗或结构。\n')
print('total points',sum(map(len,D.values())))
