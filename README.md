# metaxingtong

私有直播场景重建档案。模型、来源参考、白模/纹理、真实修改历史与检查证据按场景和版本保存。

## 当前状态与原文件入口

2026-10-11，16个场景历史PR（#17–32）及历史核验PR #35已通过merge commit合入main。各场原文件现在可直接从[main的scenes目录](scenes/)访问；真实历史提交和归档分支均保留。原件按真实版本保存相对布局，CURRENT用于导航既有候选，旧ZIP保留追溯。所有模型仍为待来源验收候选。

固定历史范围的269条评论、2248个图片展示位置已全部完整实显：此前2075处加Safari补验173处；此前2075处未重跑。历史范围待验、部分覆盖、已确认坏图和显示技术阻塞均为0，图证保持展开。新增研究PR #36–39及其图片另批待独立实显验收，不计入旧2248，也不属于本次历史合并。显示通过及历史合并不代表模型、来源、几何或相机验收。

[历史核验PR #35](https://github.com/Shuang-su/metaxingtong/pull/35) · [完整核验与缺失原件报告](docs/history-recovery-20261011/README_历史恢复与图证核验.md) · [逐场显示完成结果](docs/history-recovery-20261011/显示核验与待验清单.md) · [Safari原173处证据报告](docs/history-recovery-20261011/safari-original-173/原173处核验完成报告.md)

旧原件缺口仍按报告保留，不以新模型替代缺失旧版本。卧室旧标签中的“7.7”仅是旧模型的推定进深，不是已证实的真实尺度或最终验收状态。

| 场景 | main 原文件目录 | Issue | 历史PR |
|---|---|---|---|
| 教室 | [原文件](scenes/classroom/) | [Issue #1](https://github.com/Shuang-su/metaxingtong/issues/1) | [已合并 PR #17](https://github.com/Shuang-su/metaxingtong/pull/17) |
| 开放露台 | [原文件](scenes/terrace/) | [Issue #2](https://github.com/Shuang-su/metaxingtong/issues/2) | [已合并 PR #23](https://github.com/Shuang-su/metaxingtong/pull/23) |
| 城堡宴会厅 | [原文件](scenes/castle-hall/) | [Issue #3](https://github.com/Shuang-su/metaxingtong/issues/3) | [已合并 PR #24](https://github.com/Shuang-su/metaxingtong/pull/24) |
| 病房 | [原文件](scenes/hospital-room/) | [Issue #4](https://github.com/Shuang-su/metaxingtong/issues/4) | [已合并 PR #27](https://github.com/Shuang-su/metaxingtong/pull/27) |
| 列车 | [原文件](scenes/train/) | [Issue #5](https://github.com/Shuang-su/metaxingtong/issues/5) | [已合并 PR #28](https://github.com/Shuang-su/metaxingtong/pull/28) |
| 霓虹舞房 | [原文件](scenes/dance-studio/) | [Issue #6](https://github.com/Shuang-su/metaxingtong/issues/6) | [已合并 PR #25](https://github.com/Shuang-su/metaxingtong/pull/25) |
| 厨房 | [原文件](scenes/kitchen/) | [Issue #7](https://github.com/Shuang-su/metaxingtong/issues/7) | [已合并 PR #29](https://github.com/Shuang-su/metaxingtong/pull/29) |
| 卧室 | [原文件](scenes/bedroom/) | [Issue #8](https://github.com/Shuang-su/metaxingtong/issues/8) | [已合并 PR #30](https://github.com/Shuang-su/metaxingtong/pull/30) |
| 深月KTV开放舞台 | [原文件](scenes/ktv/) | [Issue #9](https://github.com/Shuang-su/metaxingtong/issues/9) | [已合并 PR #21](https://github.com/Shuang-su/metaxingtong/pull/21) |
| 海边吧台 | [原文件](scenes/seaside-bar/) | [Issue #10](https://github.com/Shuang-su/metaxingtong/issues/10) | [已合并 PR #26](https://github.com/Shuang-su/metaxingtong/pull/26) |
| 城堡花园 | [原文件](scenes/castle-garden/) | [Issue #11](https://github.com/Shuang-su/metaxingtong/issues/11) | [已合并 PR #31](https://github.com/Shuang-su/metaxingtong/pull/31) |
| 海滨开放场景 | [原文件](scenes/seaside-scene/) | [Issue #12](https://github.com/Shuang-su/metaxingtong/issues/12) | [已合并 PR #22](https://github.com/Shuang-su/metaxingtong/pull/22) |
| 星斯卡舞台 | [原文件](scenes/star-awards-stage/) | [Issue #13](https://github.com/Shuang-su/metaxingtong/issues/13) | [已合并 PR #32](https://github.com/Shuang-su/metaxingtong/pull/32) |
| 钢琴门廊 | [原文件](scenes/piano-terrace-nook/) | [Issue #14](https://github.com/Shuang-su/metaxingtong/issues/14) | [已合并 PR #18](https://github.com/Shuang-su/metaxingtong/pull/18) |
| 红金灯泡拱形舞台 | [原文件](scenes/red-gold-stage/) | [Issue #15](https://github.com/Shuang-su/metaxingtong/issues/15) | [已合并 PR #19](https://github.com/Shuang-su/metaxingtong/pull/19) |
| 暗色铁栏布景 | [原文件](scenes/dark-cell/) | [Issue #16](https://github.com/Shuang-su/metaxingtong/issues/16) | [已合并 PR #20](https://github.com/Shuang-su/metaxingtong/pull/20) |


汽车副驾目前只有局部来源，不计作第17个完成模型。

## 下载与查看

从上表进入main中的对应场景目录，按该场README及CURRENT索引查找普通原文件、依赖和历史阶段；已合并PR继续提供真实提交与讨论记录。拥有本私有仓库权限的账户也可使用Git取得原件：

```sh
git clone https://github.com/Shuang-su/metaxingtong.git
cd metaxingtong
git switch main
```

各阶段README、manifest及核验报告记录内容、原始事件日期、大小、SHA-256和Git blob SHA。普通模型、贴图、脚本、来源及QA原文件按相对布局保存；历史assets中的原ZIP或GLB继续留存。可按具体文件链接下载所需版本，后续交付以原文件为准。部分历史原包使用ZIP-LZMA，需要兼容解压器，未为改变压缩方式重打包。

## 2026-10-10历史归档快照

本节及下列账本保留2026-10-10的统计口径，不是当前仓库总量、最新阶段数或当前PR状态。

- 早期整包快照为38阶段、113个完整原件，其中82个原ZIP；当时的逐文件SHA-256、大小与ZIP CRC核验记录保留在[整包账本](docs/archive-status.json)、[中文摘要](docs/archive-status-summary.txt)及[独立远端回读](docs/independent-remote-binary-readback.json)。
- 随后的普通原文件迁移快照为39阶段，阶段和成员数见[2026-10-10迁移账本](docs/raw-archive-status.json)。其[下载说明](docs/raw-files-download.md)、[独立原文件回读](docs/independent-raw-readback.json)与[主模型依赖检查](docs/model-dependencies.json)均按当时范围阅读。
- 当前历史恢复与未取回旧版本以[2026-10-11核验及缺口报告](docs/history-recovery-20261011/README_历史恢复与图证核验.md)为准；本README上方记录历史合并后的main入口。

## 完整重建规则

[重建规则](docs/reconstruction-standard.md)覆盖登录后高清和后续回放同场多角度、场景与剪辑分类、白模到纹理、共享几何同机位叠图改进、完整有限室内、真实孔洞/厚度/承接、影子与实体区分、主视角确认及逐场Issue/commit/PR历史。

历史日期与实际补录commit时间分开，不回填日期。Library修订号不等于场景版本。观察、推定、检查通过项、来源残差和用户验收分别记录。历史归档合并只将可核实原文件及证据纳入main；各场未解决的来源门槛和用户确认状态继续适用。

## 2026-10-10来源与版本更正记录

- 教室：历史HD QA v0和分类修订v1分别作为第6/7阶段保留，两张主图字节未改。[D叙事背景分类更正](docs/source-coverage/2026-10-10-classroom-reclassification.md)说明其与正片同模型/布局仍待关联，不作为现场桌数硬约束。
- 教室：[课桌拓扑更正](docs/source-coverage/2026-10-10-classroom-topology-correction.md)。旧20桌／六列仅历史冻结基线，未获正片拓扑验证；T1/T2/T3分别追踪，不固定20填满房间。后续未保存研究候选不计为本轮整屋交付。
- 列车：第3阶段新增HD r03候选。原模型/评审身份为Library v2，新增来源与主图为v0；精确来源拟合未通过、皮革材质取舍和8个极小导出三角零角法线例外均保留于Issue #5和包内说明。
- [首轮16场来源覆盖审计](docs/source-coverage/2026-10-10.json)作为当时真实记录保留，后续变化通过新增阶段与评论补充，不倒改旧工件。
