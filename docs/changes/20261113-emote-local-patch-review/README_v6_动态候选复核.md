# 02 / 03 局部修补动态候选 v6

已基于用户对上一轮局部对照“大体上还能接受”的反馈，完成可观看的完整动态候选。保留原件、前几轮未通过尝试和第一版动态候选。本轮状态是**可供观看复核的候选**，尚未获得用户对完整动态版本的验收，也没有把浏览器未能实播写成通过。

| 内容 | 02-butterfly | 03-awake |
| --- | --- | --- |
| 选用目录 | `v6-contour-and-motion/dynamic-candidate` | `v6-contour-and-motion/dynamic-candidate-r1` |
| 完整时间轴 | 58 帧，4860 ms | 54 帧，4650 ms |
| 改动帧 | 24–28，共 580 ms | 1–33，共 2900 ms |
| 具体区域 | 多余手所在裙边 | 肩部 1–27，共 2420 ms；膝部 10–33，共 2120 ms |
| 保持原样的完整帧 | 53 帧 | 21 帧 |
| 主候选遮罩外 / 保护区变化 | 0 / 0 像素 | 0 / 0 像素 |

各目录的完整前缀为 `emotes/sunburst/agent-emotes/<名称>/versions/20261113-local-patch-review/`。每组都有 `CANDIDATE-master-768.gif`、`CANDIDATE-preview-112.gif` 和 `comparison-motion-320.gif`。并排动态对照左侧为原件，右侧为候选；112 px GIF 保持实际像素尺寸。六个 GIF 都回读验证了帧数、每帧时值、无限循环标记和画布尺寸。

## 本轮具体修补

02 沿用局部配准后较可接受的 F23 真实衣料供体方案，将裙边和白线两组位置锚点分别匹配到 F24–F28。正确的前方手掌及另一只手保护区域保持原像素。第三只手的主要形状被衣料替换，没有删帧、变速或隐藏正确动作。F23 与 F29 是未改的边界参照。

03 肩部沿用正常 F28 衣领供体。自动匹配曾在睁眼后的若干帧落到脸部，已弃用那些匹配，并逐帧按肩部位置调整；原始错误匹配记录仍保留。第一版动态候选在 F1–F4 领口下方残留肤色尖片，`dynamic-candidate-r1` 用同一正常供体的小范围遮罩扩展清理了它。修订前后可见 `early-shoulder-prototype/comparison-3x.png`。03 第一版完整动态候选作为被修订的版本保留，不作为本轮选用文件。

03 膝部没有可用的干净同位置衣料原帧，因此使用可逆的**新绘局部裙摆图层**：奶油色布料、小灰色褶皱与弧形衣摆线，衣摆以下借用同帧裤袜像素。它是局部重建假设，不是找回的历史原画。只在 F10–F33 多余膝上手区域合成；真实伸出的手、袖口以及另一只膝上手列入保护区。没有删除伸手动作或整帧重绘。

## 逐帧复核与尚存缺陷

- 02 F23–F29 的局部细节及实际 112 px 解码结果已逐帧查看。F24–F28 不再呈现独立第三只手；正确手掌保留。白色裙边线在掌下右侧仍有小段断续，F23→24 与 F28→29 的裙褶变化可见，原动作关键姿势跳变也保留。
- 03 F1–F33 的肩部、袖口与膝部在原生像素裁剪中逐帧查看；F1–F34 的实际 112 px GIF 解码图也已查看。F1–F4 下沿肤色残片已清理；F10–F33 仍保留伸出的手和另一只膝上手。
- 03 衣领接合处有角度偏硬和轻微色点，F4→5、F27→28 以及循环 F54→1 的领口形状变化仍可见；不能声称每个微小原画残片都消失。
- 03 新衣料比原画平，768 px 下可见浅色块与局部轮廓风格差异。F9→10 开始伸手、F33→34 收手仍是原时间轴中的明显姿势切换，没有人为补间。F10–12 与 F28–33 的袖子邻接区域通过保护遮罩保留，代价是边缘略不均匀。
- 上述问题按最新反馈作为明确保留的候选缺陷记录，没有再因微小衣料差异推翻整个候选。完整动态节奏仍需在可播放的客户端观看后验收。

## 验证范围与原件

`audit_motion_candidates.py` 从实际 GIF 文件独立解码，逐帧比较原件、允许遮罩和保护区。112 px 及对照 GIF 是重采样显示文件，**逐像素不变保证仅针对 768 px 主候选**，不适用于这些缩放派生文件。`comparison-decoded-112.png` 的候选图块来自已编码 112 px GIF 的真实解码结果，每块正好 112×112。

`v6-validation.json` 记录六个 GIF 的 SHA256、大小和时值；`v6-frame-audit.csv` 记录全部 112 帧的原件/候选 RGB 哈希、变化像素数、遮罩像素数和保护区结果。各候选目录还保存逐帧 `allowed-mask-*.png`、`protected-*.png`、透明 `local-layer-*.png`、候选 PNG 和完整构造参数。

36 个快照输入的大小和 SHA256 再次全部核对一致，未改动原素材。此前交接 tar.gz 的整体 SHA256 为 `42759187e540b81fb3868de5252e9b46da38101c7c37c1818042c34e8cee7e41`，其核验记录保留在 intake 文件中。原始 GIF 哈希：

```text
02 d2b8bb05001dca2b74c2b7535fc8ec96ea8796eb0d0be0af174f9bba98569ba2
03 04581604d66e45a04339a58c30eac0c190a6905d77b19e8b16b1f928f1b1fc6e
```

本地来源是用户交接、标注来源提交 `76051cf96bffc57200f90a6e4d88ed1ae9812287` 的必要文件快照，未伪造原分支 Git 历史。在独立 `codex/emote-local-patch-review` 分支、前序本地提交 `a74a1ff95056fcfbfff55dd36c4d79df6e099418` 上继续。未写入源分支、未推送远端。

## 可观看交付

通过用户已授权的官方 Library 直接保存入口，以下六个原文件已成功保存。没有重新触发此前 401 的 helper 认证路径，也没有建立 ZIP。其余 PNG、脚本、报告的实际保存身份记录在 `v6-library-delivery.json`。

| 文件 | 02 | 03 |
| --- | --- | --- |
| 768 px 完整候选 | [02 GIF](https://chatgpt.com/api/library/files/libfile_fde3_f-4d50e35f73108191b0cb078aa64aa656_b076fe8bc0d88191acf5572965aa3669/download) | [03 GIF](https://chatgpt.com/api/library/files/libfile_fde3_f-5c811d07b20481919637ceae84e9dbb0_b076fe8bc0d88191acf5572965aa3669/download) |
| 112 px 预览 | [02 预览](https://chatgpt.com/api/library/files/libfile_fde3_f-6d7ddb4363dc819199163f1efa021aed_b076fe8bc0d88191acf5572965aa3669/download) | [03 预览](https://chatgpt.com/api/library/files/libfile_fde3_f-b739b851613c8191aaf33adc512e67f3_b076fe8bc0d88191acf5572965aa3669/download) |
| 原件/候选动态对照 | [02 对照](https://chatgpt.com/api/library/files/libfile_fde3_f-79851fb4755881918be8fec40148f4e7_b076fe8bc0d88191acf5572965aa3669/download) | [03 对照](https://chatgpt.com/api/library/files/libfile_fde3_f-62886f389fc08191b0a19c4fac4d1e09_b076fe8bc0d88191acf5572965aa3669/download) |

此前浏览器访问本地预览页被管理策略以 `net::ERR_BLOCKED_BY_ADMINISTRATOR` 拒绝；未重试该路径、改网络或浏览器策略，也未绕道本地服务。已完成 GIF 编码、逐帧解码、原生像素与 112 px 静态审阅，**没有浏览器实际播放验证结果**。未调用收费 API、读取密钥、复制凭据或创建新的 ZIP。

## 本地脚本

新增 `local_contour_layers.py`（局部衣摆图层）、`motion_registration.py`（局部位置匹配）、`build_motion_candidates.py`（逐帧合成与 GIF）以及 `audit_motion_candidates.py`（成品解码核验）。构造脚本依赖同目录已归档的 `try_local_candidates.py` 和 v5 供体参数。默认拒绝覆盖已有候选目录，可用新 `--output` 名称复现；03 细修启用 `--refine-early-shoulder --emotes 03-awake`。
