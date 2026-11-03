# 城市拱窗卧室舞台 R09/R09b 相机增量归档

R09/R09b仅D/E/F相机条件性改进，R08全部565mesh共享几何、材质灯光及A/B/C与8检查角不变。保留R09初解、F09接触/阴影语义歧义、全圆背面误配及R09c纯计算可见半圈复核。R09b底缘局部改善但同8点F均值/最大由5.371/22.434回归到6.590/33.012px，E饱和拟合不是标定。最终GLB包含14相机+565mesh的技术回导结果来自制作端独立报告，原无相机geometry-only GLB保留。实际7新增小规模预检渲染；R09b六原尺寸direct50，D/E材质复用R09原路径，22视图继承R08；均不冒充新渲染或新来源。A–F完整来源验收仍FAILED，不计新场景；后续不同日期同场回放仍缺。

503普通原件与完整23原阶段映射见 [files/](files/) 和 [provenance.json](provenance.json)。新增4个真实原commit逐阶段归档，保留R01/R06/R08目录和所有失败证据。大bundle仅运输，普通文件直接Git，不用LFS。

## CURRENT：R09b 未验收

- [CURRENT.json](files/CURRENT.json)
- [models/R09b_material.blend](files/models/R09b_material.blend)
- [models/R09b_white.blend](files/models/R09b_white.blend)
- [models/R09b_material.glb](files/models/R09b_material.glb)
- [models/R09b_white.glb](files/models/R09b_white.glb)
- [docs/R09b-report.zh.md](files/docs/R09b-report.zh.md)
- [qa/R09b-final-independent-review.md](files/qa/R09b-final-independent-review.md)
- [qa/R09b-image-mapping.json](files/qa/R09b-image-mapping.json)
- [qa/R09b-view-coverage.json](files/qa/R09b-view-coverage.json)
- [renders/R08_material/SOURCE_A.png](files/renders/R08_material/SOURCE_A.png)
- [renders/R09b_material/SOURCE_F_fan4k.png](files/renders/R09b_material/SOURCE_F_fan4k.png)
- [comparisons/R09b/white-three-view-proof.jpg](files/comparisons/R09b/white-three-view-proof.jpg)

SOURCE_A主图沿用R08，只是继承入口；本次新图为R09试解D/E/F及R09b材F/白D/E/F。7张均8采样CPU预检，不当精修主视觉。没有新视频采集/深度推理，全部源已见，非盲测。

发布端核原件字节、图片尺寸与报告hash，不重跑Blender、生成脚本、源验收或原像素公式。精确采集缺口沿用旧清单。GitHub浏览器既有证书错误路线未重试，不把解码/API HTML当网页实显。

本映射commit尚不宣称远端回读；后续机器回执记录已执行结果。Issue100及DraftPR101按已授权逐版本更新，main不改、不合并/批准、不改凭据权限，Space留给父任务核验后处理。
