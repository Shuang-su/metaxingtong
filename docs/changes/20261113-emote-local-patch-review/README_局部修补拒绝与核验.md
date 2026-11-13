# 02／03 局部修补候选与核验

**结论：没有通过验收的修复。所有新候选均拒绝，正式 master.gif、chat.gif 和源网格保持原样。**

本轮完成了素材接收校验、可逆局部候选、保护区域与时间轴检查、112 px 静态对照及预览 GIF。浏览器实际播放被环境策略阻止，未通过实播验收。预览文件名均有 `REJECTED`，不可当作修好版本发布。

## 来源与分支

- 分支：`codex/emote-local-patch-review`，环境仓库 `/workspace/metaxingtong`。
- 本地基线：`0ca7ae5be9892e9fc6656142682f7702cf244110`。本地快照导入提交：`dfffaa3`。
- 来料是发送方标注源提交 `76051cf96bffc57200f90a6e4d88ed1ae9812287` 的 36 文件快照，不是 Git bundle；未伪造该提交或 sunburst 分支历史。
- 传输包为 51,421,199 字节，SHA-256 为 `42759187e540b81fb3868de5252e9b46da38101c7c37c1818042c34e8cee7e41`。安全解包前核对整包，解包后逐个核对 36 文件，全部一致；处理结束后再次核对 36 原件仍全部一致。
- 文件原件哈希完整记录于根目录 `handoff-manifest.json` 和本目录 `intake-verification.json`。
- 02 master：`d2b8bb05001dca2b74c2b7535fc8ec96ea8796eb0d0be0af174f9bba98569ba2`。
- 03 master：`04581604d66e45a04339a58c30eac0c190a6905d77b19e8b16b1f928f1b1fc6e`。

此前两个整网格 API 失败结果不在本次最小快照中，未重建也未作为通过结果。本包的 masked-repair 请求与网络失败记录完整保留，未执行其中任何 API 请求。

## 原片与缺陷范围

帧号从 1 开始；以下时值直接由原 GIF 解码并与 manifest 的逐帧数组逐项比较。

| 项目 | 原片 | 本轮复核 |
|---|---|---|
| 02-butterfly | 58 帧，768×768，4860 ms，循环 0 | 24–28 帧共 580 ms：第三只手连着多余袖口；23、29 为正常边界参照 |
| 03-awake | 54 帧，768×768，4650 ms，循环 0 | 10–33 帧伸手期间仍有双膝两只手，共 2120 ms；1–27 帧肩上可见额外指状形，共 2420 ms |

02 对应源格为 strip-1 的 10/11/12、keys 的 key5、strip-2 的 1，与 manifest 一致。02 已有 key5 草稿只圈住手掌，没有解决相连袖口；不能直接当作可用遮罩。03 已有第 17 帧遮罩也没有被默认验收，本轮另存具体多边形和保护区域。

03 的分镜要求伸手触碰并保留另一只膝部手。新候选没有删除伸手来伪装两只手。03 仅在第 17 帧试验，失败后没有把同样的坏补丁传播到其余 23 个伸手帧。

## 尝试与拒绝原因

全部采用本地 Pillow／NumPy／SciPy，供体取自已有原帧像素；未调用生成模型，没有整帧重绘。每一轮均保留原件、候选、遮罩、参数和对照。

| 试验 | 影响范围 | 决定与原因 |
|---|---|---|
| v1-clone-offset | 02 第 27 帧；03 第 17 帧 | 拒绝。02 供体带入别处的手掌残片；03 带入头发与袖口残片，接缝明显 |
| v2-cloth-mapping | 02 第 24–28 帧；03 第 17 帧膝部 | 拒绝。02 衣料拉伸、裙边白线断裂；03 是明显覆盖块，缺少合理衣摆边缘，肩部缺陷仍在 |
| v3-seam-matching | 02 第 24–28 帧 | 拒绝。局部 Poisson 边界融合产生模糊与肤色污染、白线变形 |
| v4-neighbor-donor-23/29 | 02 第 27 帧 | 拒绝。正常邻帧的上衣与裙摆姿态不吻合，出现折线接缝、残片或显眼白色补丁 |
| rejected-review | 02 第 24–28 帧；03 第 17 帧 | 在 v2 上再恢复保守手部保护框，编码成完整审阅循环；仍有衣料接缝／残留，明确拒绝 |

每个变体的 `candidate.json` 已写为 `rejected_not_for_production`。修补前后的局部对照包含放大图，不能用缩小后不明显作为通过依据。

## 像素与 GIF 检查

审阅成片目录为各表情的 `versions/20261113-local-patch-review/rejected-review/`：

- `REJECTED-candidate-full-loop.gif`：768 px 完整循环，02 保持 58 帧／4860 ms，03 保持 54 帧／4650 ms。每帧时值完全一致，未跳过或冻结动作。
- `candidate-NN.png`、`allowed-mask-NN.png`、`comparison-NN.png`：可逆修补、允许变化区域、原图／候选／遮罩对照。`gif-decoded-NN.png` 是实际重新解码后的 GIF 帧。
- `validation.json`：每一帧的原件 RGB 哈希、变化像素数、允许区、保护像素数及 GIF 重解码结果。遮罩外变化数均为 **0**，未修改帧在 768 px 重解码后也逐像素相同。
- 编码使用每帧原有颜色板，仅把允许区写入；不把全局重调色导致的变化混同为局部修补。
- 02 另外固定两个保守手部框 `[634,478,722,538)`、`[460,473,528,540)`；03 固定真实伸手框 `[285,425,508,545)`。坐标为 768 px 的左上原点，右、下界不包含。框内原像素全部恢复并验证相同。这些框不代表精确人体分割；遮罩外全部像素同时受保护。
- 112 px 是缩放和再次编码的审阅副本，不能把 768 px 的逐像素不变声明套用到缩放副本。

`original-decoded/` 保留每帧 GIF 解码 PNG；它们的 RGB 哈希与 manifest 中原始编码前 PNG 哈希属于不同数据阶段，不强行宣称相同。

## 112 px 审阅与实际阻塞

已生成并检查 `comparison-native-112.png`，以原生 112×112 尺寸显示原图与被拒候选；也生成 `REJECTED-preview-112.gif`。02 仍有衣摆残留和线条变化；03 第 17 帧的覆盖块及未修肩部使整片不能验收。

Chromium 实播脚本已实际运行，但在打开本地预览页时立即失败：

- 操作：`page.goto`。
- 目标：`file:///workspace/emote-local-patch-review/browser-evidence/playback.html`。
- 原因：`net::ERR_BLOCKED_BY_ADMINISTRATOR`，来自 Chromium 管理策略。
- 状态：被拒；没有完成任何 GIF 实播截图采样，不存在已验证循环次数。
- 后续：查阅可见用户历史后没有发现允许改变此限制的新证据，未重试、未改浏览器或网络策略、未改走其他访问路径；本轮自启的浏览器进程已关闭。

这是浏览器策略拒绝，不是自动审批工具的拒绝。详见 `browser-playback-blocker.json`。浏览器原速播放连续性仍是未验收项；文件级时间轴与 112 px 静态接触表已完成。

## 文件和复现

- 报告与脚本：`docs/changes/20261113-emote-local-patch-review/`。
- 02 全部候选：`emotes/sunburst/agent-emotes/02-butterfly/versions/20261113-local-patch-review/`。
- 03 全部候选：`emotes/sunburst/agent-emotes/03-awake/versions/20261113-local-patch-review/`。
- 精确帧清单：`frame-review.csv`；合并技术检查摘要：`loop-verification-summary.json`。
- 脚本顺序：`inspect_originals.py`、`try_local_candidates.py`、`try_cloth_mapping.py`、`try_seam_matching.py`、`try_neighbor_donors.py`、`build_review_artifacts.py`。后五个脚本在已有输出目录时拒绝覆盖；复现应使用保留原始素材的新工作副本。
- `verify_playback_112.cjs` 保留失败的实际播放检查方法。不得在本环境重复被拒的导航或为运行它而改变策略。

本轮未改第 15 条、pout-neck-follow、09 呆毛或 01 蓝灰服饰，未运行 3D、付费 API 或外部依赖安装，未复制凭据、访问此前被拒的服务或 push。未创建新 ZIP；交接为 GIF、PNG、脚本及报告原文件，内部输入 tar.gz 不作为成果包。

剩余工作是制作能与原图线条和衣摆形状匹配的局部清洁衣料／肩领图层，再重新逐帧验收；当前像素拼补实验不支持声称修复成功。
