# C31 材质模型：仅补来源文字，不是新几何版

## 本次实际改动

派生文件：`hospital_C31_MATERIAL_PROVENANCE_ONLY_20261028.blend`。

原 C31 材质版中 26 个建筑部件缺少白模版已保存的 C26 来源说明。本次先核对同名对象的顶点、边、面、UV/其他几何属性与世界矩阵，再从原 C31 WHITE 逐字复制三个字符串属性：

- `C26_evidence`
- `C26_uncertainty`
- `C26_reference`

合计 26 对象、78 个字符串属性。对应窗框、柱状构件、帘轨及支点、墙面接缝和房间壳。**不复制 `C26_control_key`、参数对象或驱动，不调整任何尺寸。** 原 `c31/` 两份模型均保留不变。本文件不是 C32 几何候选。

## 历史标签的含义

属性名和文字保留 C26 原文，表示 2026-10-19 已记录的历史来源与不确定性，不表示本次重新标定或验收。尤其：

- “可见成员/线身份得到支持”不等于精确尺寸、位置、墙厚、房间深度得到验证。
- 隐藏延伸、精确直角、米制尺度、完整帘轨支点数量等仍是未经证实的假设。
- 继承名称中的 `calibrated` 不作为标定成功证据。
- C31 原有床端板局部候选及其残差原样保留；C30/C30B 床高方案仍被拒绝。

**没有新原生帧、几何改动、相机拟合、渲染或新的直接叠图。** 本次不宣称视觉更接近来源，不宣称室内几何完整或场景通过。

## 原始来源路径恢复

两张 C26 方向诊断所引用的旧原图此前不在恢复出的医院仓库中；现按既有 Library 身份恢复至本目录：

| 历史文件 | 当前相对路径 | 原 Library ID |
| --- | --- | --- |
| `frame_1107.723.png` | `source_dependencies/frame_1107.723.png` | `libfile_043b1e6106c08191a3a5063acb263b2a` |
| `frame_1116.243.png` | `source_dependencies/frame_1116.243.png` | `libfile_4ada25e261d481919626fb39b5808918` |

它们的 SHA-256 与未改动的 `../c26/direction_constraints.json` 完全一致。`source_dependencies.json` 保存精确 hash、字节数、Library 身份和路径映射。它们是**恢复的旧开发来源**，不是新补采、盲测或独立第二视角。

同标签中的 650/658 原图仍在 `../inputs/hospital_650.811153_native.png` 与 `../inputs/hospital_658.052095_native.png`。原生源视频为 `https://www.bilibili.com/video/BV1GqXMByE1s/`。C26 说明及其限制仍以 `../c26/README_C26.md`、`../c26/WHITEBOX_SCOPE.md` 为准；未重写原诊断历史。

## 验证方法

`add_architecture_provenance.py` 使用 Blender 4.3.2、禁用自动脚本执行进行派生和重开验证。`verification.json` 记录：

1. 原材质版、白模版及 C26 清单的 SHA-256；派生输出 SHA-256。
2. 26 组对象的同名对应、完整几何 hash 与世界矩阵。
3. 复制前后的属性原文。
4. 保存前后所有对象、网格、材质节点及链接、相机、灯光、世界、打包图片、场景/渲染设置、节点组、集合的语义状态 hash；预期差异列表为空。
5. 原文件字节未改；没有新增参数对象或驱动。

初次对应校验把 WHITE 独有的全白 `material_index` 属性存在性当成几何差异而停止，未输出模型。该日志与诊断保留为 `initial_correspondence_check.log`、`initial_correspondence_diagnostic.json`。修正后，仅在 WHITE/MATERIAL 的对象对应检查中排除材质索引属性；**材质版派生前后仍完整检查该属性、各面材质索引及材质状态不变**。这是验证器分类修正，不是为通过检查修改场景。

历史第二次校验日志保留于 `pre_update_correspondence_check.log`。读两文件状态前均明确更新依赖图，不启用新驱动、不改原默认值。恢复重跑仍失败，精确诊断保存在 `recovery_failure_diagnostic.json`：矩阵相同，但验证器的递归 RNA 读取通过 `uv_layer_clone` / `uv_layer_stencil` 旧式 UV API 惰性创建了 `.vs.UVMap`、`.es.UVMap`、`.pn.UVMap` 选择/固定属性。最终只避开这两个有读取副作用的便利指针，保留原始 UV、完整几何属性及 clone/stencil 索引的检查；不是放宽几何相等条件。`INT32_2D` 也改为直接 hash 整数值，避免泛型 RNA 摘要遗漏只读值。保存时禁用相对路径重映射，保留已有路径字符串。

`independent_verification.json` 与 `verify_independent.py` 提供第二次只读重开复核：逐对象比较全部自定义属性，确认恰好新增 78 字符串、涉及 26 对象，其他属性无差异；全场景 10 类语义状态完全相同。另在每次状态采集前后直接 hash 所有网格，确认验证器自身不再创建或修改任何网格属性。两张历史方向原图的字节数与 SHA-256 再次验证。

复现命令（从仓库根目录）：

```sh
blender -b --disable-autoexec -t 1 --python-exit-code 1 --python provenance_20261028/add_architecture_provenance.py
blender -b --disable-autoexec -t 1 --python-exit-code 1 --python provenance_20261028/verify_independent.py
```

脚本只输出本目录派生文件及验证 JSON，不覆盖原 C31。原生图不被重采样或改写。仅本地 Git 提交；没有远端推送。
