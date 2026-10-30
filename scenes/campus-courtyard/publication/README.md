# 校园庭院原件与版本归档

状态：**重建候选，未通过来源验收，未经用户接受**。有限校园庭院，与医院分别管理；不存在已证实的空间连通、完整学校范围或真实尺度。实时渲染/预录属性未知。

当前几何冻结于 `87b37f98911f533605d5aebdd60756edb96fe951`（Stage03）。后续 Stage04 仅保留六个未采纳相机试验，几何、材质、照明、可见性和原相机不变。

## 可编辑模型与检查入口

- [材质 BLEND](../stage-03-contact-qa/campus-courtyard_material.blend)、[同几何白模 BLEND](../stage-03-contact-qa/campus-courtyard_white.blend)、[GLB](../stage-03-contact-qa/campus-courtyard.glb)。
- [GLB 实际重新导入 BLEND](../stage-03-contact-qa/qa/glb_actual_reimport.blend)、[纹理](../textures/)、[建模与检查脚本](../stage-03-contact-qa/scripts/)。
- [正常主图 PNG](../stage-03-contact-qa/renders/MAIN.png)、[1920×1080 JPEG 预览](../stage-03-contact-qa/renders/MAIN_display_preview.jpg)、[八角检查](../stage-03-contact-qa/inspection_contact_sheet_display_preview.jpg)。
- [四来源原生同机位对照](../stage-03-contact-qa/comparison/)、[逐物件表与 QA 原件](../stage-03-contact-qa/qa/)。
- [未注册补源原件](../stage-04-cross-bv-holdout/source/)、[失败相机诊断对照](../stage-04-cross-bv-holdout/comparisons/)、[来源身份更正](../stage-04-cross-bv-holdout/qa/correspondence_correction_2026-10-29.md)。

模型原件仅在 Git 归档；不生成新 ZIP。图片和报告可作为独立预览交付。历史源、旧模型、撤回试验和失败日志均保留，不能把归档成功称为来源通过。

## 真实阶段

| 阶段 | 实际日期（UTC） | 结果与限制 |
|---|---|---|
| 来源与共享白模 | 2026-10-29 | 四张原生1920×1080图属于同一BV；建立有限共享白模，保留首次渲染失败 |
| Stage02 材质候选 | 2026-10-29 | 材质/白模/GLB、四组直接50%叠图、八角检查；窗、植被、场地布局与相机仍有残差；错误立面与近纯旋转机位试验保留 |
| Stage03 接触/边缘修正 | 2026-10-29 | 改正长凳、篮架和灯脚的有限接触，拓展有限铺砖，修正花池/台阶交叠；四源和八角回归，材质与白模一致、GLB实际回导 |
| Stage04 相机诊断 | 2026-10-29 | 只加相机，未修改冻结几何；两组原生直接叠图与六个失败试验保留 |
| 来源身份更正 | 2026-10-29 | 较早BV缺无歧义跨期固定物对应，列为未注册补源；“反向视角”只是待验证假说 |
| 版本归档 | 2026-10-30 | 保留上述真实提交历史，以原文件和明确限制说明归档，不重写制作日期 |

逐提交 SHA、实际时间和原件哈希见 [history.json](history.json) 与 [originals_manifest.json](originals_manifest.json)。每次几何阶段的图、模型与QA属于该阶段，不混称最新状态。

## 来源及待查范围

基础来源：[BV1GqXMByE1s](https://www.bilibili.com/video/BV1GqXMByE1s/)，播放器时间3356.842934、3368.109825、3426.097342、3610.834976秒。原生PNG均1920×1080，逐图字节、SHA和采集状态保留。选择1080P高清，菜单中的更高高码率选项有会员限制，未声称其生效。

较早的 [BV1fwSEBqEPJ](https://www.bilibili.com/video/BV1fwSEBqEPJ/) 96.994858秒原图是未注册补源。原四图内部“近篮架—三球架—橙框门/台阶—外楼梯”关联较强；较早图缺共同桥接物，无法唯一对应前景篮架。场地总体次序相似不足以建立同一局部身份，也没有直接像素矛盾证明不同资产。它不满足更晚其他回放条件。

原四来源相机尚未标定。窗格与立面比例、树池/运动面/跑道位置、运动场涂装、植被和光照均有未解决差异；隐藏结构和尺度是推断。有限几何检查、文件可打开和GLB回导均不等于来源验收。Stage04失败只否定已尝试的对应/相机/布局组合假说，不据此自动改形。
