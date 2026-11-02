# 2026-11-02 第一批仅发布归档：HANDOFF

远端原件验证完成于 2026-11-02T01:11:32.867022+00:00。本交接文档随后按真实当前时间正常 Git 提交。

## 已完成范围

三个独立来源 bundle 及一个单独海港原 PNG 经当前 Library 正式物化，在消费端核存在、大小和 SHA256。保留 64 个输入普通原件（73,063,701 字节），另 6 个归档说明，合计 70 个原始发布文件（73,128,903 字节）。本次两个回执文件不包含在上述 70 项内。

新建不存在的 bare 空仓，通过官方 GitHub HTTPS 正常 Git fetch 三条原始历史分支，再正常部分克隆获取三条真实 upstream 归档分支；没有本地 clone、对象复制或 alternates。逐路径 git show 读取实际远端对象字节，核大小/SHA256/Git blob，与传入原件相符；并核 8 个 upstream 阶段快照、8 条原始提交及其全部 95 个独立可达 commit/tree/blob 对象。另取回此前营地输入原图 3,202,090 字节，作为既有依赖，不重复计本批新采。fsck 通过；无关 main 继承的 promised blobs 不在全量字节断言范围。

机器回执：[remote_verification.json](remote_verification.json)。含全部 70 路径的 expected/remote_actual 大小、SHA256、Git blob、各阶段快照、95 对象、4 项 Library 身份、fetch 方法/日志、图片位置及 API HTML 读回。树完整性、实际字节取回和网页显示分开记录。

## 固定原件与发布入口

|范围|原件/全部发布文件|已逐字节验证的 payload commit|Draft PR|
|---|---:|---|---|
|colonnade|14/16|[ee5f8507bd220a9eddebfe7044d7a7563d6586dc](https://github.com/Shuang-su/metaxingtong/tree/ee5f8507bd220a9eddebfe7044d7a7563d6586dc/scenes/lantern-petal-stage/research/colonnade-remake-cp01-20261102)|[#94](https://github.com/Shuang-su/metaxingtong/pull/94)|
|depth|31/33|[55ebf7b60e5fc69dceeb3592286626170c8d4cde](https://github.com/Shuang-su/metaxingtong/tree/55ebf7b60e5fc69dceeb3592286626170c8d4cde/docs/depth-analysis-20261102)|[#96](https://github.com/Shuang-su/metaxingtong/pull/96)|
|festival|19/21|[9aec955aa67de333816512da5b7ad0ce26cacffd](https://github.com/Shuang-su/metaxingtong/tree/9aec955aa67de333816512da5b7ad0ce26cacffd/scenes/festival-ring/research/remake-r00-20261102)|[#95](https://github.com/Shuang-su/metaxingtong/pull/95)|

三 PR 的 base 都是 main `6ad31e4b2fe8398060c33de20fc09f5edad427a7`；均 Draft、未合并。深度分支在上述 payload 之后还增加本回执 commit；不把回执更新误称原生产阶段或模型变更。main 未修改。

## 唯一阶段记录

- colonnade：[Issue 88 / comment 6566746612](https://github.com/Shuang-su/metaxingtong/issues/88#issuecomment-6566746612)。
- festival：[Issue 90 / comment 6566747389](https://github.com/Shuang-su/metaxingtong/issues/90#issuecomment-6566747389)。
- depth_camp：[Issue 93 / comment 6566748302](https://github.com/Shuang-su/metaxingtong/issues/93#issuecomment-6566748302)。
- depth_harbor：[Issue 93 / comment 6566749370](https://github.com/Shuang-su/metaxingtong/issues/93#issuecomment-6566749370)。

原 Issue 88 / 90 的旧 M03/F07 丢失声明、失败与拒采历史不改写；Nov2 是新实际阶段。研究 Issue 93 不计新场景。评论中所有 PR href 与 14 个图片 src/canonical-src 已经 API body_html 精确核验；此结果不是网页实显。

## 原历史与真实阶段映射

### colonnade

原独立历史 `history/colonnade-cp01-original-20261102`，tip `b752755708fad0196306bc4da4e57aeb1b054964`；完整原对象真实作者、提交者时间和父链保留。

|原提交|原提交者日期|当前 upstream 归档提交|
|---|---|---|
|[8c67cd18b94e82485becfef540b99baebc8a6271](https://github.com/Shuang-su/metaxingtong/commit/8c67cd18b94e82485becfef540b99baebc8a6271)|2026-11-02T09:53:39+09:00|[64836436e0504defd2ba850af60ca214d51cef4c](https://github.com/Shuang-su/metaxingtong/commit/64836436e0504defd2ba850af60ca214d51cef4c)|
|[b752755708fad0196306bc4da4e57aeb1b054964](https://github.com/Shuang-su/metaxingtong/commit/b752755708fad0196306bc4da4e57aeb1b054964)|2026-11-02T09:54:39+09:00|[035ce29a61821a3bdd62b2cf94c15224d4b6c5c9](https://github.com/Shuang-su/metaxingtong/commit/035ce29a61821a3bdd62b2cf94c15224d4b6c5c9)|

Nov2 廊架 CP01 新制作的有限可编辑检查点；旧 M03 BLEND/原来源仍缺失。4 个材质/白模 BLEND/GLB，不是完整灯笼圆台。GLB 与旧 SHA 相同属于确定构造再生成，不证明旧文件恢复。没有本轮新原生来源对照、深度分析或渲染；全部尺寸、背部连接与材质待来源确认。

### depth

原独立历史 `history/depth-harbor-original-20261102`，tip `f20277101571cb47fb770da039aba47f3b7a5c46`；完整原对象真实作者、提交者时间和父链保留。

|原提交|原提交者日期|当前 upstream 归档提交|
|---|---|---|
|[c7ca89d7cfeb158f373fcaa644675394919e4ae4](https://github.com/Shuang-su/metaxingtong/commit/c7ca89d7cfeb158f373fcaa644675394919e4ae4)|2026-11-02T09:42:29+09:00|[365d8094c18fd8ecb5ef365543b2d2b14d2b1718](https://github.com/Shuang-su/metaxingtong/commit/365d8094c18fd8ecb5ef365543b2d2b14d2b1718)|
|[f20277101571cb47fb770da039aba47f3b7a5c46](https://github.com/Shuang-su/metaxingtong/commit/f20277101571cb47fb770da039aba47f3b7a5c46)|2026-11-02T09:47:00+09:00|[925d007684cb1d9ba7c60cfc7d3961acd33232c0](https://github.com/Shuang-su/metaxingtong/commit/925d007684cb1d9ba7c60cfc7d3961acd33232c0)|

营地旧原生帧上的 CPU 相对逆深度工具验证，以及海港首帧初步分析。官方模型 revision/权重 SHA/配置/脚本/实际原日志保留，99 MB 权重及 venv 不在本批。924×518 为模型网格，1920/3840 显示是派生插值；掩码保留失败与未知，255 置信度掩码表示未知。不是米制测量、几何验收或新场景；海港单张裁切正面尚未达到制作门槛。

### festival

原独立历史 `history/festival-r00-original-20261102`，tip `1ccae9c211b54e63af7b1e49d8ab3d5996cd27d2`；完整原对象真实作者、提交者时间和父链保留。

|原提交|原提交者日期|当前 upstream 归档提交|
|---|---|---|
|[211bd483cbb067ffb84a42e20e10ab2e5dc6e6e3](https://github.com/Shuang-su/metaxingtong/commit/211bd483cbb067ffb84a42e20e10ab2e5dc6e6e3)|2026-11-02T09:51:44+09:00|[6cd66313c7f595a16342badf5698684cbceded9c](https://github.com/Shuang-su/metaxingtong/commit/6cd66313c7f595a16342badf5698684cbceded9c)|
|[4397f87aac14599331c328107a64455dd8a8a462](https://github.com/Shuang-su/metaxingtong/commit/4397f87aac14599331c328107a64455dd8a8a462)|2026-11-02T09:56:34+09:00|[d07441924aca8911a2bc0ca97c64e06a501bf53b](https://github.com/Shuang-su/metaxingtong/commit/d07441924aca8911a2bc0ca97c64e06a501bf53b)|
|[f59a9e706c2b2af78fab2899780b63790d7e2867](https://github.com/Shuang-su/metaxingtong/commit/f59a9e706c2b2af78fab2899780b63790d7e2867)|2026-11-02T09:58:54+09:00|[adbbe00b568dd5d9bd4b2eaa8af7a0c5088130f3](https://github.com/Shuang-su/metaxingtong/commit/adbbe00b568dd5d9bd4b2eaa8af7a0c5088130f3)|
|[1ccae9c211b54e63af7b1e49d8ab3d5996cd27d2](https://github.com/Shuang-su/metaxingtong/commit/1ccae9c211b54e63af7b1e49d8ab3d5996cd27d2)|2026-11-02T09:59:23+09:00|[8dca5c3611aa820d05e904a6a1e449e0a2c20421](https://github.com/Shuang-su/metaxingtong/commit/8dca5c3611aa820d05e904a6a1e449e0a2c20421)|

Nov2 R00 为丢失旧 F07 后新制作的局部层台/边唇/暂定边灯（70 mesh），不是完整旧 F07。2 个新 BLEND/GLB；64 灯及尺寸均未确认。53.951826 s 原生 4K 是新补采，不是已丢失 52.898942 s 帧；3 张旧 F07 JPEG 是历史派生辅助。缺两角、完整结构、材料全套、GLB fresh-import 与来源验收；本检查点没有后续新渲染。

## 传入身份

|Library ID / version|文件名|字节|SHA256|
|---|---|---:|---|
|`libfile_5cecd1c0acec819193ee10c9682a27ff` / 0|colonnade-nov2-cp01-b752755.bundle|196155|`5b00d3e44d96912e194cfb2764c7cc615212c4576b3056708c357e75aaa0928c`|
|`libfile_91cd8e0173208191b901521dec649c01` / 1|depth-analysis-harbor-f202771-20261102.bundle|37560182|`27217886a0f14af739987c9a4ba27c265935f99b06960b1e8da8d99c155fb1ea`|
|`libfile_8bde37b381bc8191a56f92b7707f5d8d` / 0|festival-ring-remake-R00-20261102.bundle|12215590|`065424ac7af38792b3059b175a63283e27f85b2d4d8cf79130feb42bd090f1ac`|
|`libfile_4c622c58bfe48191a2e960230cf3c9af` / 0|BV1iteRzHEsK_1.093550_4k_preliminary.png|6194386|`812cd46f910320ff49755ef28c3ed8bab3b2f4a9f6a4cfa34379336f96af5584`|

## 未完成与明确边界

- 输入原件远端字节失败数 0；此前丢失的旧 F07/M03 原模型没有被这次新生成检查点替代为“已恢复”。
- CP01 没有新原生来源、深度或渲染；R00 只有局部台盘，暂定 64 灯/尺寸/多角/全材质/GLB fresh-import 未验收。新 53.951826 秒源不冒充旧 52.898942 秒帧。
- 海港首帧仍不足开建。深度模型原网格为 924×518，4K 展示是插值；不作测量、接触、隐藏结构或来源验收真值。
- 本发布执行器未运行生成脚本、Blender、渲染或模型推理；日志和图像是收到的原生产证据，不冒称重新验证。
- 网页图片显示 0/14。已知 Chromium 访问 GitHub 报 net::ERR_CERT_AUTHORITY_INVALID，未重新尝试已知阻塞路线，未绕过证书/代理。14 张图的远端原字节解码及 API img 属性通过不等于浏览器逐位置显示通过。
- CI 不能由无检查推定通过；最终精确 head 的状态在完成报告中单列，本回执不声称运行了 CI。
- 没有修改 main、强推、LFS、删除分支、合并、批准 PR 或删除 Space。Space 中同身份可能演进至新版本，母任务按版本和远端字节核验决定统一清理，不由本执行器删除。

本次回执与 HANDOFF 发布后另以正常远端 fetch 读回自身字节，结果在最终完成报告给出；本文件不预先宣称该后续动作已完成。
