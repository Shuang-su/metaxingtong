# 新场来源筛选阶段记录

记录冻结日期：2026-11-04。此包只交付来源筛选证据，不包含新场模型或验收结论。两张 JPEG 均为公开搜索返回的缩略图，不是播放器原生帧，未被用来建模。

## 排重范围

本次通过 GitHub 连接器读到 29 个 Issue：28 个场景记录及研究 #93。读取 Issue 文本不等于逐一看过全部源图。今日已经制作的森林花岛与湖上叶舟也算已有，不能再报新。

| Issue | 场景 |
|---|---|
|100|city-window-bedroom 城市拱窗卧室|
|97|harbor 海港|
|93|来源研究，非场景|
|90|festival interlocking rings|
|89|redmoon|
|88|lantern|
|87|desert camp|
|86|ferris cabin|
|85|arcade|
|83|interview whiteboard room|
|81|campus courtyard|
|79|car passenger cabin|
|76|piano seaside exterior|
|16|dark cell|
|15|red-gold bulb arch stage|
|14|piano terrace nook|
|13|star awards stage|
|12|seaside road|
|11|castle garden|
|10|seaside bar|
|9|KTV|
|8|bedroom|
|7|kitchen|
|6|neon dance studio|
|5|train|
|4|hospital room|
|3|castle hall|
|2|terrace|
|1|classroom|

Issue 链接格式为 https://github.com/Shuang-su/metaxingtong/issues/数字 。仅默认分支旧16场不足以排重。今日森林花岛、叶舟尚未从这一 Issue 返回中列出，另行排除。

## 已确认官方来源链与后续观察入口

1. BV1KF411f7Qu《虚拟偶像竟在直播间大打出手！》官方简介指向2023-07-30直播 BV1Ku4y1m7QS，BGM《Go High》《So Addictive》，注明UE5及动作捕捉。同日官方 BV1y14y1i7RF《你的自以为你的梦寐，都是神预言你的美》也指向该回放。登录恢复后先看短纯享全段识别宽景，再定位直播；本轮未取得可信片内时刻，不能虚构精确seek点。
2. BV1D94y1e7Dc《星瞳二周年丨照进深渊的光，从“星”觉醒！》官方同日链。实际取得的1146×716封面只有人物合成，不能约束空间。
3. BV1hu4y1S72B《虚拟偶像的直播摄像头开了...》官方简介明确2023-07-18直播和2D模型制作。登录恢复后先核片头背景是否等于粉化妆间；本轮尚未桥接，不因这个2D说明替另一片房间下结论。粉房来自粉丝BV1oP411579K，实际缩略图1728×1080，缺演出日期、官方原片和第二角。先看这段短片背景是否固定，再寻找同房3D使用；无可信片内时刻。
4. 父代理独立核到官方 BV18h4y1977m《暖暖·摇曳在星光中的小船》简介指向2023-05-27直播 BV1jm4y147Cv。同日 BV1VW4y1Q76a、BV14m4y1v7Et、BV1Vh4y1G7ZZ 为官方入口。没有可见像素，标题“小船”不能证明区别现有叶舟。登录恢复后先看纯享宽景，再核直播同场；时刻未知。
5. 已归档可明确seek的研究线索：BV1CF8h6BEDJ P1 900.015547及907.188832海滩留声机区，需星瞳实际使用桥接及独立虚拟机位；BV1hwEG6NEE3 3100.582142白沙发城市窗区，需取得真实图并排重。既有黄卧室3074.719183和Touchless135.163011缺真实虚拟视差；Touchless115.501707是斜拍大屏，不作第二视角。具体归档路径见findings.md。

可读官方页面：
- https://www.bilibili.com/video/BV1KF411f7Qu/
- https://www.bilibili.com/list/401315430?bvid=BV1D94y1e7Dc&oid=361731100
- https://www.bilibili.com/list/401315430?bvid=BV1y14y1i7RF&oid=786979453
- https://www.bilibili.com/list/401315430?bvid=BV1hu4y1S72B&oid=828520484
- https://www.bilibili.com/list/ml2385803926?bvid=BV18h4y1977m&oid=656945319

## 失败和剩余门槛

- 部分视频网页读取返回412；图像搜索未找到粉房第二角。公开图片的确切URL可正常下载，两图均已实际查看，未声称原生或高清解码。
- 归档大PNG fetch_file 返回空，github_fetch 二进制UTF8失败。父代理专用fetch_blob测试Touchless同样UnicodeDecodeError0x89，已停止，不重复、不猜传输端点。
- 浏览器安全登录交接仍由父代理管理；本轮完全不碰共享Chrome及中间认证状态。没有复制任何凭据。
- 当前没有足够证据开新场：需要官方身份桥接、真实3D使用、多角原生帧、最高实际可解码画质及完整排重。缩略图只能筛选，不能替代这些条件。
- 本阶段受阻仅影响这些候选的后续取源，不代表项目暂停；父代理已有模型修正与归档继续。

## 文件和完整性

两张图的来源、尺寸、SHA256和观察限制在各自JSON中。tree-manifest.json 覆盖除自身与.git外所有交付文件；清单自身及Git bundle哈希在外部delivery-manifest.json中记录。Git历史为本次筛选新建独立记录，不伪装成上游既有提交。
