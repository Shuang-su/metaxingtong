# 汽车副驾局部 — 首轮重建候选

状态：**有明确边界的局部研究，未通过来源验收，不计作完整汽车或完整前排内舱。**

来源：星瞳_Official《【直播回放】【突击3D】车我回家！2026年08月28日19点场》，[BV1wwtN6sEwL](https://www.bilibili.com/video/BV1wwtN6sEwL/)。6069 秒为视频总时长。2026-10-29 收到并在本环境独立核验 4 张原生 1920×1080 PNG；原始字节及采集者清单保存在 sources/native。

范围：副驾门板与门槛、车窗开口/玻璃、外后视镜、A柱/局部顶棚/遮阳板、仪表台右端圆风口、有限可见座椅侧缘。有限底板、背面厚度和承接是明确推断。没有完整外车身、后排、驾驶台、完整座椅、品牌或车外城市。角色不建模，不凭角色身高定尺度。单位仅为模型单位。

关门源 2190.197282 / 2968.842253 与开门源 610.828893 对应同一扇门的独立时间状态；开门角度为试验值。所有相机共享几何和材质，状态通过公开帧号选择，不由相机名称触发。605.763813 的前向视野只作条件性上下文，不作为副驾几何硬约束；605→615 的无 seek 播放未记录精确切镜，不证明连续 3D 相机轨迹或完全几何同车关系。

本轮只在本地独立分支 scene/car-passenger-cabin 逐阶段提交，不推送、新建 PR 或 Issue，不改历史、main、校园和钢琴场景。GitHub 搜索 car 分支、汽车及 car Issue 均无命中；本地 README 原已列出汽车副驾来源候选。

来源边界：采集清单记载实际选择 1080P 高清，未证明所有更高可用档位已排除；没有跨 BV 后续回放补角，没有观看整部回放。相机未标定，三张侧舱图只有有限视角增量、角色遮挡严重。任何几何/导出检查通过均不能替代来源验收。

## 当前本地交付

- [主图 PNG 无损原件](renders/main/car_passenger_cabin_main.png) · [JPEG 展示预览](renders/main/car_passenger_cabin_main.jpg)（完整 1920×1080，不缩放，<900 KiB）
- [可编辑材质 BLEND](models/car_passenger_cabin_material.blend)（纹理已打包）· [同几何白模](models/car_passenger_cabin_white.blend) · [含门状态动画 GLB](models/car_passenger_cabin.glb)
- [检查说明与未完成项](docs/REVIEW.md) · [45 件逐物件证据表](docs/OBJECT_EVIDENCE.md)
- [原生来源清单](sources/source-manifest.json) · [完整源/渲染/50%叠图与局部裁切清单](qa/comparison-manifest.json)
- [几何检查](qa/geometry-report.json) · [真实 GLB 回导报告](qa/glb-roundtrip-report.json) · [回导 BLEND](qa/glb_actual_reimport.blend)
- [8 方位及额外开门检查联系图](qa/arbitrary_views_contact_sheet.jpg) · [全部相机/状态记录](qa/render-manifest.json)

当前 45 网格闭合流形、正体积、零退化面；窗孔400、槽体200、风口间隙208条局部射线检查通过。初版失败报告及修改前试图保留在 qa。几何检查范围和剩余来源残差详见 REVIEW，不代替完整内舱验收或用户确认。

原文件分别位于 models、scripts、textures、renders、qa、docs；不生成新 ZIP，不启用付费 LFS。该入口只是局部候选，不改变仓库16场历史计数或 CURRENT。
