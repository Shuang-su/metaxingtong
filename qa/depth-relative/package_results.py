from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent;s=p.parent/'early-technical-source-20261104';d=Path('/workspace/shared/depth-twistframe-gif-20261104');d.mkdir(exist_ok=True);names=['key-a15-frame110','key-a16-frame027','key-a16-frame107','key-a18-frame000']
for n in names:
 rp=p/n/'report.json';r=json.loads(rp.read_text());r['method']['low_resolution_note']='Actual source320x176 -> processor/model518x280 is upsampling; no new observed detail. Source-grid derived output is back-resampling to320x176.';r['source']['time_basis']='gif_elapsed_ms is GIF cumulative time only, NOT live-video time';r['limitations'][0]='Article GIF decode is NOT logged-in highest-quality native live-video frame';rp.write_text(json.dumps(r,ensure_ascii=False,indent=2));shutil.copytree(p/n,d/n,dirs_exist_ok=True)
shutil.copytree(p/'provenance',d/'provenance',dirs_exist_ok=True);shutil.copy2(p.parent/'depth-observatory-20261104/provenance/packages-freeze.txt',d/'provenance/packages-freeze.txt');(d/'sources').mkdir(exist_ok=True)
for f in [n+'.png' for n in names]+['a15.img','a16.img','a18.img','key-frame-manifest.json','gif-frame-manifest.json']:shutil.copy2(s/f,d/'sources'/f)
for f in ['run_depth.py','run_batch.py','package_results.py']:shutil.copy2(p/f,d/f)
shutil.copy2(p.parent/'depth-observatory-20261104/fetch_model.py',d/'fetch_model.py');(d/'model').mkdir(exist_ok=True)
for f in ['config.json','preprocessor_config.json','README.md']:shutil.copy2(p/'model'/f,d/'model'/f)
(d/'analysis.zh.md').write_text('''# 红白扭方框厅GIF解码图相对深度：低清局部研究、未验收
来源腾讯游戏学堂2022-01-12采访https://www.gameres.com/892357.html。演出日期未知，原GIF a15/a16/a18及所用PNG原字节保留。分别a15第110帧8800ms、a16第27帧2160ms、a16第107帧8560ms、a18第0帧0ms，320×176。GIF累计时刻不是直播片内时间，非直播原生帧，未核登录最高画质。已逐张从原GIF重解码RGB像素比较PASS，并复核累计duration及时长；详见gif-decode-readback。
## 模型与分辨率
使用官方Depth Anything V2 Small HF固定revision5426e4f0f36572d16453bbda7a8389317b1bef99，CPU单线程float32，版本及所有参数/权重哈希在report和provenance。实际输入320×176被处理器上采样为518×280模型网格，输出raw也518×280。这不新增真实图像细节，不能声称高分辨率重建。raw float32 NPY和16bit灰图保留；名为resampled-screenshot-grid的320×176结果由bicubic回采样而来，截图在此泛指GIF来源图，不是直播截图。
大值/白一般较近，小值/黑一般较远，是相对逆深度类估计，不是普通亮度、不是真实距离。逐图minmax不可跨图当尺度比较；不能由灰度推出框厚、框间距、洞深或真实米制几何。
## 实看原图和输出：失败保留
A15斜广角：模型保留地面、墙和近角色的粗层次，但扭方框多层白边大多消失，黑洞变为平滑灰面。不能凭深度补画洞底墙或确证空洞深度。
A16第27帧冻结主态：近乎正面外壳和暗洞投影可见，但方框嵌套、细柱和顶环条带严重合并，远角色几乎融进背景。低清输入不足以恢复逐物体细部。
A16第107帧：模型突出前景人和右圆板，方框成为模糊多边形，洞内几何不可判。不得用人形或遮挡轮廓补建筑。
A18第0帧只作亮洞状态辅助，不能混入A16主态几何/灯光拟合。洞内原图变亮后模型输出也大改，不能解读为真实洞深变化；舞狮/角色动态遮挡不是实体墙。不能确认相同表演姿态或时空连续。
A05蓝紫状态未纳入本次推理或拟合。四图不能证明整厅隐藏结构、真实相机、米制尺度、同状态或不同日期复用；需更高质量原生多视图、逐物体核对和直接同机位叠图。
## 掩码
1人物/舞狮动态遮挡，2黑洞内部未知，3地板反射/彩光警戒，4亮洞状态变化。保守人工ROI不完整，0未标记不是有效。暗部原RGB各≤25仅低信号提示，不是深度方法。confidence-unknown全255表示没有校准置信度，非高可信；nonfinite=0只代表数值有限不代表几何正确。不可见表面不补成事实。
''')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps(files,indent=2))
for f in files:assert sha(d/f['path'])==f['sha256']
for n in names:assert sha(d/f'sources/{n}.png')==json.loads((d/n/'report.json').read_text())['source']['sha256']
print(d,len(files),sum(f['bytes'] for f in files),'hash readback PASS')
