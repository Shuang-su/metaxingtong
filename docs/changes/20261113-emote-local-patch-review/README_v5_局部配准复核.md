# 02／03 新一轮局部配准复核

**本轮新增了真实像素供体配准试验，但五个新变体仍未通过静态验收。没有替换原 GIF，没有将坏补丁扩展到其他帧。** 官方 Library 直接保存入口已实际成功，已保存的每个文件 ID 与 SHA-256 单独记录；先前失败的 helper 认证路径没有重试。

## 本轮与旧试验的区别

从本地 `codex/emote-local-patch-review` 的 `913ac96bbddfeb9fefdf48382dd4e8d884e2ad7f` 接续。上一轮 v4 是正常帧 23／29 的同坐标贴图，没有配准。

新 v5 对 02 第 27 帧（key5）使用正常第 23 帧衣料，通过 20 个上衣下摆、裙摆白线及裙边对应点做分片仿射反向映射。只重采样局部衣料，保护两只正确的手。被冗余手遮住的目标衣摆点需要在可见两端之间推定，参数中明确标为推定，没有称为可观测原图真值。

第 29 帧供体的对应裙面含显著亮色块，直接使用的造型不匹配已由 v4 验证。本轮没有重复同坐标贴图，也没有再次把这一块冒充可用底图。

03 逐格检查了已交接的 keys 9 格、strip-1 12 格、strip-2 12 格，共 33 格。目标膝部都保留了手或袖口，未发现同区域无手的完整衣摆。strip-2 第 3 格仍有肩上指状形；第 4 格（原片第 28 帧）有干净肩领，因此新增了向第 17 帧配准肩领的试验。膝部问题保留为未解决。

## 新候选结果

| 表情／变体 | 实际变更像素 | 检查结果 |
|---|---:|---|
| 02 trial-23 | 3561 | 第三只手主体消除；裙摆白线左侧接缝及右侧碎段不合格 |
| 02 trial-23-refit | 3561 | 校正左侧白线后改善；手下右侧白线仍断成碎段，不验收 |
| 02 trial-23-right-band | 4064 | 单独配准右侧白线后，末端出现不合理亮色尖角和衣褶变形，拒绝 |
| 03 shoulder-trial | 1379 | 肩领覆盖部分指状形；袖肩轮廓不衔接，正确伸手旁仍有残片，拒绝 |
| 03 shoulder-trial-refit | 1745 | 调整边界后仍有残片和折角；膝部冗余手未解决，拒绝 |

每个候选都有单独 PNG、允许区遮罩、手部保护遮罩、配准参数及原图对照，原件与失败样本没有覆盖。所有候选的遮罩外变化数均为 **0**；各脚本设置的正确手部／伸手保护区变化数也为 **0**。保护区的像素校验不等于自动解剖验收，手数、袖口、衣摆和边界仍通过原生图及放大对照人工审阅。

02 的第三只手主体能被局部消除，但新衣料边缘未达到门槛；没有因手数减少而判定成功。03 没有删除正确伸手来减少手数，也没有把肩部局部试验冒充整帧修复。

## 连续性与原件保护

02 对照原第 26、27、28 帧；03 对照原第 16、17、18 帧，分别制作原生 112 px 静态相邻帧表。只在中间格展示被拒候选，两侧仍是原帧，明确标注未验收。这些对照显示单帧替入不能作为完整修复循环，未宣称整段连续性通过。

由于单帧静态门槛未通过，本轮没有扩展 02 的其余 24–28 帧，也没有扩展 03 的其他受影响帧，没有生成新的候选 GIF。原 02 仍是 58 帧／4860 ms；原 03 仍是 54 帧／4650 ms；两份 master、chat GIF 都未改。

36 个输入文件全部再次通过原 SHA-256 校验。第 15 条、已完成 pout-neck-follow、09 呆毛、01 蓝灰部件均未动。没有 API、收费调用、凭据复制、网络策略改动、3D 工作、Git push 或新 ZIP。

Chromium 本地导航的管理限制继续保留。本轮没有再次尝试被拒路径，没有运行浏览器实播，也没有声称 112 px 原速播放通过。

## 精确本地路径与复现

- 仓库：`/workspace/metaxingtong`。
- 02：`emotes/sunburst/agent-emotes/02-butterfly/versions/20261113-local-patch-review/v5-registered-donor/`，三个子目录分别是 `trial-23`、`trial-23-refit`、`trial-23-right-band`；每个候选名为 `candidate-frame27.png`。
- 03：`emotes/sunburst/agent-emotes/03-awake/versions/20261113-local-patch-review/v5-donor-assessment/`；`shoulder-trial` 和 `shoulder-trial-refit` 中的候选名为 `candidate-frame17.png`。33 格供体接触表为 `all-source-knee-donors-native.png`。
- 结构化判断：本报告同目录的 `v5-review.json`。
- 脚本：`registered_donor_trial.py`、`registered_shoulder_trial.py`，依赖同目录已有 `try_local_candidates.py` 的根路径、遮罩和对照辅助函数。
- 02 脚本无参数、`--refit-stripe`、`--refit-right-band` 分别复现三个变体；03 无参数、`--refit-boundary` 分别复现两个变体。输出目录已存在时拒绝覆盖。应在保留源素材的新工作副本中复现。
- Library 交接副本：`/workspace/emote-local-patch-review/deliverables-v5/`。图像文件名中的 `REJECTED` 必须保留。

## 交接与尚缺条件

本报告保存前，官方直接保存已确认 10 个原文件成功：7 张 PNG（含源格检查图）和 3 个 Python 文件。它与先前返回 HTTP 401 的 hosted-app helper 是不同的受支持工具入口；本轮未重试该失败认证路径。每个成功文件的本地 Library 元数据均已写回。没有重复上传已取得文件 ID 的项目。

当前未解决的是可验收的局部衣摆轮廓、右裙边形状，以及正确伸手与肩领残片的准确边界。邻帧供体的衣褶和透视并不一致；本轮配准不能自动补出被遮挡的真实结构。后续仍需先得到通过静态审阅的局部清洁图层，再扩展各受影响帧，最后完成当前被阻止的实际播放检查。

以下记录均为已成功保存的真实文件，链接直接指向 Library 原文件；不代表修复验收通过。


- [03-source-grid-donor-review.png](https://chatgpt.com/api/library/files/libfile_fde3_f-981c28993dd08191854913092dc7238d_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-981c28993dd08191854913092dc7238d_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_00000000f5308209b105e997b93bdfa0`
  - SHA-256: `5356d29dfa304666c99dea99e719843932459d736a250c2acb32b315f40e85e6`

- [02-butterfly-v5-REJECTED-frame27.png](https://chatgpt.com/api/library/files/libfile_fde3_f-b354112490648191a173c6720ef15256_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-b354112490648191a173c6720ef15256_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_00000000fd3c8209934fc306dc299ff5`
  - SHA-256: `ecfe58432f3d3ea23c50255c186c2a6fc7b888552873a404b63beb522742e8dc`

- [02-butterfly-v5-REJECTED-comparison-3x.png](https://chatgpt.com/api/library/files/libfile_fde3_f-b59294ead19081918ce3b388c57f0f7a_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-b59294ead19081918ce3b388c57f0f7a_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_00000000cd708209a45f48ada3642126`
  - SHA-256: `1673a293553e2d1fec2c73e88798b66255b476752ce2947fde43ba13aa4b6d26`

- [02-butterfly-v5-REJECTED-temporal-112.png](https://chatgpt.com/api/library/files/libfile_fde3_f-452f7368f9ac8191bd55171c2418d872_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-452f7368f9ac8191bd55171c2418d872_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_0000000033348209bf7e297f79241031`
  - SHA-256: `73d4ff7a2be8c6ba3346c1b40c804c3dee0bb9ae3a7e3987f361e30912177bb2`

- [03-awake-v5-REJECTED-frame17.png](https://chatgpt.com/api/library/files/libfile_fde3_f-5f5f564dfcb88191b6f1d69a0f572f82_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-5f5f564dfcb88191b6f1d69a0f572f82_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_00000000df5c81f8aacbcef19d134426`
  - SHA-256: `53bb84ea7e2d4168d0c0fad168817712c05fc5df1db9ac3cc5cc6a421ece180a`

- [03-awake-v5-REJECTED-comparison-3x.png](https://chatgpt.com/api/library/files/libfile_fde3_f-14721b6978e08191a0afeac588a07a57_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-14721b6978e08191a0afeac588a07a57_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_00000000975481f89d30d74d2c9e8378`
  - SHA-256: `7e5f8300c1411ee354fbced99f4e57b8f44891be31277e2e2053bb13ecee3e13`

- [03-awake-v5-REJECTED-temporal-112.png](https://chatgpt.com/api/library/files/libfile_fde3_f-18c9cb7cb1548191be341d9814420662_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-18c9cb7cb1548191be341d9814420662_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_000000009b188209b4c65e4657baacc6`
  - SHA-256: `82975082cbf8844ea1950aef046ff40eb931b838fcdb7232f55a6520a7f40674`

- [registered_donor_trial.py](https://chatgpt.com/api/library/files/libfile_fde3_f-ab45eaee8a008191b77c533ed893d12e_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-ab45eaee8a008191b77c533ed893d12e_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_000000001b4482099383a6c8d968c807`
  - SHA-256: `4cb67ea465e0ffed02d9477fde2573bf990b8ff36acefb414a2dae1aabadf7f3`

- [registered_shoulder_trial.py](https://chatgpt.com/api/library/files/libfile_fde3_f-930e1f0afcfc8191b5ea99f78c7051ef_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-930e1f0afcfc8191b5ea99f78c7051ef_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_00000000857081f8b8ebb24898978522`
  - SHA-256: `4ae03f43f02afcbca9ab4883c9bcf31aff2bbe991be61051bd0e9e592588f1db`

- [try_local_candidates.py](https://chatgpt.com/api/library/files/libfile_fde3_f-3b5c785725448191aa0cf6288c35b394_b076fe8bc0d88191acf5572965aa3669/download)
  - Library ID: `libfile_fde3_f-3b5c785725448191aa0cf6288c35b394_b076fe8bc0d88191acf5572965aa3669`
  - File ID: `file_000000006ef482098347d22b2eb411ad`
  - SHA-256: `1ebbae1179284a295b5c9ab1d959076eeaa82e3a08415aac461c9c521547fcee`
