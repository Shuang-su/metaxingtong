from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
groups={'forest-additional':['forest-3047.185491','forest-3050.458712'],'lakeleaf':['lakeleaf-92.142973','lakeleaf-100.762992','lakeleaf-108.755584']}
for names in groups.values():
 for n in names:
  rp=p/n/'report.json';r=json.loads(rp.read_text());ex=r['source']['exclusions'];ex.sort(key=lambda x:x['class']==1)
  m=Image.new('L',tuple(r['source']['size']));d=ImageDraw.Draw(m)
  for x in ex:d.polygon([tuple(pt) for pt in x['points']],fill=x['class'])
  m.save(p/n/'manual-exclusion-classes-source-grid.png');r['masks']['manual_exclusions']+=' Performer ROIs drawn last to preserve performer caution in overlaps.'
  for f in r['outputs']:
   q=p/n/f['path'];f.update(bytes=q.stat().st_size,sha256=sha(q))
  rp.write_text(json.dumps(r,ensure_ascii=False,indent=2))
notes={
'forest-additional':'''# 花岛增量真实相对深度分析
两帧官方 BV1ic12BMEk6 原生1920×1080，3047.185491低角、3050.458712高角。来源、哈希、停帧证据见各report.json。
实看原生及深度输出：3047低角暗倒锥在预测中成为连续近侧浅灰轮廓。这支持识别其投影轮廓，但不能解读内部材质、壁厚、距离或根部空隙；不能将其改为空根网。顶部树冠与花岛在预测中大面积合并，亮深度不是地板。3050高角预测把花环、草地及前景叶片平滑成片，只可作近远结构提示，不能按灰度雕刻逐花高度。角色和遮挡区域已保守标注。
保留所有失真输出，不以有限数值或平滑结果宣称几何验收。无米制尺度，无后续日期同场验证，无新增独立相机校准。
''',
'lakeleaf':'''# 叶舟三帧真实相对深度分析
官方 星瞳_Official BV1JqCeBMEAb，源说明表演日期2025-11-07、投稿2025-11-17，并非不同日期后续回放。实际解码3840×2160，最高菜单4K超高清；上游是否升频未知。处理92.142973、100.762992、108.755584，6.585758未推理，仅由建模者作辅助参考。
实看原生和模型输出：92侧全船轮廓被识别为相对近处，但水面被预测成强渐变的近侧表面，不能拿来重建湖底坡度、水深或接触线。100俯视将叶舟压成接近全白平片，细叶脉/角色深度几乎丢失，水下色块及反射不能当实体；它只帮助分开船与背景，不能验收壳厚和曲率。108近斜人物与舟体融为近侧浅灰，主脉略可见但不可量化。人物、水面/反射、背景树叶遮挡均有保守手工掩码。未标注不等于有效，无效/遮挡不能靠插值补成事实。
船两尖、凹曲面和主脉应以原生多视图及直接同机位叠图判断。深度不能证明浮力、接触、尺寸、运动或水深。三张输出全部保留，包括这些失败。
'''}
for group,names in groups.items():
 dest=Path('/workspace/shared')/f'depth-{group}-20261104';dest.mkdir(exist_ok=True)
 (dest/'analysis.zh.md').write_text(notes[group]+'''\n方法：官方Depth Anything V2 Small HF，revision5426e4f0f36572d16453bbda7a8389317b1bef99，CPU float32，实际raw518×924。大值/白通常近、小值/黑通常远，是相对逆深度类预测，不是普通图像亮度或真实距离。16位灰图与float32 NPY保留模型网格；source-grid输出是bicubic align_corners=False重采样，不是原生4K深度。各帧独立归一化不可跨帧当米制比较。全255confidence-unknown表示无校准置信度，不代表高可信。nonfinite为数值无效，dark mask仅原图RGB≤25的低信号提示，不是深度算法。手工ROI保守且不完整，0只是未标注。脚本、权重哈希、参数和版本在provenance与报告中。原生原图由sources目录保存，此包仅分析输出。\n''')
 for n in names:shutil.copytree(p/n,dest/n,dirs_exist_ok=True)
 (dest/'provenance').mkdir(exist_ok=True)
 for f in (p/'provenance').iterdir():
  if f.is_file() and (f.name.startswith(tuple(names)) or f.name in ['model-manifest.json','packages-freeze.txt']):shutil.copy2(f,dest/'provenance'/f.name)
 for f in ['run_depth_frame.py','run_additional_batch.py','package_additional.py']:shutil.copy2(p/f,dest/f)
 (dest/'model').mkdir(exist_ok=True)
 for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,dest/'model'/f)
 files=[{'path':str(f.relative_to(dest)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(dest.rglob('*')) if f.is_file() and f.name!='manifest.json'];(dest/'manifest.json').write_text(json.dumps(files,indent=2));print(dest,len(files),sum(f['bytes'] for f in files))
