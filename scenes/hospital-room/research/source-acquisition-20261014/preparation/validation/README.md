# 定向截面标注验证器（准备阶段）

本目录只提供纯 Python 3.9+ 的数据合同检查、合成单元测试及后续二维诊断工具。没有载入病房模型、拟合相机/几何或生成病房 render。旧 J1 仍为 **REJECTED**；这里没有恢复其合格性。`../restored/audit_H_upper_envelope.py` 和 `audit_BF_contour_branches.py` 仅被阅读以识别失败机制，未执行。

所有数值统计只能叫 `conditional_screen_space_diagnostic`。一个小 residual、成功退出码、`metadata_lint_ok` 或 `identity_state: verified` 都不是模型验证结论。

## 文件

- `directed_anchor_validator.py`：CLI 和可导入函数，无 NumPy/第三方依赖。
- `anchor_input.schema.json`：严格 JSON Schema Draft 2020-12，未知字段拒绝。
- `test_directed_anchor_validator.py`：只使用合成数据的 unittest。
- `examples/synthetic_upper_visible.json`：一个命名 upper branch，定 x 求有符号 y 误差。
- `examples/synthetic_partial_occlusion.json`：可见、遮挡、超 support、source 遮挡的混合例子。
- `examples/synthetic_named_physical_edge.json`：已核验、显式命名 physical edge 的有限线段欧氏距离。
- `examples/invalid_wrong_branch.json`：source upper 对 projection lower，必须 lint 失败，即便 lower 更近。

示例中的 SHA-256、尺寸和 native 状态是**合成测试字段**，不是任何真实病房图像的 provenance；示例文件名故意包含 `NOT_A_REAL_SOURCE`。它们可独立用于合同测试，不能作为真实标注或 native 解码的证据，也不能通过真实源文件核验。不要把这些字段复制进实际观测。

## 运行

在本目录执行：

```sh
python -m unittest discover -s . -p 'test_*.py' -v
python directed_anchor_validator.py lint examples/synthetic_upper_visible.json
python directed_anchor_validator.py score examples/synthetic_upper_visible.json
python directed_anchor_validator.py score examples/synthetic_partial_occlusion.json
python directed_anchor_validator.py score examples/invalid_wrong_branch.json
```

后两条故意分别退出 `3` 和 `2`。这些是预期防错结果，不是测试失败。

实际数据准备完成后，可这样显式指定源文件目录：

```sh
python directed_anchor_validator.py lint observations.json --source-root /path/to/native/source/files
python directed_anchor_validator.py score observations.json --source-root /path/to/native/source/files --output diagnostic.json
```

`score` **始终先 lint**；不会因为用户跳过单独的 lint 命令而绕过检查。`--source-root` 为可选的额外 SHA-256 与 PNG/JPEG **header 尺寸**核验：缺文件、hash 不符、尺寸不符或不支持的 header 都拒绝。该选项不解码像素，不能证明 `native_decode_status` 的真实性。未指定它时，结果明确标为 `metadata_consistency_only`，没有检查实际源文件。两个模式都保留 `native_pixel_decode_independently_verified: false`。

退出码：

- `0`：lint 通过；或 score 至少有一个可计样本、没有 rejected 样本。仍可能有 excluded 样本，必须查看 counts。
- `2`：输入合同/关联/源文件核验失败，完全不评分。
- `3`：输入合同有效，但至少一个比较没有可靠可见 support/存在截面歧义，或没有任何可计样本。保留其余可见、合格样本的诊断。

## 每条 observation 的必要信息

`frames` 是 native source registry。每个 observation 和 projection 都必须把完整 `source` 明确写出，并与 registry 完全一致；不能只凭 frame 名字猜出处。

`source` 字段：

- `frame_id`、小写 64 位 `source_sha256`、`source_filename`
- `actual_dimensions.width_px` / `height_px`，必须是原始 native 图像的真实像素宽高
- `coordinate_transform: "none"`
- `native_decode_status: "native_decoded"`
- `pixel_coordinate_convention: "top_left_x_right_y_down"`

crop、resize、letterbox、镜像、旋转、preview、normalized UV 或未知 decode 状态不能当作 none/native 输入。若先前在缩略图上点过坐标，必须先在上游重新核验到原始图像的坐标，完整保存该转换的独立证据，再建立符合此合同的 native observation；本工具不自动换算，也不隐藏换算。

`source_filename` 只接受 basename，不允许斜杠路径。`--source-root` 的路径不能通过符号链接逃出指定目录。JPEG header 核验使用编码宽高，不应用 EXIF 自动旋转；上游 native 解码必须使用同一未经变换的坐标系统。

观测语义字段：

- `observation_id`：唯一名字。
- `object_id`、`semantic_part`：事先核验的物体与部位，不根据最近距离自动选择。
- `contour_branch`：`upper / lower / left / right / physical_edge / physical_vertex / soft_shading`。
- `evidence_kind`：`silhouette / physical_edge / physical_vertex / soft_shading`；必须与 branch 相容。
- `identity_state`：必须显式为 `verified / conditional / unresolved`，没有默认值。verified/conditional 还要有 `identity_evidence` 说明；lint 只能检查其存在，不能判断说明真伪。
- `geometry_use_allowed`：必须显式写布尔值。conditional/unresolved 或 soft shading 不得设为 true；verified 也不会自动变成 true。这里的 true 只是这条观测的使用资格声明，绝不授权拟合或证明模型有效。
- `source_xy`：native 像素 x/y，必须在图像范围内，坐标允许小数。
- `uncertainty_px`：严格正的人工声明尺度，范围 1e-9 到 1e9 px。不是从数据估计的标准差。
- `visibility`：原图中该**采样点**的 `visible / occluded / unknown`。occluded/unknown 不计分；一个点不能用笼统 `partially_visible` 代替可见性判断。
- `sample_order`：可为非负整数或 null，只是记录顺序。
- `point_identity`：普通 contour 样本用 `state: "not_asserted"`，`physical_point_id` 与 `evidence` 均为 null。只有独立核验的 physical vertex 才能用 `state: "verified"` 并填写命名 3D 点和证据。工具不推断或验证对应关系；同序、近邻或低残差不能作为证明。

软阴影不能冒充物理顶点。可以保留 `soft_shading` 作为禁止几何使用的注释，但本工具不对它输出几何误差。`physical_vertex` 可以保存已核验身份，但当前没有提供 vertex-to-vertex 评分方法，避免把局部 contour 采样误当作物理顶点。

## 命名 branch-specific projection

每个 `projection_id` 都只能表示同一 frame、object、semantic part 和 branch，与 source observation 精确匹配。身份、provenance、是否允许几何使用均需显式提供。

每个 projection 包含一个或多个独立 `polylines`：

- `vertices_xy`：有序二维顶点，至少两个。
- `segment_ids`：每对相邻顶点一个明确线段名，在该 projection 内唯一。
- `segment_visibility`：每条线段的 `visible / occluded / unknown`，数量必须恰好等于顶点数减一。

部分遮挡必须在可见边界处分割线段。被部分遮住的整条线段不能笼统标 visible。被遮挡/未知的线段从计算中排除，不会跨过去连接端点；不同 polyline 之间也不会自动补线。

Source 点必须为 visible；两侧 identity 都必须 verified；两侧 geometry_use_allowed 都必须 true，否则记录为 excluded。几何真正可见性、物体身份和 branch 命名本身仍需上游核验，不能靠写一个 verified 字符串替代证据。

## 比较方法和拒绝规则

每条 `comparisons` 都明确给 `observation_id`、`projection_id`、`method`、`cross_section_axis`、`segment_id`。没有最近物体、最近 projection 或任意凸包选择接口。

### directed_cross_section

- upper/lower：固定 source x，计算该命名 branch 上的 projected y − source y。
- left/right：固定 source y，计算 projected x − source x。
- physical_edge：必须另外显式指定固定 x 或固定 y。
- `segment_id` 必须为 null，因为这里计算的是指定 branch 的截面，不是最近线段距离。
- 只有可见线段的截面交点可被采用。超出 support 直接 `unsupported_cross_section`，没有 endpoint/凸包/最近物体 fallback，也不额外创造罚分。
- 只有 occluded/unknown support 时为 `unsupported_visible_cross_section`。
- 同一截面穿过多个不同的可见交点时为 `ambiguous_multiple_visible_intersections`，不会选最近、上包络或下包络。请在上游进一步分割 branch。
- 截面与一条可见线段共线时为 `ambiguous_collinear_cross_section`，不会选任意点。
- 相邻线段的同一共享顶点只算一个观测。仅交点去重使用 1e-9 px 数值容差；support 范围从不扩大。长度 ≤1e-9 px 的退化线段拒绝。

本规则刻意比“在全凸包里取 min y”更严格：不能用把完整凸包标成 upper 的方式偷渡 lower；若凸包产生两次截面相交，直接拒绝。若上游把一条实际 lower 边错误命名为 upper，纯二维元数据无法识破，仍需真实图片/物体语义复核。

### named_segment_distance

仅在 source 和 projection 都为**明确 verified 的 physical_edge**时可用，`segment_id` 必须指向已存在的具名物理线段，`cross_section_axis` 为 null。该线段必须 visible。

计算 source 到这一条**有限线段**的欧氏距离，超出端点时夹到该线段端点，并输出 `segment_parameter`。这是该方法的明示定义，不能用于 directed_cross_section 的 support fallback，也不寻找其他更近线段。轮廓 silhouette 或 conditional/unresolved 身份不允许使用此方法。

## 结果怎样解读

每条比较是 `scored / rejected / excluded`，拒绝/排除记录没有 residual 或虚构 target。计数必须和数值一起读。

统计按 frame、object、semantic part、branch、projection、方法与固定轴分组，避免把不同身份或不同方法揉成一个“通过率”。输出 mean residual、median absolute、max absolute、RMS；没有合格样本则 statistics 为 null。所有统计名称都伴随 `conditional_screen_space_diagnostic`，不输出模型 pass 或验收阈值。

`error_over_declared_uncertainty` 只是误差除以声明的像素尺度，不是带已验证方差模型的 z-score，不支持置信度或统计显著性结论。一个视觉轮廓点在不同视角中一般也不是同一个 3D 顶点；不论 sample_order 是否相同都不会自动建立跨帧对应。

这个工具只验证合同是否完整/自洽，并在已指定二维关系上计算条件诊断；无法证明上游的像素解码、原图标注、身份、遮挡、物理顶点、投影相机或模型正确。真实标注仍要逐项视觉核验。
