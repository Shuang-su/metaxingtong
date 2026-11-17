# 星瞳·鼓脸晃头：统一奶绿画风的新原画版

按本次确认的方向，依据星瞳原生《老实》《揣手手》重新绘制，采用奶绿版的线条、比例、块面上色和制作流程。动作重新编排；紫色发箍保留，右上角蓝白挂件省去。

## 成片

- [320px GIF](delivery/chat.gif)、[768px GIF](delivery/master.gif)、[512px GIF](delivery/master-512.gif)
- [奶绿／星瞳并排](delivery/paired.gif)：左为奶绿，右为星瞳，动作不是逐帧复制。
- [112px GIF](delivery/review-112.gif)、[54 帧缩略图](delivery/contact-sheet.jpg)、[54 组并排对照](delivery/pose-comparison.jpg)
- [本次基础造型](sources/style-r1.png)、[九个原生姿势](native-nine-review.jpg)、[实际返回的原生 GIF](sources/native-nine-r1.gif)

完整成片 54 帧，一圈 4560 ms，无限循环。原画单格为 512px，统一裁去四边各 2px 后等比缩放导出；768px 是放大版。原生九帧源 GIF 是 512px、每帧 200ms，共 1.8 秒，不能与最终成片时长混淆。

## 制作依据和流程

星瞳原图是 162×162 的原生 PNG，其字节、B 站来源核验后的哈希保存在 sources 和 source-records.json。512px 的白底输入只是原图的等比放大，没有增加原生细节。银灰短发、大块刘海、弯呆毛、蓝眼、紫发箍、浅蓝紫大袖外套、白绒领和粉色内搭来自这两张图。风格输入取自奶绿原生动图的实际画面。

奶绿流程记录来自 codex/sunburst-emotes 的 76051cf96bffc57200f90a6e4d88ed1ae9812287：原生九姿势 GIF → 5 张 3×4 格过渡原画 → 9 个关键姿势和 45 张过渡画面 → 54 帧曝光表。此处复用相同格选与曝光表，重新设计鼓脸、左右轻晃、眨眼、呼气、放松和返回开头的表演，见 storyboard.json。

每幅都是完整人物原画，头、短颈、颈肩、双拳和完整袖口一起绘制。本次没有使用旧星瞳 GIF、头身贴片、分部位变换、光流补帧或画面交叉溶解。后处理只有白底铺平、全片一致裁边和缩放、编码时统一近白色及共用 GIF 色表。逐帧 PNG 与对应新原画格的整幅裁切逐像素一致。

并排对照仍使用一份 256 色表，两边各分配 128 色，避免星瞳的小面积蓝瞳被奶绿的棕绿颜色挤掉。额外检查对照中的蓝眼色相；对照 GIF 与单人主片的色表不同，不能要求每个颜色逐像素相同。

实际使用既有 OpenAI Images API：gpt-image-2.6-sunburst、medium、零自动重试。本次 7 次成功请求分别是 1 张造型图、1 份九帧原生 GIF 和 5 张过渡原画。所有真实返回字节、输入、提示词、request ID 和用量回执均保留。未使用旧生成校样作为星瞳形象输入，未新建或导出 API 密钥。

## 验证与边界

- 6 份原始来源文件和 7 次实际 API 回执逐一核验输入／输出散列。
- 9 个原生关键姿势、45 张完整过渡原画均有不同像素；54 个 PNG 均能对应实际新画格，见 delivery/manifest.json。
- 5 份 GIF 经 Pillow 与 FFmpeg 独立复解，帧数、每帧时值、循环标记和解码像素散列核对，见 delivery/validation.json。
- 112px／320px 在启用沙箱的 headless Chromium 中实际解码并按原时值播放三圈。报告和截图保存为 delivery/browser-playback.json、browser-playback-complete.png；这是自动播放检查，不是用户验收。
- reproduce_offline.py 会用缓存原画重新编码、复核并比较 5 份 GIF 的字节散列。实际执行结果见 offline-reproduction.json；不再次调用 API。

逐格检查覆盖九个关键姿势与五张过渡图的全部格子，重点看角色数量、发型与衣色、两只拳头、袖口完整性和颈部连接。生成原画之间仍可能有轻微的线条、眼型和衣褶变化；采用整幅姿势切换的表情包节奏。技术检查和像素不同不能代替动作自然度判断。

## 恢复和重建

离线恢复不需要 API 凭据：

```bash
python build.py
python verify.py
python reproduce_offline.py
```

Python 依赖固定在 requirements.txt；验证另需 FFmpeg。浏览器检查使用环境已有 Playwright 1.62.0 与 /usr/bin/chromium。先在本目录启动 python -m http.server 8768 --bind 127.0.0.1，再运行 python check_playback.py。

call_image_api.py 是单次在线制作工具，已有输出／回执时拒绝重发。日常恢复只使用已保存的原画；需要修改原画时另建请求版本，不覆盖真实来源与回执。
