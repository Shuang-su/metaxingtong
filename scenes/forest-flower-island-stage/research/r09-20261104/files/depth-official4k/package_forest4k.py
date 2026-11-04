from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent;d=Path('/workspace/shared/depth-forest-official4k-20261104');d.mkdir(exist_ok=True)
for t in ['501.149406','503.06141']:
 n=f'forest-official4k-{t}';shutil.copytree(p/n,d/n,dirs_exist_ok=True)
(d/'provenance').mkdir(exist_ok=True)
for f in (p/'provenance').iterdir():
 if f.is_file() and (f.name.startswith('forest-official4k-') or f.name in ['model-manifest.json','packages-freeze.txt']):shutil.copy2(f,d/'provenance'/f.name)
shutil.copy2(p.parent/'source-newscene-20261104/official4k-capture-manifest.json',d/'provenance/source-manifest.json')
for f in ['run_depth_frame_cpu1.py','run_forest_official4k.py','package_forest4k.py']:shutil.copy2(p/f,d/f)
(d/'model').mkdir(exist_ok=True)
for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,d/'model'/f)
(d/'analysis.zh.md').write_text('''# 官方森林4K两帧真实相对深度补充
仅处理501.149406低角及503.06141整岛俯视。来源星瞳_Official BV11jCEBiEwE，2025-11-12投稿的2025-11-07同场演出剪辑，不是后续不同日期复用验收。独立剪辑时间轴，不声称与旧1080源逐帧对应。505及517没有处理。
原图实际3840×2160、菜单最高4K、Chrome原生保存、前后paused/ready4/时间一致证据及SHA均在report/source manifest。上游是否升频未知。原图保留于场景sources，不在分析包重复存储。
真实模型Depth Anything V2 Small HF，固定revision5426e4f0f36572d16453bbda7a8389317b1bef99，CPU float32，线程1，实际raw518×924。较大值/白通常近，较小值/黑通常远，是相对逆深度类预测，不是普通亮度或米制距离。源网格4K NPY/8bit由bicubic align_corners=False重采样，绝非4K独立深度预测；模型网格float32及16bit一并保留。不能跨帧用独立归一化灰度比距离。
实看原图及输出：501低角模型确保留连续倒锥的投影轮廓，但与花冠和右侧近叶融成平滑浅灰块，底部体积、材质、表面厚度和细根空洞不可恢复。不能把暗色倒锥改为空根架，也不能把亮深度树冠当平地。503俯视整岛成为中灰平滑团块，人物和花环内部差异大量丢失；右下遮挡叶片更白只代表模型预测较近，不表示岛上更高或支撑关系。原生花环位置比深度可靠。失败输出完整保留。
掩码：手工类别1人物、2可能翼光/光束、3林叶遮挡及雾光、4暗底形状不明。保守ROI不完整，0未标注不是有效认证。dark-low-signal为原始RGB各通道≤25提示，不是深度方法。全255confidence-unknown表示无校准置信度，非高可信；nonfinite=0仅数值有限，非几何有效。隐藏结构未知。
不能据此验收米制尺寸、接触、相机匹配、运动、逐物体几何或后续同场。仍需多视角与直接50%叠图；本包未修改模型或生产Git。\n''')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
for f in d.glob('*/report.json'):
 r=json.loads(f.read_text());assert sha(Path(r['source']['path']))==r['source']['sha256'];print(f.parent.name,r['range'],r['method']['forward_seconds'],r['method']['threads'])
print(d,len(files),sum(f['bytes'] for f in files),'hashes PASS')
