# 主屋盖taper：只读证据包，不应用

本包没有新BLEND、GLB或渲染，不修改R05 production，也不引入R06b云实验。输入是已归档R05 e9e4291064a5157630e7ad4348c9eeea8ed300b1的models/roof-r05.blend，SHA256 57af46b19e8ace266c0d1ea1f4c2522f9d79ca52a26c3bbbf38a4d03e7d651df；诊断后再次读回仍同SHA。本包不重复包含大模型，回放脚本需将该原模型放在同级cyber-roof-stage-20261105/models/。

入口：docs/taper-review.zh.md。完整51对象世界包围域/45实际顶点与作者站点见results/r05-main-roof-projection.json。9个有界h假说完整点集、实际端环、下包络边与world交点见results/taper-only-scan.json；9×51对象位移/边长/壳厚对应见results/taper-object-displacements.json。原图和独立可见点/遮挡null在sources。

可视入口：results/taper-source11-contact.png，三个h的原尺寸屋盖裁片上叠数值投影，不是新渲染。红是条件source点，青是模型几何投影，绿是三角联合包络，黄是粗source带；所有原幅标图也保留。

结果：h=.55/.57只在11顶杆横向条件对应改善，杆端高度仍约+31px、坡接约+17.6px、左尖语义/高度仍失败。10脊出画，不能充作独立验证。10几何包络来自后坡推断底边而非前金梁，落粗带不是来源通过；11前坡包络仍太低。

当前连续x场虽固定前后檐中心线，但并未保持完整厚实体：h=.55前檐管最大位移0.061825模型单位；约0.12壳对应距离变0.115762..0.153983。clamp和管截面/壳厚影响均明确。基于这些回归，此场不应用，不用它强行生成可交付模型；也不推出所有缩脊方案不可能。今后基于中心曲面再生并重算厚度属于另阶段，尚未执行。

独立QA在results/independent-qa：从真实模型复算51物体基线和h=.55，确认位移/投影/厚度反例；只核包络见证点回投，没有重算全部9case或全部极值，未做first-hit可见性。不要把生产全扫描都说成独立全量验证。

未执行sx/dz扫描、自由相机拟合或高度另调。docs/scope.md保留初始提取阶段的计划语境，后续最终执行范围以本页及taper-review为准。SOURCE仍FAILED；非native/未知时刻/比例与背面推断限制保持。
