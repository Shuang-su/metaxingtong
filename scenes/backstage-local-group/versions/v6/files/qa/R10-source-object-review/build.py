from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
p=Path(__file__).parent;s=Path('backstage-local-study-20261105/sources')
a={}
def ob(i,b,shape,e=4,occ='none visible',cross=None):return dict(id=i,bbox_visible=b,shape_color=shape,subjective_error_px=e,occlusion=occ,cross_image_id=cross)
a['009']=[
ob('D01',[327,99,578,297],'黑色提手面板设备；类别未证，疑收录机。禁止沿旧名直接称化妆箱',5,'右下受前臂遮挡'),
ob('D02',[365,116,542,179],'D01顶部抬起的长条提手；非独立物',4),
ob('D03',[353,201,459,282],'D01前面左侧大深色矩形面板/疑网罩，细网纹不可辨',7),
ob('D04',[467,179,545,201],'D01前面右上横向细亮刻度/条带，字符不可辨',6),
ob('D05',[543,180,563,245],'D01右侧竖列圆形暗钮区域，可见约3处圆斑；最下边不清',6),
ob('D06',[411,162,446,182],'D01顶部3个小亮矩形键/条，不是瓶',4),
ob('B01',[92,326,264,408],'米白圆珠串折叠成多段环，至少两回弯；是一条还是多条不能定',4),
ob('B02',[28,243,72,322],'左缘红色肩/红顶暗瓶可见部分',8,'黑暗融合，底界弱'),
ob('B03',[680,120,721,175],'奶白上口暗筒，顶部有暗芯，疑蜡烛；不确定功能',4),
ob('B04',[1080,71,1163,161],'奶白纵向棱纹圆鼓瓶，顶有圆钮/瓶塞',5,'底部深暗'),
ob('B05',[989,86,1045,147],'右后奶白顶暗筒，疑蜡烛',7,'深暗'),
ob('B06',[235,220,295,269],'设备左侧小黑色条带物，可见多条白竖线；不强定梳子/瓶',7),
]
a['011']=[
ob('C01',[375,525,513,597],'红色圆角矩形电子钟，灰白面和深色数字20可见',3,'右部被手和衣袖遮挡，完整宽度未知'),
ob('C02',[338,502,380,565],'米白纵棱鼓瓶，颈部圆钮；完整底被前瓶遮挡',3,'下部遮挡','009:B04 candidate only'),
ob('C03',[250,483,305,543],'白/米色方肩短颈容器，左上有灰色瓶盖区域；可能前后两物，实例数未定',5,'前方黑/红物遮挡'),
ob('C04',[211,548,247,605],'前排银亮矮圆筒/杯，顶缘可见',3),
ob('C05',[214,530,231,561],'红色短柱/圆帽与暗细身',3,'下部在银筒后，可能其内物'),
ob('C06',[241,507,272,583],'黑色直立体带红色方块/细条；瓶/口红功能未证',4,'邻物重叠'),
ob('C07',[262,580,299,601],'银透明矮圆罐，深色顶面',3),
ob('C08',[299,582,328,601],'青蓝小圆润扁体，向右收尖；非直立瓶',3),
ob('C09',[301,529,329,580],'暗棕细瓶/管，顶部有金色亮斑',4,'仅局部，和后方扩香器有遮挡'),
ob('C10',[329,548,348,580],'黑色短圆筒亮顶，靠白棱瓶前',3),
ob('C11',[346,551,361,580],'红边暗短筒',3),
ob('C12',[351,578,365,602],'浅粉细小直立体',4,'柔焦，类别未证'),
ob('C13',[298,439,357,551],'棕细长杆束及暗瓶座，疑扩香棒；杆数不可数全',5,'杆束相交/暗处融合'),
ob('C14',[205,398,308,508],'暗色枝叶/小花束与绿瓶颈，下界遮挡',7),
ob('C15',[142,461,162,553],'青绿尖锥局部',5,'前景深色竖物遮挡'),
ob('C16',[167,411,216,671],'前景深青绿高长体；顶/底裁切和暗部不清，不用其全形定瓶',9,'底出画且遮挡后物'),
ob('C17',[345,637,404,671],'近前黑盖圆罐上部',4,'底出画'),
ob('C18',[311,640,347,671],'近前奶白珠状链小段',5,'出画/罐遮挡','009:B01 candidate only'),
ob('C19',[0,380,138,671],'左缘镜旁暗物集合，反射/前景实体无法逐个区分；不计实例',12,'暗部、裁切、镜像混合'),
]
polys={'009':{'device_top_outer':[[328,165],[541,111],[573,153],[345,209]],'device_front_left_panel':[[355,218],[451,196],[457,262],[361,282]],'bead_visible_path':[[96,369],[117,390],[151,401],[193,400],[229,389],[254,367],[258,354],[243,345],[214,350],[176,358],[144,368],[139,376],[169,378],[198,368],[234,350],[242,338],[231,333],[207,339],[182,337],[155,330]],'top_bright_keys_centers':[[416,176],[430,172],[442,169]]},'011':{'clock_visible_outer':[[378,539],[387,528],[449,527],[455,536]],'clock_visible_bottom':[[378,583],[389,592],[469,593]],'clock_face_visible':[[391,538],[445,538],[447,580],[390,580]]}}
records=[]
for n,obs in a.items():
 f=s/f'backstage-{n}.png';im=Image.open(f);d=ImageDraw.Draw(im)
 for j,o in enumerate(obs):
  c=['#ffdc40','#00ffff','#ff70ed','#7cff62'][j%4];d.rectangle(o['bbox_visible'],outline=c,width=2);d.text((o['bbox_visible'][0],max(0,o['bbox_visible'][1]-12)),o['id'],fill=c,stroke_width=1,stroke_fill='black')
 for k,pts in polys[n].items():
  if 'centers' in k:
   for x,y in pts:d.ellipse((x-2,y-2,x+2,y+2),fill='white')
  else:d.line([tuple(x)for x in pts],fill='white',width=1)
 im.save(p/f'{n}-annotated.png')
 records.append(dict(source=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),dimensions=im.size,kind='report screenshot, not native frame',frame_time=None,objects=obs,visible_polylines=polys[n]))
(p/'annotations.json').write_text(json.dumps(dict(method='manual source-only v1; bbox visible extent, not full-object geometry; no model consulted',error='subjective pixel uncertainty, not calibrated confidence',records=records,cross_image_policy='Only cream fluted bottle and bead section are tentative candidates. No forced identity of bottles or 17-model indices. Mirrors are not duplicated.'),ensure_ascii=False,indent=2))
