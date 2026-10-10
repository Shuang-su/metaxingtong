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

`scenes/<scene>/<阶段序号>-<阶段名>/`：按最早可核实历史开始的独立阶段；包含变更说明、实际交付原包与校验清单。原始事件日期与实际补录 commit 日期分开。

每阶段 `assets/` 保存未经改包的完整原件；`manifest.json` 记录大小、SHA-256 和 Git blob SHA。

`scenes/<scene>/spec.md`、`plan.md`、`report.md`：范围、补录计划、结果与限制。

main 保存项目规则与核验索引；实际资产与版本历史在各场景归档分支的 Draft PR 中。只有可达 commit/tree 中核实存在的文件才计为已归档，不能把索引或尚未提交的 blob 当作完成。

## 重建标准

[来源覆盖、几何检查与历史完整性标准](docs/reconstruction-standard.md)。所有场景均为重建候选 / 待来源复核；不声称每场均有新高清与独立多角度来源。

## 16 场归档入口

核验快照：2026-10-10 08:34:59 UTC。10 个 PR 均为 Draft，未合并；5 场收齐原计划可取得快照，5 场只有历史前缀，6 场尚无阶段入库。35 个阶段中 14 个已核验（12 个实物快照、2 个纯证据阶段）；100 个计划原始文件中 30 个已入可达 commit/tree，包括 25 个完整原 ZIP。另 70 个仍待，其中 26 个超过当前接口保守阈值。没有已提交分片。

[逐文件机器可读核验清单](docs/archive-status.json) · [中文核验摘要](docs/archive-status-summary.txt)

- [教室](https://github.com/Shuang-su/metaxingtong/issues/1)：[Draft PR #17](https://github.com/Shuang-su/metaxingtong/pull/17)；2/5 阶段，仅历史前缀已归档。
- [开放露台](https://github.com/Shuang-su/metaxingtong/issues/2)：[Draft PR #23](https://github.com/Shuang-su/metaxingtong/pull/23)；2/5 阶段，仅历史前缀已归档。
- [城堡宴会厅](https://github.com/Shuang-su/metaxingtong/issues/3)：[Draft PR #24](https://github.com/Shuang-su/metaxingtong/pull/24)；1/2 阶段，仅历史前缀已归档。
- [病房](https://github.com/Shuang-su/metaxingtong/issues/4)：0/2 阶段，尚无模型阶段入库。
- [列车](https://github.com/Shuang-su/metaxingtong/issues/5)：0/2 阶段，尚无模型阶段入库。
- [霓虹舞房](https://github.com/Shuang-su/metaxingtong/issues/6)：[Draft PR #25](https://github.com/Shuang-su/metaxingtong/pull/25)；1/2 阶段，仅历史前缀已归档。
- [厨房](https://github.com/Shuang-su/metaxingtong/issues/7)：0/2 阶段，尚无模型阶段入库。
- [卧室（7.7深最终版）](https://github.com/Shuang-su/metaxingtong/issues/8)：0/2 阶段，尚无模型阶段入库。
- [深月KTV开放舞台](https://github.com/Shuang-su/metaxingtong/issues/9)：[Draft PR #21](https://github.com/Shuang-su/metaxingtong/pull/21)；2/2 阶段，原计划可取得快照已归档齐。
- [海边吧台](https://github.com/Shuang-su/metaxingtong/issues/10)：[Draft PR #26](https://github.com/Shuang-su/metaxingtong/pull/26)；1/2 阶段，仅历史前缀已归档。
- [城堡花园](https://github.com/Shuang-su/metaxingtong/issues/11)：0/3 阶段，尚无模型阶段入库。
- [海滨开放场景](https://github.com/Shuang-su/metaxingtong/issues/12)：[Draft PR #22](https://github.com/Shuang-su/metaxingtong/pull/22)；2/2 阶段，原计划可取得快照已归档齐。
- [星斯卡舞台](https://github.com/Shuang-su/metaxingtong/issues/13)：0/1 阶段，尚无模型阶段入库。
- [钢琴门廊](https://github.com/Shuang-su/metaxingtong/issues/14)：[Draft PR #18](https://github.com/Shuang-su/metaxingtong/pull/18)；1/1 阶段，原计划可取得快照已归档齐。
- [红金灯泡拱形舞台](https://github.com/Shuang-su/metaxingtong/issues/15)：[Draft PR #19](https://github.com/Shuang-su/metaxingtong/pull/19)；1/1 阶段，原计划可取得快照已归档齐。
- [暗色铁栏布景](https://github.com/Shuang-su/metaxingtong/issues/16)：[Draft PR #20](https://github.com/Shuang-su/metaxingtong/pull/20)；1/1 阶段，原计划可取得快照已归档齐。

各场景的模型与真实历史保留在各自归档分支/Draft PR；未合并到 main 的资产不冒称已位于 main。汽车副驾目前只有局部来源，不在完整模型归档清单内。

## 完整需求与当前门槛

已将用户完整直播场景重建要求写入[重建规则](docs/reconstruction-standard.md)，包括登录后高清补采、后续回放同场新增角度、白模/纹理、同机位叠图改进与主视角确认。当前16场均为候选，[逐场来源覆盖审计](docs/source-coverage/2026-10-10.json)列明尚未满足的门槛；不把几何检查当作来源验收。

## 最新教室来源分类修正

[高清 QA v0→v1 与 D 叙事背景更正](docs/source-coverage/2026-10-10-classroom-reclassification.md)：D 尚未证明与正片同套模型，不再用其桌面数量硬约束现场几何；E→C 为硬切，A/B/C 也未因此通过。原模型、源图/叠图像素和主视角 PNG 未替换；新增 QA v0/v1 与两张主图目前尚未入 Git。此项另列于清单，不混入前述35阶段统计。
