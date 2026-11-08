# R06 七张源的深度覆盖独立补充

**实际产物覆盖7/7来源帧，而不是“初一帧工具可用”泛称全源完成；7/7产物存在不等于7/7几何/来源验证通过。**

本审阅重新读取7个float32 NPY、解码输出、复算全部报告所列文件SHA/字节，独立从raw数组重建gray16和bicubic展示gray8；没有重跑网络模型。结果全部来源SHA正确、输出SHA/字节吻合、raw无非有限值、范围吻合、灰16与灰8派生逐像素0差异。7个source ID各有一组，不含重复计数。

## 准确覆盖表

所有推理原网格均 **924×518（数组H×W=518×924；输入tensor=1×3×518×924）**。源网格显示只是派生，不是1080P/4K独立深度预测。

|源绑定ID / 实际源时刻|实际原源/展示尺寸|深度产物目录|raw min / max|CPU线程 / 报告耗时|
|---|---|---|---|---|
|aug24-front / 1.093550|3840×2160|外部 `harbor-preliminary-analysis`|0 / 4.815495|4 / 2.164643s（推理及输出合计）|
|preview-front / 5.051975|1920×1080|本repo `depth/preview-front`|0 / 6.590440|1 / 3.777862s|
|preview-high / 10.106498|1920×1080|本repo **`depth/preview-oblique`**|0 / 3.958324|3 / 1.988671s|
|preview-wide / 13.767175|1920×1080|本repo `depth/preview-wide`|0 / 5.043179|3 / 1.750864s|
|preview-low / 16.085747|1920×1080|本repo `depth/preview-low`|0 / 3.502374|1 / 3.792496s|
|companion-120 / 120.140741|1920×1080|本repo `depth/companion-120`|0.339219 / 8.859534|1 / 3.753757s|
|companion-126 / 126.768777|3840×2160|本repo `depth/companion-126`|0.367402 / 10.386987|1 / 3.639896s|

耗时是原执行报告/日志字段，不是本审阅重新推理的测量。`preview-oblique`文件夹绑定10.106498，渲染中名为`preview-high`；不是额外第8帧，也不是错漏。初帧另外保留3840×2160重采样float32数组，33,177,728字节；本次也验证其与raw的bicubic结果完全相等。其余6帧没有宣称存有该大数组，保留的gray8展示已核派生正确。

## 方法、版本、权重与展示

- 模型：`depth-anything/Depth-Anything-V2-Small-hf`。
- 固定revision：`5426e4f0f36572d16453bbda7a8389317b1bef99`。
- safetensors SHA256：`3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70`。本审阅实际读取本地权重99,173,660字节计算，和7报告一致。权重是外部本地cache、不是海港交付必须自带/已提交的blob；复现应按固定revision重取并核SHA，不能靠未指明的“本机已有模型”。
- 全部报告与当前depth venv版本一致：torch `2.15.0+cpu`，transformers `5.22.1`，safetensors `0.8.0`，Pillow `13.0.0`，NumPy `2.5.4`。
- `float32`、CPU、`local_files_only=true`、`trust_remote_code=false`。DPTImageProcessor按短边518、keep_aspect_ratio、ensure_multiple_of=14处理源；不是把原源PNG篡改成924×518。
- raw语义为模型相对逆深度式值，一般大=近。每图自身min-max归一化，白=大；没有跨图绝对可比距离或米制尺度。
- gray16是原网格归一化量化；展示gray8是raw经torch bicubic、`align_corners=False`重采样到原源网格再归一化/clamp/量化。**7/7独立复算逐像素完全吻合**。不是原源普通亮度灰度。

## 掩码与“不通过”边界

实际读像素确认7张confidence图都只有255一个值；这里255代表**未知**，不是高置信或通过。

- 初aug24帧：手工人物矩形、节目图形矩形、中心天空近似多边形、下部反光台面/水域/混合区域。尚有4,424,076像素类0，但类0仅未标，不认证有效。
- preview-front/low：实际类1/2/3/4覆盖全幅；分别是节目图形、反光下部舞台、海水远景/树、强发光显示/结构混合区。
- preview-high：实际类1/2/3/4覆盖全幅；同样保守，不是实例级精确分割。
- preview-wide：类0尚有189,471像素；其余节目图形/镜面/水远景/发光混合区。类0不等于可信几何。
- companion120/126：实际类1至5覆盖全幅，额外类5是动态人物保守ROI；字幕、反射、远景、发光/结构混合仍被排除。

全幅被保守标注不意味着模型“没运行”，也不意味着有任何经验证有效的像素；不能拿未知置信图作自动拟合权重。完整像素计数和原mask说明见 `independent-depth-coverage.json`。

以下视觉失败摘自builder逐图`depth-review.md`及外部首帧报告（本次独立核其文件/数值，没有冒称重新目检7灰图）：初帧人物深度与地面脱节、节目logo被预测近物；front观众/字幕极近且箭框孔被压平；high镜台成为平滑坡；wide台盘/冠层压缩；low把碟底与曲带连为宽实心块；companion120曲带/箭框压暗且人物/地面不连续；126前灯极近、脚与镜面接触不连续。故不能用深图证明脚接触、下碟截面、孔穿通、隐藏第3/4腿或真实距离。

执行历史还保留：`evidence/source-bridge-and-limitations.md`记录首次宽景调用cwd错导致相对config找不到，改回项目后成功。该失败在现有文字记录中，不冒称本审阅取得原始失败终端完整日志。`additional-four-inference.log`真实保留后四帧加载权重/shape/range/时间及`use_fast`弃用警告；警告不是推理失败。每帧成功产物均已实际复算，不把已修复执行失败删成“始终一次成功”。

## 跨仓库首帧可取引用

本审阅实际核对外部本地 `depth-validation-20261102@f20277101571cb47fb770da039aba47f3b7a5c46`：初帧报告所列6个输出都与该commit实际Git blob SHA256相等；源SHA也等于R06 aug24-front原PNG。

父任务另提供已远端核验的可消费关联：**PR96、固定HEAD `3a92e456889f2931429897e37e5680dfc6802423`、路径 `docs/depth-analysis-20261102/files/harbor-preliminary-analysis`**，且对应原PNG已绑定。远端核验是父任务证据，非本子审阅独立网络访问。owner随后已在external-reference写入仓库 `Shuang-su/metaxingtong` 和固定可取地址 `https://github.com/Shuang-su/metaxingtong/tree/3a92e456889f2931429897e37e5680dfc6802423/docs/depth-analysis-20261102/files/harbor-preliminary-analysis`；不能只引用`../depth-validation-20261102`，也不能依赖已trash旧Space。该固定引用不意味着R06所有文件已经远端提交。
