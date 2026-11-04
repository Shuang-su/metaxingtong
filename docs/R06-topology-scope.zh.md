# R06实体、自然表面与未验证厚度边界

自然开放场不需要凭空加墙顶，但不代表水/岸地形厚度已验收。以下区分模型实际拓扑与来源状态，整场没有宣称为闭合体积。

- primary_leaf_shell：1个，开边0个。Closed mesh with real modeled thickness nominal0.035 arbitrary model units. Thickness is inferred, not observed metric truth. No claim of continuous self-intersection/collision proof.
- vein_closed_tubes：19个，开边0个。Closed capped vein geometry. Radius/attachment inferred; discrete finite-footprint samples passed, not continuous contact/source proof.
- water_open_surface：1个，开边1个。Single-sheet wave surface, no modeled bottom, volume or water depth. Finite boundary is a modeling extent, not observed lake boundary. Reflections do not imply lakebed.
- finite_shore_open_surfaces：2个，开边2个。Two finite ground-top surface sheets without bottom or side thickness. Bank profile, junction, submerged extent and supporting volume are unverified/inferred. Outdoor scene does not waive this limitation.
- vegetation_open_leaf_sheets：515个，开边515个。Zero-thickness foliage sheet proxies with double-sided shading, not closed leaf solids or measured leaf thickness. Exact instances and attachment are not source-confirmed.
- closed_vegetation_supports：2162个，开边0个。Individually closed trunk/rachis meshes. This does not establish root contacts, inter-object collision freedom, or matching source plant topology.
- closed_rock_proxies：4个，开边0个。Closed low-poly rock proxies. Position/shape/count/underwater contact inferred, not source-confirmed.
- other：0个，开边0个。Must inspect individually before claiming a topology category.

详见qa/r06/topology-scope-by-class.json中的全部稳定ID及精确边数。主叶舟壳闭合且有实际厚度，植物叶面为双面薄面代理（GLB实际doubleSided逐材核验）；湖水1面和岸地形2面无底、无侧厚度，湖深和岸下支撑体积未知。闭合杆管不代表每个根/枝/地表接触真实。全场三角碰撞和持续物理接触未检，不能宣称全场物理/来源通过。
