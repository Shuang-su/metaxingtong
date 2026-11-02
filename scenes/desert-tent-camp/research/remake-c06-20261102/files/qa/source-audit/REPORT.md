# 2026-11-02 沙漠旧候选重制：只读来源 / 深度 / 相机脚本审计

## 结论
1. 三张旧来源 PNG 的实际字节 SHA、大小、PNG IHDR 与 PIL 完整解码尺寸全部匹配 recovery_manifest。它们是旧来源精确字节恢复，**不是新采集或11月2日新场景**。
2. 已有1566.095177深度结果可以按源 SHA **精确绑定同一PNG**；当前来源文件路径与报告旧路径不同，但字节身份相同。6个深度/掩码文件实际SHA、大小均匹配已有report。它们是单图相对逆深度类预测，不是米制、完整几何或相机校准证据。
3. 恢复的 audit.py 等4个脚本文本均匹配恢复候选manifest当前SHA且语法解析通过，**原始历史脚本SHA仍未回读证明**。audit.py依赖3个现已缺失的旧anchors/camera JSON；脚本本身不含完整旧硬箱3D坐标或旧相机seed。不能直接运行并冒称旧模型/旧FAIL原字节已恢复。
4. 未运行任何新模型推理、相机优化、Blender、渲染或云端Codex；未修改生产分支。只在本审计目录写入报告/核对结果。

## 1. 三个来源原件
均为BV169Y96rEo1 P1，实际尺寸1920×1080；时间数值按历史播放器记录，不冒称容器PTS。

|当前文件（recovered-source-candidates/camp/）|字节|实际SHA256|
|---|---:|---|
|BV169Y96rEo1_P1_1541.38851.png|2916703|a6ade8c81a8bfdb6b0d26e5b8e3ec44496c5e9f95ceb8e16a56c7fe170080b24|
|BV169Y96rEo1_P1_1570.44087.png|3151148|9c9715e240152f88b254353f63918da47104014668667e749a9b1db486d93b02|
|BV169Y96rEo1_P1_1566.095177.png|3202090|947229e1fc963f73b47468f371083fe876f0dcf6458b43f0623fbb7b59c2fc7b|

上述每项均与recovery_manifest的original_sha256、recovered_sha256、bytes、dimensions一致。登录、最高画质与实际解码证据仍来自历史记录；本次未重复登录/导帧。来源同一回放，不能替代后续独立回放同场验证。

## 2. 现有1566深度文件：身份、方法与原grid
目录：`depth-validation-20261102/camp-tool-validation/`。

已有report.source的SHA与当前1566 PNG完全相同，crop为[0,0,1920,1080]。读过完整 `run_depth.py`，没有执行它。

已记录模型：`depth-anything/Depth-Anything-V2-Small-hf`，revision `5426e4f0f36572d16453bbda7a8389317b1bef99`；本地`safetensors`权重实际重算SHA `3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70` 与报告一致。原执行CPU/float32/4线程，trust_remote_code=False、local_files_only=True。上述为已有模型与执行记录，不是本次新推理。

输入tensor记录[1,3,518,924]，实际原输出NPY shape **[518,924]** float32（图像宽924、高518），finite全部有效数值，范围0…8.15842056。报告的1920×1080版本是 `bicubic, align_corners=False` 源网格重采样，**不能称独立原生1920深度预测**。本次没有重执行插值，只核报告/脚本与实际输出字节。

|文件|实际大小/shape|SHA256（均与report一致）|
|---|---|---|
|relative-inverse-depth-model-grid.npy|1914656 bytes；518×924 float32|e345edb39ff2740317c144e52695d5c147774705d99c4fc2dbf92d3daf57d416|
|relative-inverse-depth-gray16-model-grid.png|924×518，uint16|ceca4ee1d4d77c6a9cf8088dbfd8e1d39b9b9bcfe95b604b8920ec07e27f7f0e|
|relative-inverse-depth-resampled-source-grid.npy|8294528 bytes；1080×1920 float32|41ab8645d8398561ce463296d63f2e7beaaf049ea65260d0b54bd00e1e08a065|
|relative-inverse-depth-gray8-resampled-source-grid.png|1920×1080，uint8|92795c41690cc6e5da4d48448b19b27f683cfcd628ade44f23cbf25b27fc6aae|
|manual-exclusion-classes-source-grid.png|1920×1080，uint8|5e3ae393692ed65983f004fd02e49e9425fea52be6275d2f4610285277673d0a|
|confidence-unknown-source-grid.png|1920×1080，uint8|6ae2cfa8276a1bd642b45a5401579b8a93bc9506299ae41171573adff763f9f6|

原16位灰度=`round(clamp((raw-min)/(max-min))*65535)`；派生8位灰度使用相同原min/max并clip。独立编码检查两PNG与各自NPY推导值均**0像素差**。派生float32网格范围−0.2319463…8.1612234，5394值低于原min、8值高于原max，符合bicubic过冲风险；不能把这些数值当负物理距离。显示灰度已经clip。

### 掩码具体含义
- 类0：1769544像素，未标注，**不是已验证可用像素**。
- 类1：98115像素，人工保守人物矩形[845,411,1055,875]（含旁边背景）。
- 类2：45600像素，字幕矩形[706,887,1180,982]。
- 类3：160341像素，近似天空多边形，顶点见run_depth.py；边界不精确。
- confidence图所有2073600像素都为255，含义是**全部未知置信度**，绝非高置信度。

本人实际看过1566来源和派生灰度：主体、帐篷与近物的大轮廓能够对应，但字幕被错误预测为近物，远峡谷深度压缩，人物不属于静态场景；布面光影、植被边界和雾/背景均不宜作为精确深度。掩码不完整，未见区域不能补成已知。

若重制使用：仅可作明确降权的相对遮挡/深度辅助或问题定位，不可由其恢复绝对米数、人物身高标尺、硬箱精确支撑、隐藏背面或唯一相机；更不能用模型输出去替代独立第三帧FAIL检验。

## 3. 恢复audit脚本可用与不可用参数
当前 `reconstruction-recovery/camp/code-candidates/roll/audit.py` SHA为`02144b67b709d62513e2cce486623f4fbd6d80859469ec0c5129fdca4cbbb91b`，与RECOVERY_MANIFEST一致；这只证明恢复候选自洽，不证明旧原脚本字节已恢复。

脚本自身明确保留：
- 固定主点(960,540)，f=1800/2500/3200三个事前profile。
- 完整6DoF姿态xyz+yaw/pitch/roll；roll±5°诊断界，非实测。
- 训练像素：F1[186,700]、F2[283,697]、软apex[143,193]；权重6/6/8px。
- 后箱保留像素：B1[85,551]、B2[140,549]；不用于选择分支/焦距。
- 每f56起点，按pose聚类，保留全部运行、正深度、可见面、rank/边界；六标量三点恰定不能用零拟合误差宣布标定成功。
- 原可见生成器另保留前箱中段样本[185,707]、[185,731]，模型名义边[-.45,0,0]→[-.45,0,.456]、4px权重。此边和箱体正交/水平是工作假设；它不是测量尺寸，也不能把样本端点当箱顶/箱底。

脚本**缺少且当前路径不存在**：
1. `/workspace/shared/desert-camp-build-20261031/scenes/desert-tent-camp/qa/heldout_r03/frozen_geometry_anchors.json`（F1/F2/apex真实旧工作3D点）；
2. 同根 `qa/R07_actual_model_anchor_check.json`（旧R07实际箱点）；
3. 同根 `qa/heldout_r03/fixed_model_camera_cases.json`（旧固定f相机seed及协议结果）。

因此不能只拿恢复audit.py再跑，必须先为**新重制版本**建立可读、显式的几何/相机输入与阶段身份；不得伪装为旧R07原件恢复。本次没有填补这3个缺失JSON，没有重优化。

### 第三帧历史FAIL仍保留
可见历史工具记录曾报告：R03固定几何zero-roll第三检验后箱20–29px；R07仅修原两源箱中心构造后复用第三相机仍13.36/13.41px；6DoF复查f2500三点方案9.53/9.78px、再加前箱竖边7.80/8.97px，仍超过±6px。此段是**历史可见结果文字**，非本次重跑、非当前旧结果JSON字节复验。

1566已经在失败后多次被检查。重制若用它拟合/选镜头，必须标已进入训练，不得称新盲验；仍要完整保留另一个未拟合物件/有限段作验证，且来源三图不替代后续其他回放。

## 本次文件
- `audit.json`：实际全部SHA、尺寸、NPY范围/finite、掩码计数、脚本候选SHA与缺失依赖。
- `encoding_check.json`：灰度编码0像素差及重采样过冲计数。
- `check_inputs.py`：只读字节/尺寸/AST检查代码（已运行；不导入任何深度模型）。
- 本报告：只为旧候选11月2日重制提供来源审计，不把旧候选算新scene。
