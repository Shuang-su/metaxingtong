from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent;d=Path('/workspace/shared/depth-observatory-report-20261104');d.mkdir(exist_ok=True)
for n in [13,14,15]:shutil.copytree(p/f'report-image-{n}',d/f'report-image-{n}',dirs_exist_ok=True)
shutil.copytree(p/'provenance',d/'provenance',dirs_exist_ok=True)
(d/'sources').mkdir(exist_ok=True)
for n in [13,14,15]:shutil.copy2(p.parent/f'observatory-candidate-20261104/sources/report/{n}.png',d/'sources'/f'{n}.png')
shutil.copy2(p.parent/'observatory-candidate-20261104/sources/source-manifest.json',d/'sources/source-manifest.json')
for f in ['run_depth.py','run_batch.py','fetch_model.py','package_results.py']:shutil.copy2(p/f,d/f)
(d/'model').mkdir(exist_ok=True)
for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,d/'model'/f)
(d/'analysis.zh.md').write_text('''# 观星台报道截图相对深度分析：非原生来源、未验收
处理报道https://www.bilibili.com/opus/937708347092631557 的13/14/15图，2024-05-31演出报道，原字节1192×671。官方完整回放BV1tZ421H714仅作为来源关联。片内时间全部未知，原视频解码尺寸、登录最高画质未验证；不能把此包标作原生视频帧深度完成。网站图像地址带@1192w，不声称上游原生像素。原图及SHA、网站图URL已保留；未改写来源或补造时间。
## 真实方法及参数
使用官方Depth Anything V2 Small HF，revision5426e4f0f36572d16453bbda7a8389317b1bef99，safetensors权重SHA3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70。CPU单线程float32，local_files_only=True，trust_remote_code=False，版本/处理器参数/输入输出尺寸/范围见各report.json。模型网格float32 NPY和16位灰度保留，截图网格由bicubic align_corners=False派生，并非1192×671独立高分辨率深度。
模型输出是相对逆深度类预测：大值/白通常近，小值/黑通常远，不是普通亮度图，也不是真实米制距离。逐图minmax归一化，不能跨图直接比较距离或缩放。源码、依赖freeze、安装日志、官方权重哈希和获取脚本齐全；模型权重不在结果包，按脚本从官方固定revision取并验哈希。
## 原图与输出实看结果
13高角：室内柱/门/星形地饰几乎消失，地面与反射被平滑成强近远渐变，仅角色轮廓稍突出。这是细部结构失效，不能据灰度认地面坡度、星形厚度、柱径或开口深度。
14前角：角色成为近侧完整浅灰团块，光翼大部分消失；门拱可见粗投影，但墙体/镜面地仍被大幅简化。光翼不是实体墙，脚下镜像不能当另一个人或几何凹槽，不能用此结果决定足底接触与门墙厚度。
15外观：建筑和两侧支架有相对轮廓，前景拱门最亮，但模型也给星空行星分配表面深度。背景行星/宇宙是不可校准图像内容，不能作为建筑距离和尺度基准。屋顶肋条/支架厚度/内外开口仍丢失，不作为几何验收。
所有失败输出保留。三图仅作可视化空间排序辅助，不能替代原生多角、相机匹配、逐物体核对或直接50%叠图，也未建立后续不同日期同场验证。
## 掩码
人工保守ROI：1人物/遮挡，2镜面地与反射，3星空/行星/背景开口，4光翼/光束等非实体特效。后绘覆盖前绘，区域不精确且不完整，0未标注不是有效认证。暗部掩码只是原图RGB全部≤25的低信号提示，不是深度算法。nonfinite掩码255是数值无效，0仅数值有限，不证明几何有效；confidence-unknown全255表示没有校准置信度，绝非高可信。隐藏结构未知，禁止填成事实。
''')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
for n in [13,14,15]:
 r=json.loads((d/f'report-image-{n}/report.json').read_text());assert sha(d/f'sources/{n}.png')==r['source']['sha256'];print(n,r['method']['raw_shape'],r['range'])
print(d,len(files),sum(f['bytes'] for f in files),'hash readback PASS')
