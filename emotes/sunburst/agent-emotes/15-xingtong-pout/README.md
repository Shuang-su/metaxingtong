# 星瞳·鼓脸晃头

星瞳把手平放在身前，鼓脸偏头，停一拍再呼气回正。这一版恢复了初版的半垂眼、瞳孔高光、脸颊线条和细碎发丝。[320 像素分享版](chat.gif) · [768 像素母版](master.gif) · [和奶绿并排播放](paired.gif) · [1024 像素静态图](../references/xingtong-detailed.png)

## 三个版本

| 版本 | 形象与动作 | 文件 |
|---|---|---|
| 最初的精细 Q 版 | 银发偏粉紫，拳头在下巴两侧，随头一起转动。 | [原始 PNG](sources/previous-portrait.png) · [原始 GIF](versions/01-original/master.gif) · [原始分享版](versions/01-original/chat.gif) |
| 上次的重画版 | 简化了刘海、眼睛和脸型，双手改为平放。 | [静态 PNG](versions/02-redraw/portrait.png) · [768 像素 GIF](versions/02-redraw/master.gif) · [320 像素 GIF](versions/02-redraw/chat.gif) |
| 本次修复 | 在初版原画上校正偏紫的发色与袖色，重建被拳头遮挡的下颌和发尾，单独固定双手。 | [修复版 GIF](master.gif) · [原包与三版形象对照](reference-comparison.png) |

初版 PNG、原始 GIF 和上次的两份 GIF 均与相应历史提交逐字节核对。当前静态图和分享包第 15 项使用本次修复版。[版本哈希与逐帧核验](fixed-hands-check.json)

## 修复范围

眼睛、刘海和原有面部直接取自初版的 1024 像素画像。除补画区域外，主体按原图取像素，再校正色相。两块覆盖刘海和眼脸的区域在校色前与原作完全相同。嘴形取自初版九格分镜。Sunburst 带图编辑只提供两份修补素材，即被拳头遮住的下颌、发尾，以及独立的衣身和双手。两次实际提示词、交付图来源与哈希可复查。[初版分镜](sources/keys.png) · [下颌修补提示词](sources/restored-detail/fill.txt) · [衣身和双手提示词](sources/restored-detail/arms.txt) · [合成脚本](sources/restored-detail/restore.py) · [素材清单](manifest.json)

校色依据来自 B 站同套《揣手手》《老实》。原画刘海取样为 RGB (205, 193, 209)，最终 GIF 同一处为 (197, 194, 201)，《老实》的同类中间色为 (198, 195, 202)。[原作索引](../references/README.md) · [对照图](reference-comparison.png)

## 播放核验

768 母版、320 分享版及双人版均解码出 54 个不同的星瞳画面，一圈 4.56 秒。逐帧比较两只手、袖口和覆盖两手的底部整带，三种文件的变化像素数均为 0。112 像素浏览器回放匹配到 6 个完整循环，包含连续三圈。[逐帧图](frames.jpg) · [各帧 PNG](frames/) · [三圈回放截屏](playback-112.jpg) · [回放数据](playback.json)
