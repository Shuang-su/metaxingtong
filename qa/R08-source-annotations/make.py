import json,hashlib,pathlib
from PIL import Image,ImageDraw
root=pathlib.Path(__file__).parent
src=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104/sources/report/15.png')
items=[]
def add(id,sem,pts,e,note,kind='polyline'):
 items.append(dict(id=id,semantic=sem,kind=kind,pixels=pts,subjective_error_px=e,notes=note))
add('P01','中央实体屋尖顶',[674,282],3,'尖端抗锯齿且背后星云，非大行星最高点。','point')
add('L01','左侧屋面实体外轮廓',[[674,282],[662,313],[643,328],[601,333],[564,344],[528,359],[517,367]],5,'屋尖至坡顶部分被装饰光环穿过；643,328附近实体/环线交叠，不宜作硬同点。')
add('L02','右侧屋面实体外轮廓',[[674,282],[687,314],[706,332],[747,341],[792,353],[833,365],[845,374]],5,'706,332附近白色绕环不是屋面，取暗色实体边，仍有歧义。')
add('L03','屋檐下方外沿左可见段',[[515,374],[546,377],[585,378]],4,'外侧水平撑臂遮住更低檐边，禁止把撑臂最左端当圆厅半径。')
add('L04','屋檐下方外沿右可见段',[[780,379],[815,378],[845,376]],4,'檐圈和撑臂近水平重叠，此段较短。')
add('L05','圆厅左墙体剪影可见段',[[502,409],[499,445],[498,483],[499,521]],4,'取墙体而不是更外侧细弯支撑；端部被底台连接遮。')
add('L06','圆厅右墙体剪影可见段',[[851,410],[853,447],[854,484],[854,523]],4,'右侧另有外置弯支撑到x874，不混同。')
add('L07','上部高装饰拱外轮廓',[[634,448],[642,430],[655,415],[675,405],[696,414],[710,431],[717,449]],4,'这是通行洞口上方装饰门面，不是实际开口顶部；中心星形饰物遮挡局部。')
add('L08','主通行洞口深色框外轮廓',[[630,539],[632,496],[637,474],[650,456],[675,446],[698,456],[713,474],[720,498],[720,540]],3,'外深框一条连续边；下方被独立近前拱遮挡，所列两端只是最后可见处，不是门脚。')
add('L09','主通行洞口内边',[[644,536],[643,497],[649,476],[660,465],[675,458],[691,465],[703,479],[709,497],[708,536]],4,'内边与室内结构/透视暗部局部低对比，不能和L08交替拟合同一拱。')
add('L10','近前拱最外上轮廓',[[600,624],[611,589],[632,560],[653,545],[677,541],[700,546],[724,563],[741,588],[752,621]],3,'独立前景拱；不是厅主门、不是舞台环。下端出画/与第二层叠合。')
add('L11','近前拱内轮廓可见上弧',[[625,604],[642,580],[659,567],[678,561],[698,567],[715,581],[730,604]],4,'内侧另有更低第二道拱与暗部，底端不标。')
add('L12','底台阶上部左外沿可见弧',[[489,526],[501,543],[527,556],[559,568],[596,576]],4,'选墙脚外台阶最上侧可见亮暗界；不是最外地面金环。中央被前拱遮。')
add('L13','底台阶上部右外沿可见弧',[[756,579],[789,571],[819,558],[850,543],[869,526]],4,'与L12是否严格同高同半径仍条件假说；右端多层台阶融合。')
add('N01','主门左实体门脚',None,None,'被近前拱遮挡，不外推。','unknown')
add('N02','主门右实体门脚',None,None,'被近前拱遮挡，不外推。','unknown')
add('N03','完整圆厅底台正前中心',None,None,'被近前拱、前景金星叠挡，不按对称造点。','unknown')
add('N04','屋檐完整椭圆背半部',None,None,'实体屋面遮挡，不能凭环状外观重建观测。','unknown')
data={'source':{'path':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'width':1192,'height':671,'type':'public report screenshot, not decoded native frame','video_time':None},'method':'Independent manual source-pixel inspection only. No model/render consulted. Coordinates original pixels x right y down; subjective errors are not statistically calibrated. Polyline samples describe visible image contours, not guaranteed known 3D point correspondences.','exclusions':['Planet silhouette and luminous orbit loops excluded from building geometry.','No scale from character.','No hidden symmetric completion.','Do not mix exterior decorative portal arch with entrance opening.'],'annotations':items,'fit_limit':'Camera-only fitting may use contours only after correct model semantic correspondence is separately established. Neither camera calibration nor geometric acceptance is claimed. Roof shoulder and base-ring semantic ambiguity must remain visible; do not discard poor-fit points silently.'}
(root/'annotations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
colors=['#ff5050','#ffbb00','#30e0ff','#60ff70','#ff55ff']
for i,a in enumerate(items):
 if a['pixels'] is None:continue
 c=colors[i%len(colors)];p=a['pixels'];p=[p] if a['kind']=='point' else p
 if len(p)>1:d.line([tuple(t) for t in p],fill=c,width=2)
 for x,y in p:d.ellipse((x-2,y-2,x+2,y+2),fill=c)
 x,y=p[0];d.text((x+4,y-11),a['id'],fill=c,stroke_width=1,stroke_fill='black')
im.save(root/'annotated-original-size.png')
(root/'README.zh.md').write_text('仅源图15的独立像素诊断，未看模型后调整。报道图1192×671，非原生视频帧，时刻未知。\n\n最重要的区分：高装饰拱顶y405、通行洞口深框外顶y446、洞口内顶y458、独立近前拱顶y541，不能交叉作为同一拱的对应点。圆厅墙体约x498至854；撑臂和外置曲撑不算墙体轮廓。屋尖约674,282，屋面肩部与发光环交叠的点允许误差5像素且仅条件使用。\n\n所有门脚/台基前中点被遮挡，保留null。左右台阶弧是否严格同一层仍未证。点段并不自动提供已知3D同点，camera-only拟合前必须另核语义映射。不得因拟合误差删除不利标点。inspection-2x.png仅局部2倍检查图，非更高分辨率来源。\n')
manifest=[]
for f in root.iterdir():
 if f.is_file() and f.name!='manifest.json':manifest.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(root/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(len(items),'entries',sum(1 if x['kind']=='point' else len(x['pixels'] or []) for x in items),'visible pixels')
