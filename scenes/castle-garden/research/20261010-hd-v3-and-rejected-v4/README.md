# 城堡花园高清v3与否决v4：仅研究归档

## 状态与优先级

本目录保存真实存在的研究原文件及复现材料，不是当前成品发布。v3冻结模型仍未通过来源忠实度验收、未交付；原有四项Library仍为version 1。所有CURRENT指针保持原样。本目录不得被当作替换CURRENT的依据。

当前权威结论：**盆柱布局/机位不匹配尚未唯一归因**。不是“已证实盆柱偏外”。结论优先顺序为：本说明 → [v4否决结论与勘误](garden_v4_horizontal_trial_20261010/可辨识性与单参数试验结论.md) → [600秒保留源检查](garden_hd_holdout_600_20261010/新增600秒保留源检查.md) → 各阶段原始记录。旧记录保持原字节，其先前措辞不代表当前判断。

## 三个研究阶段

1. v3保守候选只保留有同立面比例支持的窗/门窄化（旧宽度0.67/0.80倍）、保守花拱形状近似；撤回花拱前移。有限结构检查不能代替来源高保真验收。冻结模型SHA256为 `b30c6591f4d8d80dc4628cf504ae418319daeb6e2bc8e0c359cce7957b4ef886`。
2. 新增600.385210秒来源截图前后paused=true、ready=4、时刻相同；原解码1920×1080，实际保留的是1180×664浏览器画芯，不能称为原生1080导帧。600只作一次固定HD1326姿态、窗中心等比相机诊断，未知原主点和真实机位；没有改模型几何/材质/灯光。
3. v4数值预检只动共享盆柱半间距，左右x=±a，锁定y=−1.475、帽顶z=1.73及全部已有相机。668/1326用于训练、600/1519完全保留。a=3.0299904852389883的保留横向RMS为67.1046/81.1820像素，失败并被否决。没有采用参数，没有v4模型，没有栏杆重建或全场v4渲染。

## 必须连同原记录阅读的勘误

600初期约163—181像素（概称160—180）的盆帽残差错误关联到最靠立面模型排y=−0.025。跨帧身份检查后，应以中排彩花盆柱作试验对象；旧残差作为“正确对象几何误差”的资格已撤回。`qa/600_initial_interpretation_SUPERSEDED.md`、`scripts/check_holdout.py`、`qa/holdout_fit.json`及相机sidecar中嵌入的旧盆柱行，只保留历史可追溯性。相机参数仍供复现已有600诊断；它们不能把旧盆柱残差重新变成有效指标。当前中排试验及失败残差以v4预检JSON为准。

668/1326是相关正轴构图族，不能称为独立双目；600可能存在纵向移动。源盆帽横向中心并非精确帽顶边，不据纵向残差修改高度。门槛踏步数、深度与高度仍未确定。相机、深度及同深度假设尚耦合，需要同状态连续前后与横移视差、同时保留同对盆柱及固定立面点的新来源。

## 收录范围

- v3冻结BLEND原文件、真实修订说明、拟合参数、有限技术QA、三张HD对照预览及相机sidecar。
- 600锁帧画芯与前后元数据、原诊断渲染、直接50%叠图、对照图、相机sidecar、参数、脚本、当前报告及明确标记的旧解释。
- v4单参数预检脚本、输入依赖JSON、结果JSON与否决结论。这里的“v4”只指受限试验阶段。
- 已经归档的三张HD原截图、帧元数据和基线BLEND只按同一SHA引用，不重复复制。

44,110,591字节的44MB汇总ZIP、全部其他ZIP、GLB/白模重复候选、发布helper、Library回执、下载URL、日志、内部工作记录均不纳入本阶段。为控制体积，三HD原渲染PNG及大叠图未重复加入；保留原对照预览和sidecar，完整渲染可从冻结模型生成。本目录不宣称已从零重跑全部早期拟合或全部结构审计。

## 复现边界

原脚本按原字节保存，包含当时的绝对工作目录；先将所列原目录名放在独立工作副本下，再仅在临时脚本副本中改根路径。不要改本归档原件、冻结模型或CURRENT。Python数值预检需要NumPy/SciPy；Blender渲染脚本需要相容Blender环境。版本未额外固定，本次归档准备没有执行这些脚本。

- v4最小数值依赖：`garden_v4_horizontal_trial_20261010/scripts/preflight_one_parameter.py`、`garden_hd_revision_20261010/qa/joint_candidate_v3_conservative.json`、`garden_hd_holdout_600_20261010/qa/holdout_fit.json`。运行会写结果，必须在临时副本中进行；输出与已存结果JSON比较，不能据低训练误差采用参数。
- 600图像复现：冻结v3模型、`holdout_fit.json`与`scripts/render_one.py`。sidecar保留输入/输出SHA。叠图为来源与模型的直接50%混合，没有局部扭曲；视觉差异和相机歧义均保留。
- v3冻结模型渲染：`scripts/render_frozen_v3_one.py`按sidecar标签选择相机。保存的`build_conservative_v3.py`会重建/写出模型，只允许在独立临时副本中使用，并先将下列已归档基线映射到脚本期望的相对位置；重建得到的新字节不替代原冻结BLEND。
- 三HD画芯可按`qa/source_evidence.json`的裁切矩形从下列已归档原截图提取；这些截图并非精确锁帧。

## 已有原文件的同SHA引用

以下文件已在前序花园原文件归档中，无需再次上传：

- [garden_668.249_1080decoded_viewport1180.jpg](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/garden_668.249_1080decoded_viewport1180.jpg)：SHA256 `a6dfd33ec87eed561423175be78d0f139747992f79975a869ebb0e86322419ba`。
- [garden_second_1080decoded_viewport1180.jpg](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/garden_second_1080decoded_viewport1180.jpg)：SHA256 `503c400ca7de3cdbc21983cb9041ef8508f4b134ef357e22f88815eaaea47414`。
- [garden_third_1080decoded_viewport1180.jpg](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/garden_third_1080decoded_viewport1180.jpg)：SHA256 `83302d76686f1b30e81494f6e601f0bab1c5a625bd2bb6c4bdb4e561a7ed4695`。
- [frame_668.249.json](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/frame_668.249.json)：SHA256 `99804d6a28e9017be9ec8a7869fd35894bb84f69ef1449b67c36914cb5ad6653`。
- [frame_second.json](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/frame_second.json)：SHA256 `c65096c44d012b8b2611084e201cfb24aa4d6e164924278d5d7fc4292d43d1ca`。
- [frame_third.json](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/frame_third.json)：SHA256 `6d7185217f2f11b352ace44f8043acf18bf2898988b8fdd3bc9ff37975ca5187`。
- [高清补帧说明.json](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/04_Garden_Views_and_QA--2a0143a2ee99/references/高清补帧说明.json)：SHA256 `471668dbde8c5e90fe276755498883bf973a007af216177bb61a27889a9812f7`。
- [Garden_Complete_Textured.blend](https://github.com/Shuang-su/metaxingtong/blob/0e877323ad83397db6d2e4d42d3f4654893c85f5/scenes/castle-garden/03-retain-complete-geometry/files/03_Garden_Textured_Blender_and_PBR--274507b59c20/models/Garden_Complete_Textured.blend)：SHA256 `34f42eb9e4c7a9d7387b5a49fa11d87a82fb3eb3eb036c274d0571c8f58a2357`。

新增原文件清单、文件大小、SHA256与Git blob SHA由本阶段归档清单提供。校验值用于身份与完整性核对，不代表模型验收通过。
