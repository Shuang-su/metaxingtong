from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent;d=Path('/workspace/shared/depth-seaside-arch-20261105');d.mkdir(exist_ok=True)
for n in ['03','04']:shutil.copytree(p/f'report-image-{n}',d/f'report-image-{n}',dirs_exist_ok=True)
shutil.copytree(p/'provenance',d/'provenance',dirs_exist_ok=True);shutil.copy2(p.parent/'depth-observatory-20261104/provenance/packages-freeze.txt',d/'provenance/packages-freeze.txt');(d/'sources').mkdir(exist_ok=True)
for n in ['03','04']:shutil.copy2(p.parent/f'stargravity-report-source-20261104/{n}.webp',d/f'sources/{n}.webp')
for f in ['reviewed-originals.json','review.zh.md','official-aini.json']:shutil.copy2(p.parent/'seaside-arch-screening-20261105'/f,d/'sources'/f)
for f in ['run_depth.py','run_batch.py','package_results.py']:shutil.copy2(p/f,d/f)
shutil.copy2(p.parent/'depth-observatory-20261104/fetch_model.py',d/'fetch_model.py');(d/'model').mkdir(exist_ok=True)
for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,d/'model'/f)
(d/'analysis.zh.md').write_text('''# 2023海滨三拱台03/04真实相对深度：有限辅助，未验收
仅处理03正宽和04轻偏侧，原图1192×671报道WEBP，https://www.bilibili.com/opus/800724230600654921。事件2023-05-27，官方爱你BV1mP411Q7kc只身份桥。片内时刻、最高实际解码质量及视频像素未知，非原生视频帧。06/07为不同合演状态，本轮不推理、不纳几何源。来源表含其他图仅背景记录，不表示都使用。
方法为官方Depth Anything V2 Small HF，固定revision5426e4f0f36572d16453bbda7a8389317b1bef99，CPU单线程float32，实际raw518×924。raw NPY/模型网格16bit灰图保留；截图网格是bicubic align_corners=False派生，不是独立原生分辨率预测。版本、模型权重SHA、参数、实际形状、范围见report。白/大值通常近，黑/小值通常远，相对逆深度类预测不是普通亮度、更非米制距离；独立归一化不可跨图测距。
## 原图与结果实看
03：粗层次中左亭、后拱、右伞椅和人物可分，但蓝墙圆灯/矩窗几乎全被压成平面，黑金多拱的金边/层间细节消失，中央演员与翼标和背景融合。不能从灰面推出墙厚/窗深或确切拱间距；舞者足部接触及近地面高度无依据。
04：比03只有轻偏侧，不是充分侧向基线。模型保留粗拱和椅桌投影，但椅杆/桌脚交叉边融合，圆灯和矩窗继续丢失，人物、粒子及其脚下反射影响地面梯度。不能由这些光滑灰面添加实体台阶，不能将反射影子建第二个人或把圆灯平滑成墙体凸凹。
两图只能提示粗遮挡顺序，不能恢复亭深、隐藏后方、伞架精确接触、场地闭合墙顶或实际尺度。失败输出全部保留；原生多视角、逐物体核对与同机位直接叠图尚不可由此替代，后续同场验收未成立。
## 掩码
1人物/伴舞，2反光台面，3天空/发光背景/粒子，4标字/章节/水印。人工保守ROI不完整，天空警戒部分覆盖拱实体，不作删除结构指令；0未标注不是有效，遮挡后未知。暗部mask仅原RGB各≤25低信号提示，不是深度算法。confidence-unknown全255表示没有校准置信度，非高可信；nonfinite0仅数值有限，非几何有效。未从像素推米制距离。
''')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and not(f.parent==d and f.name=='manifest.json')];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
for n in ['03','04']:
 r=json.loads((d/f'report-image-{n}/report.json').read_text());assert sha(d/f'sources/{n}.webp')==r['source']['sha256'];print(n,r['range'],r['method']['raw_shape'])
print(d,len(files),sum(f['bytes'] for f in files),'hash readback PASS')
