from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent;d=Path('/workspace/shared/depth-corridor-report-20261104');d.mkdir(exist_ok=True)
for n in ['008','023','026']:shutil.copytree(p/f'report-image-{n}',d/f'report-image-{n}',dirs_exist_ok=True)
shutil.copytree(p/'provenance',d/'provenance',dirs_exist_ok=True);shutil.copy2(p.parent/'depth-observatory-20261104/provenance/packages-freeze.txt',d/'provenance/packages-freeze.txt')
(d/'sources').mkdir(exist_ok=True)
for n in ['008','023','026']:shutil.copy2(p.parent/f'stardream-report-20261104/{n}.png',d/'sources'/f'{n}.png')
shutil.copy2(p.parent/'stardream-report-20261104/image-links.json',d/'sources/article-image-links.json')
for f in ['run_depth.py','run_batch.py','package_results.py']:shutil.copy2(p/f,d/f)
shutil.copy2(p.parent/'depth-observatory-20261104/fetch_model.py',d/'fetch_model.py');(d/'model').mkdir(exist_ok=True)
for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,d/'model'/f)
(d/'analysis.zh.md').write_text('''# 星梦游走廊报道图相对深度分析：非原生、未验收
来源报道https://www.bilibili.com/opus/961640175446786069，DD于2024-08-04报道2024-08-03星梦游三周年。008/023/026为1192×671网站图，非原生视频帧。片内时刻、解码像素和登录最高画质未知。本分析未独立核对官方BV、时间连续性或新场景排重，不能作为这些条件完成的证明。原图原字节及逐图哈希保留。
官方Depth Anything V2 Small HF固定revision5426e4f0f36572d16453bbda7a8389317b1bef99，CPU单线程float32，raw518×924。模型权重哈希、版本、预处理参数、实际输入输出/范围见report.json。raw float32 NPY及16bit灰图保留，截图网格输出是bicubic align_corners=False派生，不是原生分辨率独立深度。白/大值通常较近、黑/小值较远，相对逆深度类预测不是普通亮度、更非米制距离；独立归一化不得跨图当真实距离。
## 实看三图及深度
008朝ON AIR端门的广角只保留箱状空间大轮廓与人物/熊的相对遮挡。壁灯、门缝、顶灯分格大部分消失，端门被压成黑平面。不得按黑度推出门洞深度、墙厚、走廊长度或脚底接触；未看到部分不补为事实。
023斜低角保留大致侧墙/地面透视，角色遮挡了关键结构，顶灯和壁灯被严重平滑，彩光与反射不能改变几何。模型的连续梯度不是墙面弯曲或地面坡度证据，视角斜切不证明场景不方正。
026是横看侧墙近景，深度几乎整面墙同值，只保留人物及地面的近远。它不是反向整房，也不能推断对端门、房长、反向相机或灯总数。颜色变化不作为墙材质/厚度/位置改变。
所有失败输出保留，不以视觉顺滑或nonfinite为0宣称正确。单目相对深度不能验收米制尺寸、隐藏结构、接触、相机或后续同场。需原生多视角、逐物体核对和同机位直接叠图。
## 掩码
1人物/熊遮挡，2地面反射及暗部警戒，4动态彩光/光晕。全部为人工保守不完整ROI，后绘覆盖先绘，0未标注不表示有效；彩光ROI仍包含真实墙面，不是删除整墙。独立dark mask为原RGB全部≤25，亮度筛选只是低信号提示，不能冒充深度。全255confidence-unknown表示没有校准置信度，不是高可信；nonfinite255表示数值无效，0仅数值有限。未知遮挡后结构不得捏造。
本包未编辑生产Git/模型；排重及原生来源验收由独立任务继续。\n''')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
for n in ['008','023','026']:
 r=json.loads((d/f'report-image-{n}/report.json').read_text());assert sha(d/f'sources/{n}.png')==r['source']['sha256'];print(n,r['range'],r['method']['raw_shape'])
print(d,len(files),sum(f['bytes'] for f in files),'hash readback PASS')
