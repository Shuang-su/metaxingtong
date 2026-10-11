# 城堡厅共享白模 v1：结构技术候选，未来源验收

## 当前限制（请保留在截图前）
1. 仅下部约6级台阶存在/走势有来源支持；上部2级、平台、侧围护、屋顶和终端封闭为有限推断。完整去向未知，没有花园空间连接证据。
2. 下部踏步端点粗诊断仍有残差：4528拟合视角中位约16.7 px，4527近邻留出约11.0 px。人工像素读点约±5 px，另有遮挡/端点对应不确定性，因此这些不是正式精度成绩。
3. 宽正面4509暴露旧后窗高区、柱高/相机等整体比例残差；地砖、柱脚、家具还继承旧版。局部静态墙面点低误差不能作为全厅通过。

## 本次结构变化
在完整旧厅壳体上增加固定右侧真实拱口、3层实体拱券与侧框回边、单体承托的8级有限台阶及有限围护。修正冲突的旧重复右窗和踢脚线，近窗未观察端部缩短并标推断。逐对象检查：1571个网格不变，13个修改、13个移除、25个新增。所有视角同一几何，没有移物/隐藏或参考warp。

白模SHA256：4340c968751af0b439b1daed3b29ba3cfd7da246b2356670ed36ef3c4b348474
GLB SHA256：dd29ddb8fa96db247ce2f2ac5b0fb7fd44b0e2d9e1445e5ef6609a85fe796817

## 来源与留出
BV1aw411T7ws，2023-11-10回城堡咯！ https://www.bilibili.com/video/BV1aw411T7ws/

拟合帧：4528.936245、4529.796014秒。留出：4527.768968秒（仅近邻运动基线）、4509.252180秒（不同宽正面）。1080解码但有效画芯1180×664，未宣称原生1920导出。留出相机仅使用旧墙/柱静态约束，新拱口和踏步未作留出相机拟合；冻结后不再反馈修改几何。

## 图证（配合ISSUE_figure_manifest.json，不只归档模型）
- 正常室内主视角：renders/normal_main_clean.png。前柱造成真实遮挡，未隐藏。
- 拟合4528：qa/compare_fit_4528_contact.jpg；对应qa/overlay50_fit_4528_raw.png与clean.png。
- 拟合4529：qa/compare_fit_4529_contact.jpg；对应qa/overlay50_fit_4529_raw.png与clean.png。
- 留出4527：qa/compare_holdout_4527_contact.jpg；对应qa/overlay50_holdout_4527_raw.png与clean.png。
- 留出4509：qa/compare_holdout_4509_contact.jpg；对应qa/overlay50_holdout_4509_raw.png与clean.png。
- 内部检查：qa/normal_and_internal_inspection.jpg，原图renders/qa_arch_inside_*、qa_stair_return_*。
- 残差标注：qa/fit_4528_tread_residuals.png、qa/holdout_4527_tread_residuals.png。
- 原截图、画芯、暂停元数据及mask：inputs/与source_and_view_ledger.json。所有最终图均有模型SHA和相机/处理元数据。
- 早期相机尝试与放大读图留档在辅助证据中；用途和替代状态见qa/辅助图说明.md，不能混为最终冻结证据。

直接叠图公式：source RGB与同尺寸render RGB逐像素Image.blend(...,0.5)，不缩放或透视warp。OIDN版只作展示辅助；原始24采样渲染和原始直接叠图并存。

## 技术验证
1609网格、278324三角形；无开边/非流形/退化面/负体积，全部有UV，无隐藏或动画对象。真实孔洞射线无遮挡；8级顶面与连续承托一致；厅体及有限楼梯空间2048条围护抽样射线无逃逸。白模/保留材料候选几何一致；GLB回导名称、三角数与1e-5量化世界顶点哈希相同。UV另作逐三角形角的实际匹配：834972个角对，最大UV绝对分量误差2.384×10⁻⁷（容差1e-5），1609对象均单UV层；不等于纹理外观通过。

下一步是共同地面、柱高、后窗/墙深和相机的联合校准，再处理踏步残差；不能抬起楼梯或针对留出机位临时改物体。该Issue保持未来源验收。

## QA r2补充图证
- regression/compare_baseline_candidate_fit_4528.jpg：旧/新完全同相机、同光照、同白材质，显示旧窗/实墙到通洞、有限楼梯的改动。
- regression/compare_baseline_candidate_holdout_4509.jpg：宽正面同条件回归。
- regression/overlay50_baseline_candidate_*_raw.png：旧原始图/新原始图的直接50%叠图，另存全部旧白模原始与OIDN图及每图元数据。
- regression/regression_setup_verification.json：旧1597网格未改；相机、灯光、世界、白材质、色管相同；改动清单核验相符。4509共12201条8px采样射线最大深度差3.80×10⁻⁵，超过1e-4者0。只支持该机位采样范围，不能宣称全局无新增遮挡。4528有6个原地砖采样被新增脚座覆盖，作为新构件占地明确保留。

QA r2只补实际UV比较与上述旧/新回归，模型和原7张新白模原始图不变。
