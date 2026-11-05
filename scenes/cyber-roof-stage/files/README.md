# 青绿金檐环台有限重建候选

当前入口 R05，保留R03共享几何，实际保存2来源相机、8原检查相机和1独立补光诊断相机。来源/还原状态 FAILED，未获用户验收。不是完整房间，不是可考据城市。原生最高画质、实际片内时间、后续独立回放新角度仍缺。

- 可编辑材质模型：models/roof-r05.blend
- 同几何白模：models/roof-r05-white.blend
- 材白导出：models/roof-r05.glb、models/roof-r05-white.glb
- 必需恢复：models/roof-r05-recovery.json、scripts/restore_r05_glb.py。GLB未带Area灯与World，必须一起使用。脚本从空场导入，默认恢复材质GLB；白模恢复须把输入路径改为roof-r04-white.glb，输出到独立路径。原件/旧版本禁止覆盖。
- 主图：renders/main-candidate-r04.png（与check-01-front-oblique.png完全相同字节，检查角展示结构，不冒来源机位匹配）。同源机位图：renders/source11-r03.png。R04仅补存相机，无几何/材料/光源/源机位更改，复用R03真实像素。
- 原尺寸对照：两源材白render与direct50；都1192×671，不warp，10仍11固定DJ状态，不是同态验收。
- 8检查角：check-01..08材白PNG，796×448；不是来源基线。两张diagnostic-white-lit额外改灯检查，不能与原灯图比较成同态。
- 独立QA：qa/independent-r02保留开放端帽/恢复FOV失败；qa/independent-r03保留真实factory空场双GLB回导与材白恢复。R03只通过有限拓扑、共享几何、导出/恢复，不包含全场接触/自交或来源还原。
- 逐物件、推断、修订与失败：docs/object-review.md、scope.md、revisions.md。
- 手工点与一参数投影：qa/source11-manual-points.json、camera-height-only-test.json。未应用试验变更，残差仍大。
- 原源/深度/排重原件：sources、qa/depth、qa/independent-dedup；深度对屋檐/台面多处失败，不建观众凸块。

R01/R02/R03历史模型、失败脚本/日志全保留，均真实当前创建，不冒旧制作版本。无外部纹理依赖；全材质为程序定义，未将原图贴于模型。

## 交付真实存在性
R02只有材BLEND、白BLEND、材GLB、JSON，白GLB缺失；不能称R02材白双导出。R03/R04才各有材白两BLEND、两GLB、JSON。R01/R02仅半尺寸预览596×335，R02原尺寸渲染中断无产物；R03才实际输出原尺寸。

技术原件无需重渲可以编辑；8samples PNG有可见噪声，不冒高收敛精修。背坡/封口、台厚/台高与悬置支承均模型假设；金云只有线管代理缺实心浮雕面。模型主脊、台前缘与源图仍明显错位。source11当前275封闭mesh，不代表275个来源确认物件。

有效检查计数：原CHECK01..07加独立DIAG09同状态材白一对，7原灯+1明确补光角。原CHECK08暗/侧裁不计有效第8；早补光low-thickness累计灯状态只保留失败追溯。DIAG09默认灯态未写回模型；复现必须按R05 sidecar diagnostic09_recipe或freeze_r05_diagnostic.py独立执行。

## 最后独立复核结论
R04全部4原尺寸来源材白图、16普通检查图与4direct50已独立解码/实看；4叠图逐像素误差0，保存camera对配方矩阵差0。R05两GLB真实空场导入均275mesh/11cam，顶点误差0；两sidecar fresh恢复view_frame差0、World/灯同。材白09独立配方重建各恰4灯且环境完全同；01..07加09可计8个有限结构诊断方向，原08失败不计。完整机器记录和实际恢复BLEND在qa/independent-r04与qa/independent-r05。

仍不通过：SOURCE还原、登录最高画质与native帧、独立后续回放、未知尺度、背坡/支承、全场接触/自交、用户验收。几何可编辑和文件可恢复不能取消这些缺口。全部图为低采样诊断，不称最终精修。
