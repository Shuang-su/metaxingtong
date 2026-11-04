# 三星梦境折叠：可见外侧手机局部研究

当前V03机位持久化阶段（几何仍V02条件代理），非完整新场，不是来源验收。模型只10网格手机物件，不含草坡/飞艇/屏幕/角色。真实来源为三张1080宽报道图，非原生视频帧、片内时刻未知。

- V03当前原件入口：versions/V03/models/，5个持久化机位与完整场景记录见versions/V03/docs/report.zh.md。来源失配未改，5.2229px的准确意义为8坐标分量RMSE。
- 以下根目录V02原件/渲染保留历史，不覆盖。
- 可编辑：models/phone-material.blend、phone-white.blend。
- 导出：models/phone-material.glb、phone-white.glb。GLB不含相机或灯；保持JSON/BLEND的HORIZONTAL画幅设置。
- 同源条件主图：renders/source7-conditional.png；直接50%叠图：renders/source7-direct-50pct.png；并排：renders/source7-side-by-side.png。
- 4个diagnostic图是同一几何诊断，不冒充8个独立场景源角。
- 逐物件证据、残差与失败：docs/evidence.zh.md；qa内为真实回导、拓扑、接触、特征投影与画幅核验。
- V01真实失败保留在versions/V01及首commit a02c199；V02阶段精确模型/图保留versions/V02。根目录是当前可运行脚本与依赖布局。
- depth-analysis为真实相对深度及失败记录，不作几何测量。independent-source-review为独立人工像素约束，不等于盲测或源校准。

运行：python scripts/fit.py；blender -b -t 4 --python scripts/build.py；blender -b -t 4 --python scripts/render-diagnostics.py；blender -b -t 1 --python scripts/verify.py。需原有Blender4.3.2与Python scipy；不请求新安装。主图/叠图后处理按docs所记固定等权RGB合成。重新运行会改根目录产物，历史冻结commit保持不变。
