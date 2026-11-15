# 03 动作连续性候选 v9

接续独立分支 `7f310b95f7848b7b5f45008752cb620f3958a129`。本轮只修订 03 F5–21 的领口，保留原件、v8 和各次试样；02 保持 v8。

**结果：修补新增的衣领跳变减轻，原图 F4→5 的低头和表情切换仍明显。完整动作仍是待观看验收的候选，不能写成已经消除跳变。**

## 方法和单帧门槛

v8 在 F4→5 从正常 F54 领口供体换到 F28。v9 对 F5–21 沿用 F54 的真实像素，用七个局部位置锚点做平滑空间配准，领结和袖口位置从同角色原帧匹配。没有加入帧、删帧、改速或时间插值，也没有改表情来掩盖跳变。

直接平移和三点配准造成肩部错位或下沿重线，已拒绝并保留。增加领结锚点后仍有供体白背景渗入外侧蓝色肩部，修订为保护该区域。随后检查发现原型涉及 15–22 个面部轮廓像素，再加入面部连通区域及 2 px 边界保护。r3 单帧边界与保护检查通过后，才扩展到 F5–21。

## 完整时间轴检查

- 54 帧、4650 ms，每帧时值与原 manifest 完全相同；改动 F5–21 共 1400 ms。
- 其余 37 个完整帧保持 v8 的解码 RGB，F27→28 和 F54→1 循环接合不变。
- 正确手部、面部轮廓、y<450 头部、奶绿绿色区域、y≥552 膝部及下半身均 0 像素变化；允许遮罩外 0 像素变化。
- 三个 GIF 均重新解码检查尺寸、帧数、逐帧时值和无限循环标记。已查看受影响原生裁剪、动作入口/出口及全部 54 个真实 112 px 解码帧。
- 36 个交接原文件大小和 SHA256 均未变化。原始 GIF SHA256 为 `04581604d66e45a04339a58c30eac0c190a6905d77b19e8b16b1f928f1b1fc6e`。

## 逐帧差值及限制

数值为固定 ROI 的 RGB 平均绝对差，范围 0–255；它描述像素变化，不代表实际播放或感知验收。

| 边界／区域 | v8 | v9 |
| --- | ---: | ---: |
| F4→5 领口 `[230,450,345,550]` | 80.07 | 67.41 |
| F4→5 下方衣领 `[230,490,315,540]` | 92.32 | 58.39 |
| F4→5 整帧 | 21.38 | 21.13 |
| F21→22 领口 | 67.74 | 62.88 |
| F27→28 领口 | 48.00 | 48.00 |
| F54→1 领口 | 34.69 | 34.69 |

原始 F4→5 的整帧差为 21.01，说明大部分跳变来自原姿势转换。下方衣领差降低约 36.8%，不能据此宣称整段动作已经顺滑。F5→6、F6→7、F12→13 领口差分别增加约 1.06、1.56、1.61，其余差值完整保存在 `final-v9-validation.json` 的全部 54 个相邻边界记录中。部分领口褶皱及蓝色肩边在 768 px 仍有局部风格差异。

此前浏览器预览被管理策略拒绝，本轮未重试或绕过；实际定时播放仍未验收。API 请求 0 次，本轮 API 费用 $0。未复制凭据、未创建 ZIP。

## 文件与复现

选用目录：`emotes/sunburst/agent-emotes/03-awake/versions/20261115-transition-v9/v9-shared-collar-r3/`。包含主 GIF、112 px GIF、v8/v9 动态对照、逐帧 PNG、允许遮罩、保护区、透明图层和 `construction.json`。

本目录保留 `prototype-r0` 至 `prototype-r3`。`try_shared_collar.py`、`fit_shared_collar.py`、`build_v9.py`、`audit_v9.py` 依赖仓库中已保留的 v8 本地工具和原件，应在本仓库运行。`build_v9.py --output 新目录名` 可复现而不覆盖既有候选；`audit_v9.py` 对实际成品解码独立核验。

## 成品 SHA256

- `emotes/sunburst/agent-emotes/03-awake/versions/20261115-transition-v9/v9-shared-collar-r3/03-v8-v9-comparison-320.gif`：`f039459541df63031d51ca1ff6929f4184c724679482ce7095276d2ba619bca8`，5758176 字节。
- `emotes/sunburst/agent-emotes/03-awake/versions/20261115-transition-v9/v9-shared-collar-r3/03-v9-CANDIDATE-master-768.gif`：`b811c5cde6708f62ad6ffda81e116429180ea734b73d7cdbd11863dd882223ca`，12362458 字节。
- `emotes/sunburst/agent-emotes/03-awake/versions/20261115-transition-v9/v9-shared-collar-r3/03-v9-CANDIDATE-preview-112.gif`：`2072a9ef05caeb4bbb334e60cea448316b2990b66fcdf15d46d2821b3f545829`，566346 字节。

Library 原文件身份保存在 `v9-library-delivery.json`；实际发布回执和远端字节核验保存在 `/workspace/emote-local-patch-review/v9-publication/`，以该处结果为准。
