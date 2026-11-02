# 2026-11-01 发布交接：有限恢复证据与收集规范v3

已完成正常Git发布、独立远端字节核验、两个Draft PR及既有Issue记录原位更新。没有建模、改模、渲染、执行恢复脚本或深度估计；没有使用LFS/Git Data API写文件、强推、合并、提交approval review或删除Space副本。

## 当前远端成果

| 范围 | 当前上游归档提交 | Draft PR | 文件入口 |
|---|---|---|---|
| 98原件恢复资料＋3归档说明/映射 | `c5858089c4508b6798566f67d911def53738dcd9` | [#91](https://github.com/Shuang-su/metaxingtong/pull/91) | [98原文件](https://github.com/Shuang-su/metaxingtong/tree/c5858089c4508b6798566f67d911def53738dcd9/docs/recovery-evidence-20261030/files) · [清单](https://github.com/Shuang-su/metaxingtong/blob/c5858089c4508b6798566f67d911def53738dcd9/docs/recovery-evidence-20261030/archive-manifest.json) |
| 规范v3及来源文件，共6最终路径 | `3b47c20d87670838443e188d9569aa0818842c8f` | [#92](https://github.com/Shuang-su/metaxingtong/pull/92) | [实际规范](https://github.com/Shuang-su/metaxingtong/blob/3b47c20d87670838443e188d9569aa0818842c8f/docs/reconstruction-standard.md) · [追溯映射](https://github.com/Shuang-su/metaxingtong/blob/3b47c20d87670838443e188d9569aa0818842c8f/docs/standard-update-20261101/provenance.json) |

两PR均open、draft=true、merged=false，base为main `6ad31e4b2fe8398060c33de20fc09f5edad427a7`。main未改变。head分支分别为 `archive/recovery-evidence-20261030-20261101`、`docs/reconstruction-standard-20261101-v3`。

## 独立原始历史与当前修订映射

- `history/recovery-original-20261030` → `27bece9ae7149aa0026b95c977ef4f159909dcf9`：1个真实独立根提交、20树、98blob，全部对象原字节远端读回一致。它是Oct30恢复快照根，不是此前丢失模型历史。
- `history/reconstruction-standard-original-20261101-v3` → `278332f1d073c1b2201dd2ef92544dca3f768631`：4个原提交、8树、6blob，全部对象原字节远端读回一致。独立根不冒充upstream祖先。
- `22cf9265fb14b7a14d9d960d4ed950f0bf5e682a` → 当前 `1c13f8ee41d559f3ddfc1f2365c88219c312061e`。
- `c64b4e26813dc73f07b2976466950add3c059c4e` → 当前 `0b3cadf591ddad1fda47f3d0e2ca217c87a7fc11`。
- `278332f1d073c1b2201dd2ef92544dca3f768631` → 当前 `3b47c20d87670838443e188d9569aa0818842c8f`。

当前提交采用执行时真实日期；原对象保留原作者/提交时间及父链。标准应用前upstream blob仍为 `528f758aad5bb7af152c002f88b9d1f9fe62c8b5`，无并发规范覆盖。

## 完整性范围

- 四个Library输入均正式接收，version0、大小和指定SHA256完全一致，Library身份已保留。
- 恢复原件98/98，共44,041,749字节；原自排除清单97/97匹配。16张原生PNG共39,843,694字节、全部1920×1080；另3张历史派生图明确区分。19图均实际解码。
- 最终归档路径107/107（恢复101＋规范6）均从GitHub独立取回大小/SHA/Git blob/字节核验；3个上游规范阶段也逐字节核验。
- 远端读回仓库先新建为空，无本地clone、alternates或共享对象库；从官方HTTPS Git拉取2个独立原历史完整对象，再过滤获取2个上游分支的元数据，读取每个所需文件时从origin补取缺失blob。未冒称把无关继承旧文件也全部读回。
- bundle仅传输恢复，未作为GitHub普通文件替代原件。标准v3.md实际应用到规范路径；699字节原manifest及原编辑来源说明保存。9,835字节patch由已恢复原Git差异推导，大小/hash完全匹配原manifest，标明并非单独下载附件。
- 规范文件24,445字节；SHA256 `45de199daf186e74b1a16185f4c1831a6fee2e5cb91da68cb4cb721d31826e2e`；Git blob `2828618bce769c32621e6220c4b98a28ec637088`。
- 原件最大3,523,898字节，普通Git限制检查通过。常规文档差异检查通过；归档patch中的空白上下文触发通用空格提示，保留与原清单一致的字节，没有改写该证据。
- 两head的statuses/check-runs/workflow_runs均0，combined status pending；没有CI，不称CI通过。

## Issue原位记录

- [Issue #85 / 6532860806](https://github.com/Shuang-su/metaxingtong/issues/85#issuecomment-6532860806)：精确正文与body_html链接通过，新增图5处。
- [Issue #86 / 6532862792](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6532862792)：精确正文与body_html链接通过，新增图5处。
- [Issue #87 / 6532864686](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6532864686)：精确正文与body_html链接通过，新增图6处。
- [Issue #88 / 6532866556](https://github.com/Shuang-su/metaxingtong/issues/88#issuecomment-6532866556)：精确正文与body_html链接通过，新增图3处。
- [Issue #90 / 90](https://github.com/Shuang-su/metaxingtong/issues/90)：精确正文与body_html链接通过，新增图0处。

四条既有恢复评论只追加当前发布结果和对应场景图片；Issue90原规则记录只前置发布状态。旧内容逐字保留，其他评论不改，没有新增重复评论；评论计数仍85=1、86=1、87=2、88=6、90=9。

## 剩余限制 / 阻塞

- 本批不含BLEND/GLB/GLTF；F07、M03、后续重制模型、最新104项快照/最新bundle仍未恢复。源码候选不等于原模型或完整可重现依赖。没有今天新模型完成或场景验收的结论。
- 本批19个图片展示位置：0/19网页实显。2026-11-01T05:57:04Z尝试Issue85/评论6532860806，在页面加载前报 `net::ERR_CERT_AUTHORITY_INVALID`。同一主机浏览器检查停止，未改证书/代理/凭据、未禁用TLS，也未通过其他接口冒充网页显示。19源图字节/解码与body_html检查已完成。
- Space副本未删除，交由负责人根据上述逐文件及原对象核验范围处理；本报告不声称缺失模型已有远端备份。

## 本地证据

- `input_verification.json`：四输入大小/hash/身份。
- `remote_verification.json`：107路径及5原始commit全部对象完整远端读回。
- `standard_commit_map.json`：3次当前规范提交映射。
- `publication_readback.json`、`body_html_verification.json`：PR/Issue精确读回及未改内容检查。
- `ci_readback.json`、`browser_display_verification.json`：无CI与浏览器阻塞实数。
- 工作树 `/workspace/metaxingtong-recovery-20261101`、`/workspace/metaxingtong-standard-20261101` 均干净。
