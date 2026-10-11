from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,html,hashlib,zipfile,shutil
R=Path('/workspace/scratch/fa58bfcf0425/red_gold_stage_v1');Q=R/'qa';F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(F,24);small=ImageFont.truetype(F,18)
src=Image.open(R/'source/stage_2416s46_crop.png').convert('RGB');mat=Image.open(R/'renders/源图匹配_材质.png').convert('RGB');white=Image.open(R/'renders/源图匹配_白模.png').convert('RGB')
assert src.size==mat.size==white.size==(1180,664)
over=Image.blend(src,mat,.5);over.save(Q/'源图_材质_50%直接叠图.png')
canvas=Image.new('RGB',(1180,800),'#161b23');d=ImageDraw.Draw(canvas)
for i,(label,im) in enumerate([('来源 2416.456秒｜360p解码截图',src),('材质版｜同一固定几何，比例推定',mat),('白模版｜无人物，不做遮挡补证',white),('50%直接叠图｜未扭曲源图',over)]):
 x=(i%2)*590;y=(i//2)*400;d.text((x+12,y+10),label,font=small,fill='white');canvas.paste(im.resize((590,332)),(x,y+43))
canvas.save(Q/'源图_材质_白模_直接叠图.jpg',quality=94)
views=['正面全景','左前','右前','左侧','右侧','背面','左后','右后','俯视','底面'];canvas=Image.new('RGB',(1182,4*262),'#161b23');d=ImageDraw.Draw(canvas)
for i,v in enumerate(views):
 x=(i%3)*394;y=(i//3)*262;im=Image.open(R/'renders'/f'{v}_材质.png').convert('RGB');canvas.paste(im.resize((394,222)),(x,y+35));d.text((x+10,y+6),v+('｜诊断补光，固定几何' if v=='底面' else '｜完整固定几何'),font=small,fill='white')
sect=R/'renders/明确剖切_X0_诊断.png'
if sect.exists():
 im=Image.open(sect).convert('RGB');canvas.paste(im.resize((394,222)),(394,3*262+35));d.text((404,3*262+6),'X=0明确剖切｜仅诊断',font=small,fill='#ffc57a')
canvas.save(Q/'完整舞台_多视检查总览.jpg',quality=94)
for p in (R/'renders').glob('*.png'):
 if p.stem.endswith('_clean'):continue
 clean=p.with_name(p.stem+'_clean.png')
 Image.open(clean if clean.exists() else p).convert('RGB').save(p.with_suffix('.jpg'),quality=91)
j=json.load(open(Q/'geometry_validation.json'));stat=j['textured']['source'];roundtrip=j['textured'];content=f'''<!doctype html><meta charset="utf-8"><title>红金拱形舞台检查</title><style>body{{background:#161b23;color:#eee;font:17px/1.7 sans-serif;max-width:1250px;margin:40px auto;padding:20px}}img{{max-width:100%;border:1px solid #485366}}h1,h2{{color:#edbe76}}.note{{background:#293440;padding:20px}}a{{color:#ffc977}}</style><h1>红金灯泡拱形舞台 · 首个可核实版本</h1><p class="note">有限舞台资产：正面形体以来源为据；进深、背部支撑、上缘与地面边界为推定。不是完整宴会厅复原，没有已证实左右独立相机基线。</p><h2>来源与直接比对</h2><p><a href="https://www.bilibili.com/video/BV1BvsfenED7/">视频来源</a>：彩色较宽正面 2416.456244秒。640×360解码，1180×664原比例截图。人物未重建。黑白插播仅辅助看形，不能当作同一灯光。新1080尝试没有取得稳定有效新帧。</p><img src="qa/源图_材质_白模_直接叠图.jpg"><p>四图均同尺寸，不做透视变形或不等比拉伸。单机位近似匹配，误差与遮挡保留展示，不宣称像素级精确复原。</p><h2>普通观察与明确剖切</h2><img src="qa/完整舞台_多视检查总览.jpg"><p>所有普通视图保持同一固定几何，相机按完整包围盒后退，不裁掉顶部或支脚。底面额外使用诊断补光，不改几何。只有明确标注的X=0剖切是独立诊断副本。</p><h2>几何与可移植性</h2><ul><li>{stat['mesh_objects']}个闭合网格，{stat['triangles']:,}个三角面；零退化、零异常法线、零非流形边。</li><li>双GLB从干净Blender场景真实回导，三角数一致；最大双向顶点差 {roundtrip['symmetric_vertex_distance_units']:.3g}。</li><li>材质/白模顶点完全相同。材质GLB内嵌256×256红漆纹理；白模无纹理。</li><li>正面/地面/拱接缝共15,411条射线无漏；{j['lamp_back_pole_contacts']['count']}个翼灯背极均接触金框。</li><li>帘顶嵌入实体悬梁，悬梁接双柱并落于台面；星饰背面通过安装座连景板；背支架与台面装配相接。</li></ul><p>必要的安装嵌入/交叠不等于全体布尔成一个实体。接触检查不是结构承载认证。独立核验另见 independent/geometry_checks.json：279件真实装配单连通，234颗全部灯泡前后几何通过，7904条限定目标接缝射线无漏。三段候选实体级差与金色鼻口区分；亮线不另算一级。</p><h2>未证实范围</h2><p>绝对尺寸、后台结构、深度、未入镜星尖和布景外边界。材质与灯光是近似解释；未增加宴会桌、天花或宴会厅。没有查证到本场已发布旧模型，不虚构版本历史。</p><h2>独立复核</h2><p><a href="independent/独立核验报告.md">独立中文核验报告</a>：几何、装配和有限资产交付通过；源匹配仅比例近似，不作为高精度复刻。</p><h2>逐项原始检查</h2><p><a href="qa/geometry_validation.json">几何、射线、真实回导JSON</a> · <a href="README_红金拱形舞台.txt">中文说明</a></p>'''
(R/'红金舞台_核验报告.html').write_text(content)
