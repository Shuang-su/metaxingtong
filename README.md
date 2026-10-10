# metaxingtong

私有直播场景重建档案。模型、来源参考、白模/纹理、真实修改历史与检查证据按场景独立保存。

## 当前归档结果

远端核验快照：2026-10-10 09:08 UTC。

- 16个场景，16个独立Issue和Draft PR；全部保持Open Draft，未合并。
- 原计划35阶段加3个新增阶段，共38阶段：33个模型/资产快照、2个独立QA版本阶段、3个纯历史证据阶段。
- 113个完整原件已入库，其中82个原ZIP。独立从GitHub重新完整clone后逐文件核对SHA-256、大小与ZIP CRC，全部通过。没有已提交分片。
- 当前可取得的原件已经补齐；未恢复的历史版本仍明确记为缺口，没有按文字重造旧模型。main保存规则与索引，实际资产位于各场归档分支/Draft PR。
- 所有重建仍是候选 / 待来源复核。登录后高清、后续不同回放同场新增角度、叠图残差处理及用户主视角确认尚未全部完成。几何和传输检查不替代来源验收。

[逐文件归档账本](docs/archive-status.json) · [中文核验摘要](docs/archive-status-summary.txt) · [独立远端原件回读记录](docs/independent-remote-binary-readback.json)

## 16场入口

- **教室**：[Issue #1](https://github.com/Shuang-su/metaxingtong/issues/1) · [Draft PR #17](https://github.com/Shuang-su/metaxingtong/pull/17) · 7/7阶段。
- **开放露台**：[Issue #2](https://github.com/Shuang-su/metaxingtong/issues/2) · [Draft PR #23](https://github.com/Shuang-su/metaxingtong/pull/23) · 5/5阶段。
- **城堡宴会厅**：[Issue #3](https://github.com/Shuang-su/metaxingtong/issues/3) · [Draft PR #24](https://github.com/Shuang-su/metaxingtong/pull/24) · 2/2阶段。
- **病房**：[Issue #4](https://github.com/Shuang-su/metaxingtong/issues/4) · [Draft PR #27](https://github.com/Shuang-su/metaxingtong/pull/27) · 2/2阶段。
- **列车**：[Issue #5](https://github.com/Shuang-su/metaxingtong/issues/5) · [Draft PR #28](https://github.com/Shuang-su/metaxingtong/pull/28) · 3/3阶段。
- **霓虹舞房**：[Issue #6](https://github.com/Shuang-su/metaxingtong/issues/6) · [Draft PR #25](https://github.com/Shuang-su/metaxingtong/pull/25) · 2/2阶段。
- **厨房**：[Issue #7](https://github.com/Shuang-su/metaxingtong/issues/7) · [Draft PR #29](https://github.com/Shuang-su/metaxingtong/pull/29) · 2/2阶段。
- **卧室（7.7深最终版）**：[Issue #8](https://github.com/Shuang-su/metaxingtong/issues/8) · [Draft PR #30](https://github.com/Shuang-su/metaxingtong/pull/30) · 2/2阶段。
- **深月KTV开放舞台**：[Issue #9](https://github.com/Shuang-su/metaxingtong/issues/9) · [Draft PR #21](https://github.com/Shuang-su/metaxingtong/pull/21) · 2/2阶段。
- **海边吧台**：[Issue #10](https://github.com/Shuang-su/metaxingtong/issues/10) · [Draft PR #26](https://github.com/Shuang-su/metaxingtong/pull/26) · 2/2阶段。
- **城堡花园**：[Issue #11](https://github.com/Shuang-su/metaxingtong/issues/11) · [Draft PR #31](https://github.com/Shuang-su/metaxingtong/pull/31) · 3/3阶段。
- **海滨开放场景**：[Issue #12](https://github.com/Shuang-su/metaxingtong/issues/12) · [Draft PR #22](https://github.com/Shuang-su/metaxingtong/pull/22) · 2/2阶段。
- **星斯卡舞台**：[Issue #13](https://github.com/Shuang-su/metaxingtong/issues/13) · [Draft PR #32](https://github.com/Shuang-su/metaxingtong/pull/32) · 1/1阶段。
- **钢琴门廊**：[Issue #14](https://github.com/Shuang-su/metaxingtong/issues/14) · [Draft PR #18](https://github.com/Shuang-su/metaxingtong/pull/18) · 1/1阶段。
- **红金灯泡拱形舞台**：[Issue #15](https://github.com/Shuang-su/metaxingtong/issues/15) · [Draft PR #19](https://github.com/Shuang-su/metaxingtong/pull/19) · 1/1阶段。
- **暗色铁栏布景**：[Issue #16](https://github.com/Shuang-su/metaxingtong/issues/16) · [Draft PR #20](https://github.com/Shuang-su/metaxingtong/pull/20) · 1/1阶段。

汽车副驾目前只有局部来源，不计作第17个完成模型。

## 下载与查看

打开对应Draft PR可查看该场历史提交和文件。拥有本私有仓库权限的账户也可通过Git取得完整原件，例如：

```sh
git clone https://github.com/Shuang-su/metaxingtong.git
cd metaxingtong
git switch archive/classroom-history
```

各阶段assets/保存完整原ZIP或GLB；README.md和manifest.json记录内容、原始事件日期、大小、SHA-256及Git blob SHA。历史包体积较大，可按账本中的具体文件链接选择下载。部分原包使用ZIP-LZMA，需要兼容解压器；没有为改变压缩方式而重打包。

## 完整重建规则

[重建规则](docs/reconstruction-standard.md)覆盖登录后高清和后续回放同场多角度、场景与剪辑分类、白模到纹理、共享几何同机位叠图改进、完整有限室内、真实孔洞/厚度/承接、影子与实体区分、主视角确认及逐场Issue/commit/Draft PR历史。

历史日期与实际补录commit时间分开，不回填日期。Library修订号不等于场景版本。观察、推定、检查通过项、来源残差和用户验收分别记录。本次没有合并PR、部署、公开仓库或授予版权许可。

## 最新来源与版本更正

- 教室：历史HD QA v0和分类修订v1分别作为第6/7阶段保留，两张主图字节未改。[D叙事背景分类更正](docs/source-coverage/2026-10-10-classroom-reclassification.md)说明其与正片同模型/布局仍待关联，不作为现场桌数硬约束。
- 教室：[课桌拓扑更正](docs/source-coverage/2026-10-10-classroom-topology-correction.md)。旧20桌／六列仅历史冻结基线，未获正片拓扑验证；T1/T2/T3分别追踪，不固定20填满房间。后续未保存研究候选不计为本轮整屋交付。
- 列车：第3阶段新增HD r03候选。原模型/评审身份为Library v2，新增来源与主图为v0；精确来源拟合未通过、皮革材质取舍和8个极小导出三角零角法线例外均保留于Issue #5和包内说明。
- [首轮16场来源覆盖审计](docs/source-coverage/2026-10-10.json)作为当时真实记录保留，后续变化通过新增阶段与评论补充，不倒改旧工件。
