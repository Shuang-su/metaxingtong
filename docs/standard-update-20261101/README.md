# 2026-11-01 收集与发布规则 v3：上游正常 Git 修订

实际规范位于 [docs/reconstruction-standard.md](../reconstruction-standard.md)，最终字节与收到的 v3 原文一致：24,445字节，SHA256 `45de199daf186e74b1a16185f4c1831a6fee2e5cb91da68cb4cb721d31826e2e`。

新增要求：Space可作临时模型/依赖备份，但不是必经中转；使用普通Git原文件，不用LFS；完整远端逐文件字节、SHA和依赖核验后才清理相应临时副本，优先可恢复删除。建模留在生产云电脑，Codex只做文件接收、正常Git发布与远端核验。原生截图的深度灰度分析须保留输入、方法/版本/参数、输出与掩码，区分亮度与深度；相对深度不作为米制测量或替代多视角验证。

## 真实历史关系

应用前当前upstream标准blob仍为 `528f758aad5bb7af152c002f88b9d1f9fe62c8b5`，与独立编辑仓根中的原文一致，无并发规范差异被覆盖。本分支以真实main提交 `6ad31e4b2fe8398060c33de20fc09f5edad427a7` 为祖先，按原三次修改分别留下当前正常commit；每条commit消息记录 `Original-Independent-Commit`。

原独立编辑仓4个commit及真实父链/作者日期完整保留于 `history/reconstruction-standard-original-20261101-v3`，tip为 `278332f1d073c1b2201dd2ef92544dca3f768631`。独立根只是当时读回原文的本地记录，不冒充upstream祖先。详细原对象、文件hash及对应上游阶段见 [provenance.json](provenance.json)。

## 输入与原文引用

- [原输入清单](original-input-manifest.json)原字节保留；其.md对应已实际应用的规范文件，.bundle仅用于内部恢复，不作为普通文件替代品入库。
- [原编辑来源说明](original-edit-provenance.md)原字节保留，其中“未push”等描述属于原编辑会话；最终发布状态以对应Draft PR为准。
- [v3差异](standard-v3-from-original-baseline.patch)由原独立Git根与v3执行git diff得到，9,835字节、SHA256与原输入清单完全相同；明确属于从已恢复Git推导的字节，不冒称单独下载了原.patch附件。

本任务只发布既有文档，没有执行深度估计、建模或渲染，也没有清理Space。规范更新及归档成功不表示F07/M03等缺失模型已恢复，不代表场景验收。PR保持Draft，main未经合并不会改变。
