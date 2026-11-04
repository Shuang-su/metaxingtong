# 森林巨树悬浮花岛 R09 普通 Git 归档回执（来源 A–G 全部 FAILED）

R09 为本轮最终冻结交付，不是模型/来源/用户验收。独立制作端QA明确所有 A–G 来源几何 FAILED；G的6/11假设目标被树先遮挡，未隐藏对象或按镜头改变几何。本执行器仅归档和核字节，未建模、渲染、运行原脚本、重算深度/叠图公式或重做Blender审计。

## 固定交付入口

- [材质BLEND](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/models/R09_material.blend) / [白模BLEND](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/models/R09_white.blend) / [材质GLB](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/models/R09_material.glb) / [白模GLB](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/models/R09_white.glb)
- [最终报告](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/docs/FINAL_REPORT.zh.md) / [R09官方4K补充](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/docs/R09-4k-addendum.zh.md)
- [主图](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/renders/R08_material/SOURCE_F_top.png) / [岛底](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/renders/R08_material/SOURCE_E_under.png)。主图明确沿用R08 SOURCE_F_top，来源F仍FAILED，不重标成新R09渲染。
- [G4K失败诊断](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/renders/R09_material/SOURCE_G_4K_top.png) / [G直接50%](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/comparisons/R09/material_SOURCE_G_4K_top_direct50.png) / [材质八角](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/comparisons/R08/material_eight-checks.jpg) / [白模八角](https://github.com/Shuang-su/metaxingtong/blob/352f3469782e95d792ba06f1064d4a5abcc96b23/scenes/forest-flower-island-stage/research/r09-20261104/files/comparisons/R08/white_eight-checks.jpg)

## 归档与远端证据

- 固定payload `352f3469782e95d792ba06f1064d4a5abcc96b23`；原HEAD `2204e912a2929c032223ea011d86f5f81d331af2`。
- 原history `history/forest-flower-island-original-20261104` 从 `55b89e69fa461f365913353cf9b7a5f49368d12a` 正常前进，21条真实原提交、作者/时间/父链及全部 615 原commit/tree/blob逐对象保留。
- 同一归档分支 `archive/forest-flower-island-r01-20261104` 从 `4d52bbe2b51eac969807b880c1f9ab43787f2196` 追加15条当前阶段映射、1条provenance说明和本回执metadata；前6条R01映射继承，不拆造或重写原制作历史。
- 最新471原文件共1617242412 B，最大普通blob76271476 B。全部30个R01源文件字节不变，新增441路径，零修改/删除；旧R01归档目录全部34路径也原样保留。
- 新空bare仓经GitHub官方HTTPS正常fetch原history，再fetch归档链；无本地对象复制或alternates。471原文件、473新payload路径、34旧R01路径（共507路径），21原/映射阶段及 615 原对象逐路径大小/SHA256/Git blob核验，每个唯一对象实际读字节比较，失败0，fsck返回0。无关旧main的promisor blobs不在全量下载断言范围，候选之外按树身份核不变。
- 回执/HANDOFF另增2路径，R09目录最终475路径，R01+R09共509路径；提交后两文件另做正常fetch/readback，结果留于执行器交接证据，避免自包含hash循环。
- 30张最终图与14直接50%均保留，材白各8诊断角；8张深度原件与独立QA保留。发布端另核4个R09模型哈希及14组来源/渲染/输出清单哈希和PNG尺寸；未把制作端全数组/视觉/Blender/深度验证冒称本端复跑。
- 原 `CURRENT.json.geometry_scope` 的14相机摘要滞后于最终报告/QA的R09实际15相机；`remote_verified:false`及旧待办属于生产时原文。原件不改写，归档状态以本回执为准。

## 输入与范围

Library `libfile_1ebf9ffca6f08191bc2c62ba6346c9b5` version3，`file_0000000054f881f9b617ed7a2820fd2e`，456759218 B，SHA256 `1a2a966d845f1a13d72eb7e3f040d2db438d5d2df2c3285c1a302ed0d1eb92e7`。当前resolved-reference helper已本地物化并核hash/大小/身份xattr；全量bundle无prerequisite，明确detached checkout原HEAD。Space保留，bundle只作运输。

CI只读查询时间 2026-11-04T02:32:26.054289+00:00：原HEAD及固定payload各0个commit status、0个check run、0次Actions运行（Actions查询不限PR事件）。没有CI记录，不称CI通过；最终回执HEAD另查询并留本地结果。

GitHub对8个超过建议50MB的普通blob给出提示，实际推送成功；没有LFS或强推。main和其它候选不改。本轮没有创建/重试Issue、PR或评论；此前拒绝仍待用户具体确认，没有换工具绕路。没有历史删除、安全配置修改、PR批准或合并。

完整机器证据见 [remote_verification.json](remote_verification.json)。时间变化/世界状态、花冠对应、植被背景、真实尺度/接触、全场碰撞和后续独立日期回放等未验收项继续保留。
