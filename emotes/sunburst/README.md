# 星瞳与明前奶绿 · Sunburst 动态表情

参考素材和前两轮产物见 [Issue #102](https://github.com/Shuang-su/metaxingtong/issues/102)。本批使用 OpenAI Images Playground 的 `gpt-image-2.6-sunburst`，输出目标为 512×512 原生循环 GIF。

两组原生 GIF 各有独立入口。最新的[原表情包脸型版](original-pack-gifs/README.md)沿用对应来源的造型；先前的[聊天六宫格脸型版](six-panel-gifs/README.md)保留四个同名动作。可结合[逐样本复核](../../docs/changes/20261105-sunburst-emotes/references.md)对照。

## 拍手初稿的原件与验收

[查看第一版拍手 GIF](drafts/xingtong-clap-v1.gif)。Pillow 完整解码，FFprobe 交叉核对：512×512，9 帧均不同，逐帧为 200 ms，一轮 1.80 秒，loop=0；598599 字节。SHA-256 为 `b89ab55a0ebcda5c6878b7c6e5d9e5b146d4da33effcccb5027363526fdc296e`。第 5、6 帧双掌相碰，第 7～9 帧分开，第 9 帧和第 1 帧的张手位置相近。角色识别未获用户认可，实际差异与修正方向见复核记录。

### 第一版实际提示词

2026-11-05，在 Playground 的 Default project 单次提交，模型为 `gpt-image-2.6-sunburst`，Frame size 为 512×512，Output format 为 GIF，Number of images 为 1。以下为实际提交的全文。

> 画一枚中国虚拟偶像星瞳（XingTong）的原创二创动态聊天表情。正面半身，脸大手小，银白齐颈短发、弯月形呆毛、清澈蓝眼、脸颊小爱心、紫色上衣有醒目的荧光绿拼色。柔灰色清晰轮廓、少量大块高光、平涂腮红，像手绘的B站动态表情。四周留白，纯白背景，固定机位、固定比例，无字幕、无文字无水印。动作「好欸拍手」：先双手明显分开，身体微蹲一拍；笑弯眼，弹起时双掌在胸前相向拍合，要清楚看见接触；张手落回起始姿势，短发和呆毛随后回弹。双手始终可见，拍合与分开轮廓对比鲜明。短促、开心、首尾自然连续，无限循环的单幅GIF。

[首张结果卡截图](../../docs/changes/20261105-sunburst-emotes/playground-first-result.jpg)。

## 修订后的四个动作

依次生成星瞳「好欸拍手」「呆眼点头」和明前奶绿「探头笑」「鼓脸晃头」。各结果卡的模型为 `gpt-image-2.6-sunburst`，类型为 GIF，画幅为 512×512。[四条提示词](prompts.md) · [六宫格与四张修正版静帧对照](../../docs/changes/20261105-sunburst-emotes/reference-comparison.jpg) · [对照稿提示词](drafts/prompts.md)。

上排六宫格用于造型核对，下排每张仅展示一个采样时刻。完整动作与逐帧参数以下载的原件为准。

## 按原表情包脸型分组的新系列

前述「脸按六宫格」是已经生成的六宫格系列。另立[原表情包附图校样](pack-style-proofs/README.md)，包含 9 张可直接打开的本地 PNG。每组有自己的上传附件、提示词和来源。[七包 136 项索引](../../docs/changes/20261105-sunburst-emotes/xingtong-packs/README.md)收录逐包缩略图和 20 个动态原址。[绿瞳双人参考](../../docs/changes/20261105-sunburst-emotes/green-duo.md)留待双人线使用。

## 与 1024px 静态原画直接对照

[四张原图驱动的 1024px GIF 与一张 768px 原生直出 GIF](reference-1024-gifs/README.md)用于比较线条、渐变、发丝和动作。每张原图与动作关键帧分别保存；可打开 GIF 原文件查看完整循环。
