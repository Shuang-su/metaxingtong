# 02 / 03 局部边缘与动作候选 v8

接续已发布独立分支 `7be64b73e589ed4dee4b1cc2ee0441856b5689c0`。开工时远端仍为同一提交，源分支保持 `76051cf96bffc57200f90a6e4d88ed1ae9812287`。本次仅修改独立修补分支，原件与前序失败尝试全部保留。

本轮是有实质改进的动态候选，未宣称最终验收通过。选用 02 的 `v8-local-r1` 和 03 的 `v8-local-r2`。

## 改动与核验

| 项目 | 02-butterfly | 03-awake |
| --- | --- | --- |
| 时间轴 | 58 帧 / 4860 ms | 54 帧 / 4650 ms |
| 改动帧 | F24–28 / 580 ms | F1–33 / 2900 ms |
| 修补 | 正确手掌下方 2.4 px 窄白线连接 | F1–27 领口；F10–33 连续衣料褶皱 |
| 遮罩外、正确手部、绿色区域 | 均 0 像素变化 | 均 0 像素变化 |

02 保留此前真实衣料修补，仅接续断开的白色裙边，逐帧跟随已有衣摆位置。03 F1–4 使用正常 F54 的真实领口像素，改善循环接合；F5–27 使用 F28 领口像素，以较自然的高度配准。F22–27 只渐变衣领位置锚点至正常 F28，不混合整帧或手部。

03 膝部仍属于明确标注的局部重建：用两条连续、逐渐展开的浅褶皱替换重复纹理，只修改原修补区内奶油色布料，保留衣摆、袖口、正确手掌和裤袜。没有删帧、变速或隐藏正确伸手动作。刘海挑染、虹膜绿色以及主体灰棕发逐像素保持 v7。

初次 r0 领口试样因残余三角线和下沿错位被拒绝；r1 单帧修订后通过边界静态检查才扩展。r1 完整 03 动画仍有 F27→28 角度切换，保留并由 r2 衣领锚点过渡取代。所有试样、参数、遮罩、透明图层、脚本均在仓库。

## 动作与循环的实际结果

已查看 02 F23–29、03 受影响领口和膝部的原生裁剪，以及实际 112 px GIF 解码后的全部 112 帧。六个选用 GIF 都重新解码核对帧数、每帧时值、无限循环标记和尺寸。36 个交接原文件大小与 SHA256 全部一致。

以下是固定领口 ROI `[230,450,345,550]` 的原始 RGB 平均绝对差，范围 0–255。它用于记录局部跳变，不等于感知质量或实际播放验收：

| 边界 | v7 | v8 |
| --- | ---: | ---: |
| F54→F1 循环 | 46.55 | 34.69 |
| F4→F5 | 65.87 | 80.07 |
| F21→F22 | 70.54 | 67.74 |
| F27→F28 | 68.21 | 48.00 |

**未通过项：** F4→F5 的姿势／领口切换仍明显，局部差值还增大，不能宣称所有连续性通过；这是下一轮优先项。部分帧领口左下接线、细小色片及新衣料风格仍可见。02 两端原动作的裙褶切换仍保留。

此前浏览器本地预览被管理策略明确拒绝，本轮没有重试或绕过该路径。已交付可播放的 112 px GIF，但没有实际定时播放通过的记录。

## 配置、用量与费用

依 OpenAI API 技能仅检查本环境已有配置：进程环境没有可用 `OPENAI_API_KEY` / `OPENAI_BASE_URL`，仓库根目录无 .env 配置，平台没有挂载项目密钥。未从其他环境复制凭据、未新建密钥或计费设置。继续完成了独立本地修补。真实 API 请求 0 次、生成用量 0、本轮 API 费用 $0。

## 原文件和脚本

每组版本目录前缀：`emotes/sunburst/agent-emotes/<名称>/versions/20261115-boundary-refinement/<选用版本>/`。包含完整 768 px GIF、112 px GIF、v7/v8 动态对照、逐帧 PNG、遮罩、保护区、透明图层和 `construction-and-validation.json`。

脚本：`refine_local.py` 为局部算法；`build_v8.py` 编码动画；`audit_v8.py` 独立解码验证。构造拒绝覆盖已有输出，用 `--output 新目录名` 复现。只读核验可运行 `python3 docs/changes/20261115-emote-boundary-refinement/audit_v8.py`。

## 选用 GIF 的 SHA256

- `emotes/sunburst/agent-emotes/02-butterfly/versions/20261115-boundary-refinement/v8-local-r1/02-v7-v8-comparison-320.gif`：`ba9a0e4f7d8fbcd364daaa125a42f77404ba6b126ce0da29fb831c19162b21c1`，4980971 字节。
- `emotes/sunburst/agent-emotes/02-butterfly/versions/20261115-boundary-refinement/v8-local-r1/02-v8-CANDIDATE-master-768.gif`：`54a75540e96270d61fa1021cd397b98d1a08be28801a865ca892c60470415b7c`，10520770 字节。
- `emotes/sunburst/agent-emotes/02-butterfly/versions/20261115-boundary-refinement/v8-local-r1/02-v8-CANDIDATE-preview-112.gif`：`bd2aa7fc35fdcfe28c0ac9dc5c9b60d921233ef0049b83e3bf19257cceffcaa0`，511815 字节。
- `emotes/sunburst/agent-emotes/03-awake/versions/20261115-boundary-refinement/v8-local-r2/03-v7-v8-comparison-320.gif`：`8bf2f26630c7c846a783bf2c5f778f54238956bba4c70a6fa5a09d349302b157`，5754421 字节。
- `emotes/sunburst/agent-emotes/03-awake/versions/20261115-boundary-refinement/v8-local-r2/03-v8-CANDIDATE-master-768.gif`：`4fc6510cea949310100c723900335c326cc19161d94cce142a9221875ea90183`，12358921 字节。
- `emotes/sunburst/agent-emotes/03-awake/versions/20261115-boundary-refinement/v8-local-r2/03-v8-CANDIDATE-preview-112.gif`：`4b17e9b7fcb70eee63207ca3f1d8af9932f5f4b2d572f27e30d5f2bb5b412ab7`，566522 字节。

官方 Library 原文件身份另记 `v8-library-delivery.json`；发布回执与远端回读结果另存 `/workspace/emote-local-patch-review/v8-publication/`，以真实结果为准。本轮不创建 ZIP。
