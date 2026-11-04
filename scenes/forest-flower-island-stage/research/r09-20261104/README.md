# 森林巨树悬浮花岛 R09 本轮最终冻结归档（A–G 全部 FAILED，未验收）

本目录保存 471 个原文件，共 1617242412 B。R09 材质/白模 BLEND 与 GLB、官方原生1080与4K、历史失败、真实相对深度、阶段记录与独立QA全部原样归档。来源几何 A–G 全部 FAILED，不能将技术完整性或导出成功写成来源/用户验收。

入口：[最终报告](files/docs/FINAL_REPORT.zh.md)、[R09补充](files/docs/R09-4k-addendum.zh.md)、[材质BLEND](files/models/R09_material.blend)、[白模BLEND](files/models/R09_white.blend)、[材质GLB](files/models/R09_material.glb)、[白模GLB](files/models/R09_white.glb)。[主图](files/renders/R08_material/SOURCE_F_top.png)按最终报告明确沿用真实 R08 输出，不重标成新 R09 渲染；[G4K失败诊断](files/renders/R09_material/SOURCE_G_4K_top.png)保留树遮挡。

生产端最终套件为 R08 的28图加R09两张4K图，共30图；14张直接50%叠图，材白各8有效诊断角。八角是模型诊断，不是八来源机位。独立QA记录G的6/11假设花点被树首先遮挡，保留错误可见性，没有隐藏树或按镜头改变几何。全数组叠图公式、Blender回导、深度及几何审计均属制作端报告；归档端只核原件字节、4模型哈希、14组来源/渲染/叠图清单哈希和PNG尺寸，不冒称复跑或独立视觉验收。

全部21条真实原提交保留在 `history/forest-flower-island-original-20261104`，从原 R01 HEAD `55b89e69fa461f365913353cf9b7a5f49368d12a` 正常前进到 `2204e912a2929c032223ea011d86f5f81d331af2`。归档分支 `archive/forest-flower-island-r01-20261104` 从 `4d52bbe2b51eac969807b880c1f9ab43787f2196` 追加15条当前阶段映射及本说明；前6条映射继承。旧 R01 目录 `scenes/forest-flower-island-stage/research/r01-20261104` 的34路径完整保留；新 R09 独立目录不覆盖原件/回执，失败阶段不删除。`provenance.json` 提供全部逐文件SHA256/blob、阶段映射及固定入口。

原件元数据保持生产时内容：`CURRENT.json.geometry_scope` 仍写14相机，与最终报告/独立QA中的R09新增G后15相机不一致；原 `remote_verified:false` 及旧文中的待办也不改写。远端交付结果由本归档回执单独证明，不把这些旧字段当当前验收结论。

输入 Library `libfile_1ebf9ffca6f08191bc2c62ba6346c9b5` version3，456759218 B，SHA256 `1a2a966d845f1a13d72eb7e3f040d2db438d5d2df2c3285c1a302ed0d1eb92e7`。当前 Library helper 在本执行器物化并核大小/hash/身份；全量bundle无prerequisite，明确checkout原HEAD。Space保留，bundle仅作运输。

本轮只普通Git归档与新空仓回读，无建模、渲染、生产脚本运行、LFS、强推、main写入或安全修改。此前Issue/PR审批拒绝未获新确认，本轮不重试、不创建任何Issue/PR/评论。CI将按远端实际查询另记，不把0项检查当通过。回执追加于 `publication-verification/`，不是新制作阶段。
