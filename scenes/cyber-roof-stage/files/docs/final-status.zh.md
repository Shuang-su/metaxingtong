# R05有限青绿金檐环台：交付状态

本机Blender4.3.2完成可编辑有限3D候选，当前入口models/roof-r05.blend与同几何白模、材白GLB、必需恢复JSON/脚本。R01至R05原件、真实失败和独立QA原始回存全部保留；R01/R02共同进入一个最早真实commit，不伪造两次提交。

## 图像计数与入口
- 本轮成套原渲22张：4来源机位材白1192×671 +16旧CHECK材白796×448（原08失败仍保留）+2新增DIAG09材白796×448。
- 4直接50%叠图均1192×671，独立全像素误差0，未warp/缩放。来源10为不同状态辅助，不冒同态。
- 有效方向8个：原01..07加单灯DIAG09；7原灯+1明确改变World/附加一盏灯，材白09配方完全一致。不算8来源角，也不算8原灯角。
- 主图renders/main-candidate-r04.png是CHECK01原字节alias，不增加图数；只展示有限结构，不冒来源机位匹配。
- 失败叠图renders/source11-direct50-r03.png与source10-direct50-r03.png，另有白版。
- 更新有效8角联系表renders/effective-eight-contact-sheet.png及effective-eight-white-contact-sheet.png；最后格显式CHANGED LIGHTING。旧8格联系表保留原08失败。
- 历史半尺寸预览、ROI、源点标注、旧累计补灯诊断和联系表均派生/历史，不混入22张原套图计数。

## 独立通过与不通过
R03修复259管条开放端帽；275单体mesh材白共享，0非流形/退化/loose且正体积。R05两GLB实际空场导入275mesh/11camera，双向顶点误差0；材白各fresh恢复11cam视框差0，World节点/链接、Area灯与保存状态一致。GLB本体缺Area/World，必须使用sidecar，不谎称GLB原生自含照明。

SOURCE还原仍FAILED：主屋脊、侧檐形态、金云实心浮雕、内台前缘/椭圆、DJ比例、背景媒体明显不匹配。原图仅报道WebP1192×671，时刻未知，非native、无登录最高画质证据，无后续独立回放角。10演员与11DJ观众态不同，人物/动态观众不建。背坡、厚度、台下支承和绝对尺度为推断，未验证全场接触/自交。未得到用户验收，绝不称完整房间/城市或还原完成。

有限单参数相机高度投影试验未应用，最优仍52.86px六分量RMSE，远超手工±10..15px粗误差带；源点非标定，遮挡后弧与出画外LED中心null。深度对檐/台严重失败，不据星观众预测凸块造家具。

完整独立记录：qa/independent-r02、independent-r03、independent-r04、independent-r05；来源/深度/排重见sources、qa/depth、qa/independent-dedup。所有模型与原套图保持不可变，最终普通Git/Space归档由backup串行处理；本制作任务不自行联网推送。
