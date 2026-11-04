from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
p=Path(__file__).parent;s=Path('early-technical-source-20261104');src=[]
for f,g,i,t in [('a05-frame000.png','a05.img',0,0),('a05-frame017.png','a05.img',17,1360),('a05-frame035.png','a05.img',35,2800),('key-a15-frame110.png','a15.img',110,8800),('key-a16-frame027.png','a16.img',27,2160),('key-a16-frame107.png','a16.img',107,8560)]:
 b=(s/f).read_bytes();im=Image.open(s/f);src.append(dict(file=str(s/f),frame_sha256=hashlib.sha256(b).hexdigest(),gif=str(s/g),gif_sha256=hashlib.sha256((s/g).read_bytes()).hexdigest(),frame_index=i,gif_elapsed_ms=t,dimensions=im.size,video_time=None,native_livestream_frame=False))
obs=[
 dict(component='最前两个交错框',blue='0/17/35可见一条偏灰金属矩形框及一条白亮斜框，顶部交叉、下端开口受地面和人物遮挡',red='15/110和16/27、107可见金属灰框和白亮斜框组合，人物遮中心',conclusion='组合相似；宽度、厚度、真实角度/深度均未标定，不可当同mesh证明',correspondence='motif only'),
 dict(component='内层错转框',blue='35中心内层低亮度，数条黑/蓝边重叠；前框遮上边，人物遮左下，无法可靠数出封闭框数量',red='27小到单边1–2px，107可见多层但相互重叠且人物遮挡',conclusion='逐框ID和全层数null；不可从红多白线/蓝少黑线推增删框',layer_count=None,rotation_sequence=None),
 dict(component='接缝/支承',blue='0右下角可见金属折角；35右下可见前框端部，但没有螺栓/明确与后框连接件',red='320像素GIF角部压缩锯齿明显，无法确认同接缝',conclusion='无足以唯一识别的接缝对应',joint_id=None),
 dict(component='顶弧檐与上部',blue='0白亮弧边上方深蓝星点及细分隔线；35已出画',red='27白色宽弧檐上有深色透明/格条高位带',conclusion='共享弧厅设计。弧半径、厚度、格数及同一构件身份未知'),
 dict(component='侧壁柱/灯',blue='35左右细白竖灯条，周围深蓝宽壁；0斜视可见深色凸出竖面',red='27左右宽浅色柱，另红色侧屏带深圆口或圆饰及银球',conclusion='实际装配外观不同；可能不同装修或不同几何，不能只当换色'),
 dict(component='地面/底缘',blue='35前景蓝色曲线台面边缘有连续白灯带，两侧晶簇花床；0边缘斜向露侧面',red='27浅地面直线灯纹或线纹，红枝饰与礼物和红盘',conclusion='可见地面轮廓与附属物不同，不可把蓝曲台边套红室'),
 dict(component='局部人物与舞台身份',blue='精确HTML将a05紧接星瞳热舞文字，已确认星瞳',red='腾讯游戏学堂采访GIF及画面Official水印，明确星瞳演出素材；具体演出日期未知',conclusion='角色身份不是同场/同mesh证明')]
(p/'comparison.json').write_text(json.dumps(dict(method='independent source-only visual comparison v1; no model or rendered comparison inspected',sources=src,observations=obs,decision='Only shared design motif is established. Same underlying geometry not demonstrated. Exclude blue a05 from red dark-state geometry fit/acceptance.',allowed_use=['可说明设计家族相似','可独立研究蓝场，需另排重/来源核验'],disallowed_use=['迁移蓝场尺寸/框数/曲台边作为红场已见几何','把a05更高GIF分辨率当红场原生补源','用角色/衣装相似代替同场身份']),ensure_ascii=False,indent=2))
# Comparison contact sheet is diagnostic only, both originals retained at cited paths.
o=Image.new('RGB',(1050,690),'#202020');d=ImageDraw.Draw(o)
for j,r in enumerate(src):
 im=Image.open(r['file']).convert('RGB');im.thumbnail((510,200));x=(j%2)*525;y=(j//2)*230;o.paste(im,(x,y));d.text((x,y+202),Path(r['file']).name+' | original '+str(r['dimensions']),fill='white')
o.save(p/'comparison-contact.png')
