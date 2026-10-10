# metaxingtong

私有场景模型与重建过程档案。首次历史补录：2026-10-10（UTC）。

## 归档原则

- 每个场景保留独立 Issue、归档分支和 Draft PR；未获明确验收的模型保持“审阅版”。
- 历史事实的发生日期单独记载；所有 Git 提交、Issue 与评论均使用本次实际创建时间，不回填或伪造旧提交日期。
- 从最早有证据的版本开始记载变更；缺失的模型不伪造。模型、纹理、检查证据和 SHA-256 清单分开记录。
- Library 附件的修订号和场景版本号是不同概念。当前文件名可能沿用早期名称，必须以内部说明和校验清单判定内容。
- 可观察来源、合理补全、未验证项、失败项和用户是否验收分别记录。仅完成历史交付不代表精确还原或验收完成。
- 不在本次归档中合并 PR、部署、公开仓库或添加版权许可。来源素材与模型权利仍需分别确认。

## 目录约定

`scenes/<scene>/history/`：按来源日期排序的版本说明。

`scenes/<scene>/versions/`：实际可读模型与交付包；每批含文件大小与 SHA-256。

`scenes/<scene>/spec.md`、`plan.md`、`report.md`：范围、补录计划、结果与限制。

本 main 提交仅初始化档案结构。实际资产与版本历史会随每个场景的 Draft PR 独立提交；不能将此索引视为模型已上传。

## 重建标准

[来源覆盖、几何检查与历史完整性标准](docs/reconstruction-standard.md)。所有场景均为重建候选 / 待来源复核；不声称每场均有新高清与独立多角度来源。

## 16 场归档入口

- [教室](https://github.com/Shuang-su/metaxingtong/issues/1)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [开放露台](https://github.com/Shuang-su/metaxingtong/issues/2)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [城堡宴会厅](https://github.com/Shuang-su/metaxingtong/issues/3)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [病房](https://github.com/Shuang-su/metaxingtong/issues/4)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [列车](https://github.com/Shuang-su/metaxingtong/issues/5)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [霓虹舞房](https://github.com/Shuang-su/metaxingtong/issues/6)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [厨房](https://github.com/Shuang-su/metaxingtong/issues/7)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [卧室（7.7深最终版）](https://github.com/Shuang-su/metaxingtong/issues/8)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [深月KTV开放舞台](https://github.com/Shuang-su/metaxingtong/issues/9)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [海边吧台](https://github.com/Shuang-su/metaxingtong/issues/10)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [城堡花园](https://github.com/Shuang-su/metaxingtong/issues/11)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [海滨开放场景](https://github.com/Shuang-su/metaxingtong/issues/12)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [星斯卡舞台](https://github.com/Shuang-su/metaxingtong/issues/13)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [钢琴门廊](https://github.com/Shuang-su/metaxingtong/issues/14)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [红金灯泡拱形舞台](https://github.com/Shuang-su/metaxingtong/issues/15)：Issue 已建立；实际模型提交 / Draft PR 待核验。
- [暗色铁栏布景](https://github.com/Shuang-su/metaxingtong/issues/16)：Issue 已建立；实际模型提交 / Draft PR 待核验。

各场景的模型与真实历史保留在各自归档分支/Draft PR；未合并到 main 的资产不冒称已位于 main。汽车副驾目前只有局部来源，不在完整模型归档清单内。
