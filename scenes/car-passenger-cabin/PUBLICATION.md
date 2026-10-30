# 汽车副驾局部归档索引 — 2026-10-30

**状态：来源未验收的局部候选；r02 相机试验和 r03 共享剖面均未采用。** 本归档保留真实制作历史、失败报告和原始模型，不把局部研究计作完整第三场或完整汽车内舱。所有原有提交保持原 SHA 和实际时间，不合并到 main。

场景分支为 `scene/car-passenger-cabin`。模型、白模、GLB、纹理和真实版本记录只保存于 Git；预览图片和对照报告可独立展示。归档前远端检查未找到本场景分支、Issue 或 PR。

## 来源与边界

来源：[BV1wwtN6sEwL](https://www.bilibili.com/video/BV1wwtN6sEwL/)，《【直播回放】【突击3D】车我回家！2026年08月28日19点场》。6069 秒是视频时长。四张原生 1920×1080 PNG 的原始字节、片内时间和 SHA256 均保留；详见 [来源清单](sources/source-manifest.json)。

S01 2190.197282 秒与 S03 2968.842253 秒关门，S02 610.828893 秒开门。S04 605.763813 秒前向夜路只作条件性上下文，不作为同车几何硬约束；605→615 秒播放关联不能证明连续三维机位轨迹。未完成整部回放核查、跨 BV 后续同场新角度或最高可用画质完整证明。

只重建可见副驾门板/门槛、车窗/外镜、A 柱/局部顶棚/遮阳板、仪表台右端风口及有限座椅边缘。隐藏厚度、承接和底面边界明确为推断。未建整车、后排、完整驾驶台/座椅、人物或城市；无实测尺度，不用人物定尺度。

## 真实版本

| 阶段及实际提交日 | 提交 | 结果 |
|---|---|---|
| 来源范围，2026-10-29 | `13c70e7` | 四原件身份与有限范围 |
| 初始白模，2026-10-29 | `d4732d0` | 同一座舱几何、同一门铰链与显式时间状态 |
| 材质初试，2026-10-29 | `03a68b8` | 可编辑 PBR；初始流形/法线等失败保留 |
| 实体修正，2026-10-29 | `f68fcb3` | 修复端盖、法线、退化面和镜支撑；真实 GLB 回导 |
| 初版交付，2026-10-29 | `32591b5`、`05d169a` | 主图、源/渲染/叠图、9 检查视角、逐物体证据；来源未验收 |
| r02 相机诊断，2026-10-29 | `71180bf`、`798f3c6`、`9381724`、`57fa4f4` | 无限线、有限线、遮挡约束试验及旧失败快照；均未采用 |
| r03 数值与实体，2026-10-29 | `b1e8dd3`、`028819b` | 五参数共享仪表台/风口实体，冻结来源相机；A 柱仅两参数数值假设 |
| r03 检查及结论，2026-10-29 | `d91a78a`、`dd44dfd` | 原尺寸叠图、独立像素检查、连接间隙证据；整体未采用 |
| 归档整理，2026-10-30 | 本文件所在提交 | 仅更新项目文档与校验清单；模型、来源、渲染原件保持 dd44dfd 字节 |

## 直接阅读入口

- 初版：[完整尺寸 JPEG 主图](renders/main/car_passenger_cabin_main.jpg)、[PNG 原图](renders/main/car_passenger_cabin_main.png)、[材质 BLEND](models/car_passenger_cabin_material.blend)、[白模](models/car_passenger_cabin_white.blend)、[GLB](models/car_passenger_cabin.glb)。
- 初版证据：[检查报告](docs/REVIEW.md)、[45 物件证据表](docs/OBJECT_EVIDENCE.md)、[直接 50% 叠图清单](qa/comparison-manifest.json)。
- r02 未采用：[完整报告](research/r02-camera-calibration/README.md)、[三来源联系图](research/r02-camera-calibration/comparisons/camera_study_contact_sheet.jpg)。
- r03 未采用：[完整报告](research/r03-shared-profile/README.md)、[源/原候选/冻结相机/共享剖面/直接叠图联系图](research/r03-shared-profile/comparisons/r03_contact_sheet.jpg)、[诊断主图](research/r03-shared-profile/renders/review/D1_MAIN.jpg)、[残差表](research/r03-shared-profile/residual_table.md)。
- r03 模型：[共享剖面材质 BLEND](research/r03-shared-profile/models/D1_shared_dashboard_material.blend)、[同几何白模](research/r03-shared-profile/models/D1_shared_dashboard_white.blend)、[GLB](research/r03-shared-profile/models/D1_shared_dashboard.glb)。

## 检查结论与剩余问题

初版 45 个网格闭合、正体积、零退化面，局部窗孔/储物槽/风口射线与真实 GLB 回导已检查；这些结果不能代替来源还原通过。帧 1 关门、帧 2 同一门轴开门 54°（角度推定），没有按相机改几何或隐藏物件。

r02 在固定共享几何下改善部分风口投影，但多特征、有限边线及真实可见性不能共同满足，镜子残差退步；失败试验有独立快照，未回写初版。

r03 使用同一冻结相机前后比较，风口中心欧氏误差由 115.6/97.9/104.2 降至 4.6/11.6/7.1 px。实际图像复核也确认局部改善，但风口比例、S02 相机 pitch 和 A 柱数值弧度触及原定边界；镜子/边线未共同改善，关门台面转折仍被镜座和门上沿遮挡。倾斜面板与台面底部另有 0.02290/0.04830/0.09910 模型单位连接间隙。故 D1 未采用，A 柱数值方案未实体化，没有扩大参数或逐点变形。

最需要的新证据是同一关门状态、无人物遮挡的副驾前角斜视，完整同框显示风口、台面上下转折、A 柱下接点、窗框和外镜，并记录明确连续运镜/时间。其次为固定机位的开门前后短连续段。材质织纹、风口叶片与反射/夜景照明仍未核准。

## 校验记录

2026-10-29 的 `qa/protected_after.json` 等保护报告是对应提交时点的历史结果。2026-10-30 归档只修改文字和清单，旧文档原件仍可通过旧 commit 获取；当前文档散列已更新，新归档核验见 `qa/publication-integrity.json`。所有 BLEND、GLB、PNG、JPEG 和纹理原件与 `dd44dfd` 逐字节相同。

远端精确 head、Issue/PR 链接、版本评论和该 head 的 CI 状态以对应 GitHub 记录为准。没有运行的 checks 不能写作 CI 通过；本地几何/图像核验也不等于远端 CI。
