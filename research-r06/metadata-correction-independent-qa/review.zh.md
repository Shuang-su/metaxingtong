# R06b 图像来源描述勘误独立附录

审查 HEAD 881636283958f08ecd1d26267e408a5224bc48ac，相对 basis 07ddd671517ef17f303c68c9d2513caca3fd7c15 实际 Git 差分仅新增三个勘误文件，未改旧原件、图像或脚本。此次不运行 Blender、不重渲、不覆盖此前技术/图像 QA。

旧 models/roof-r06b-recovery.json 的 render_products 错误继承“R03 pixels reused…mesh/material…unchanged”，对于已经修改 CLOUD_2 并实际新渲的 R06b 不成立，必须停用该描述；旧文件作为失败历史保留。此次真实更正的是描述，不是撤销模型修改或声称新图复用旧像素。

新 models/roof-r06b-recovery-description-corrected.json 与旧 JSON 逐字段实际比较：只 render_products 改变、render_products_addendum 新增，所有其他字段 deep-equal，包括 World、render、objects/cameras/lights、active camera、源 BLEND/GLB 和诊断配方。restore_r06b_glb.py 实际代码不读取这两个描述字段。因此此前实际空场恢复的参数验证仍适用；本附录没有重新执行恢复，也不冒称执行过新 sidecar。

清单实际核对 61 个 PNG 的字节数、SHA256、完整解码尺寸，全部相符：
- 18 张本轮真实渲染记录分为 R05 基线重渲 4、R06 失败试验 4、R06b 当前 8sample 8、R06b 当前 64sample 近景 2。只有其中 10 张属于当前 R06b，不把基线/失败算当前图。
- 41 张 renders/ 继承历史 PNG，与目录实际全部 PNG 集合相等。这包括旧 source、CHECK、补光诊断、联系表、主图 alias 与 crop；41 是文件数，不是独立渲染数或角度数。
- 2 张 R06b 材质 source10/11 direct50 为新派生对照，不计新增渲染/视角。

18 项所列渲染脚本均实际存在。来源归属与此前已核脚本/图像相符，但本附录的哈希校验本身不独立证明渲染事件或加载前输入 SHA；不补造原记录。其他手工描线、原源 crop、前后拼图不属于此处三个枚举集合，不能把该清单称全仓所有图像的穷尽清单。

另外，前次独立 image-integrity.json 中全部既有 R06b 模型/旧 sidecar SHA 和已记录相关图像 SHA 逐一复核未变。两 direct50 的原全数组公式检查结论无需重跑，仍限此前正确图像字节。旧 R05 八有效结构角不得转称 R06b 已重新八角验收；当前仍为局部类别假说，来源 FAILED、实例未证、非原生的结论不变。

机器证据 check.json 与复核脚本 check.py 同目录；旧独立 review.zh.md 保持原字节。本附录明确纠正原 sidecar 的失实文字，不改变有限技术结论。
