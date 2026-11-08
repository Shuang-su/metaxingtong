# 星瞳·鼓脸晃头

星瞳把两只手掌朝下平放，鼓起脸往一边偏头，斜眼停一拍，再呼气回正。星瞳和奶绿的 54 个时值一一对应，一圈 4.56 秒。[320 像素 GIF](chat.gif) · [768 像素 GIF](master.gif) · [星瞳与奶绿并排播放](paired.gif)

## 姿势和配色

头发分块、蓝瞳、发箍上的白色挂件、珊瑚色短腮红、浅蓝紫袖子和粉色内搭取自 B 站同套《揣手手》《老实》。修订后镜头留出了两只袖口和指尖的位置。[两张原作与前后版本并排看](reference-comparison.png) · [原包和 CDN 哈希](../references/sources.json) · [静态校样](../references/xingtong-detailed.png)

Sunburst 生成衣身和手掌底图，以及九个独立头部表情。以颈部为轴转动头层，沿用奶绿逐帧时值。手、袖口和胸前衣服固定在同一层。编码时为小面积的瞳色和腮红保留调色板位置。[生成原件和合成脚本](sources/fixed-hands/) · [实际提示词与输出哈希](manifest.json) · [逐帧动作数据](matched-motion.json)

## 成片核验

逐帧解码 768、320 和双人三个 GIF。母版最下方 138 行包含两只袖口、手掌和指尖，54 帧与首帧逐像素完全一致。另单独检查了每只手及袖口。三份 GIF 的星瞳画面均有 54 个不同帧，无限循环。浏览器按 112 像素原速播放，连续三圈的所有画面按顺序出现。[逐帧图](frames.jpg) · [逐帧 PNG](frames/) · [手区与色块实测](fixed-hands-check.json) · [112 像素三圈截屏](playback-112.jpg) · [回放数据](playback.json)

初版分镜、代理回执和竖拳造型作为制作历史保留。[初版分镜](storyboard.json) · [子代理回执](delegation.json) · [初版静态原件](sources/previous-portrait.png)
