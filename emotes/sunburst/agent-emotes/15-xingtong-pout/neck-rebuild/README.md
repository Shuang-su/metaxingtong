# 星瞳《鼓脸晃头》Images API 重制候选

2026-11-17 接续 da2ce5e。当前环境已实际取得可解码 PNG 与 OpenAI 请求回执，已完成 54 帧候选。未覆盖原版、上一版 neck-follow 或 main，未建 PR，候选尚未获用户视觉验收。

## 交付

- [320px 完整候选](full-review/chat.gif)、[768px 完整候选](full-review/master.gif)
- [与奶绿并排](full-review/paired.gif)、[原片／候选／奶绿动态对照](full-review/comparison.gif)
- [112px 检查](full-review/review-112.gif)、[54 组三栏逐帧对照](full-review/pose-comparison.jpg)
- [54 帧缩略图](full-review/contact-sheet.jpg)、[四张关键姿势](key-repair-review.jpg)

short-review 另存 F11–25 的 15 帧短段、每帧 PNG、允许编辑区域和技术检查。完整输出与其共享同一段结果。完整动画为 54 帧、4560 ms、无限循环，逐帧时值保持原片。

## 实际做法与保护范围

使用原项目既有 Images API：POST https://api.openai.com/v1/images/edits，gpt-image-2.6-sunburst，1024×1024、medium、PNG、n=1、180 秒、零自动重试。本次共 6 次成功请求：F17 颈肩拳袖、F17 去挂件、F11、F25、F11 接缝试验、F1。接缝试验未采用，见 rejected-trials.json。所有实际 PNG、输入散列与 request ID 均保留，未新建密钥，未将密钥复制到文件或输出秘密值。

F1／11／17／25 是实际 API 重绘关键姿势，并非 54 张独立生图。用改正后关键姿势间的局部形变和配准扩展动作，不再采用旧版首帧硬贴片与肤色检测整体升降。完整双拳和袖口随绘图变形，所有帧均移除头顶右上角蓝白挂件。侧发保留在衣领外侧，颈前的穿出发梢随颈肩重绘处理。

原头脸始终作为底图，原眼神、口型、镜头和时间表保留。下颊边界约 20px 接触过渡带及拳头前景遮挡允许局部变化，不能声称整张脸或首帧逐像素不变；首帧拳袖也已重绘。每帧 allowed-XX.png 外的原生 PNG／768px GIF 像素保持原片；独立眼部区域 x=100:560,y=320:540 保持一致。

API PNG 带透明通道，先正确铺在白底上，避免把透明像素的 RGB 当黑色补丁。原生 GIF 使用各帧原片色表并精确写回未改动像素的索引；新增区域受 GIF 256 色限制。320px／112px 为缩放导出，不作逐像素保护承诺。

## 实测验证

- 三份原始输入 GIF 已完整复解，散列、帧数及时值一致，见 resume-input-verification.json。
- 完整 5 份 GIF 经 Pillow 和 FFmpeg 独立解码，像素散列一致，均有 54 个独特帧、4560 ms、loop=0，见 full-review/validation.json。
- 54 份原生 PNG 与原生 GIF 的允许区域外变化为 0，眼部检查区变化为 0。拳头遮挡和下颊接触带单独计入允许区域。
- 有沙箱的 headless Chromium 通过 WebCodecs 实际解码 112px／320px GIF 并原速播放三圈，每圈访问全部 54 帧，文档未隐藏。报告与截图见 full-review/browser-playback.json、browser-playback-complete.png。这是自动定时播放记录，不等于用户视觉验收。共享浏览器工具未能启动，未冒称在共享窗口播放成功。
- 6 次 API 回执的输出 PNG 和输入散列已逐一验证。F17 风格参考曾有两个版本，实际输入字节保存在 keys/input-archives，映射可按回执 SHA 找回。

技术通过不代表动作自然。原片的姿势／画稿切换仍保留，例如 F21→22；关键姿势间的衣领纹理与发箍修补边缘仍可能有细小变化。请以原速动画判断是否采用，当前为供审阅候选。

## 离线重建，不调用 API

保存了全部真实 API 输出，不需要凭据即可重建。依赖版本见 requirements.txt，实测 Python 3.12、Pillow 13.0.0、NumPy 2.3.5、OpenCV 4.10.0.84；FFmpeg 用于双解码检查。

```bash
python compose_keys.py 1 11 17 25
python build_short.py
python build_full.py
python verify_short.py
python verify_full.py
```

python reproduce_offline.py 顺序执行这些命令，比较重建前后全部 9 个 GIF 的字节散列，保存 offline-reproduction.json。本次已实际执行：全部 9 个 GIF 重建前后字节一致，额外 API 调用为 0。

在本目录启动 python -m http.server 8767 --bind 127.0.0.1，另一个终端运行 python check_playback.py --full，可复查当前环境的 Chromium 播放。额外使用环境已有 Playwright 1.62.0 和 /usr/bin/chromium，明确保持浏览器沙箱开启。

edit_key.py 为单次在线调用工具，已有输出时拒绝重发；--check 只查输入，日常恢复不要重跑生图命令。edit_frame17.py／compose_frame17.py 是前期单帧脚本，完整候选以本节命令重建。旧 internal-* 文件只是上一聊天的内置工具历史试验，本次未用它们制作候选。
