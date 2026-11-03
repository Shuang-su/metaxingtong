# 城市拱窗卧室 R09/R09b 普通Git归档与远端回读交接

R09/R09b仅D/E/F相机条件性改进，R08全部565mesh共享几何、材质灯光及A/B/C与8检查角不变。保留R09初解、F09接触/阴影语义歧义、全圆背面误配及R09c纯计算可见半圈复核。R09b底缘局部改善但同8点F均值/最大由5.371/22.434回归到6.590/33.012px，E饱和拟合不是标定。最终GLB包含14相机+565mesh的技术回导结果来自制作端独立报告，原无相机geometry-only GLB保留。实际7新增小规模预检渲染；R09b六原尺寸direct50，D/E材质复用R09原路径，22视图继承R08；均不冒充新渲染或新来源。A–F完整来源验收仍FAILED，不计新场景；后续不同日期同场回放仍缺。

## 实际完成

- 冻结输入 `libfile_578765c0f3f08191a2b3c54776768bb6` version1，133367970 B，SHA256 `d1d080540604d8222239e111a42bdb74f566e072a26e56053d6b952f8a86ce84`。本执行器通过正式Library helper接收并核字节；先正常fetch R08基线a899c73，再bundle verify/import。仅运输delta，不上传bundle本体/分片/LFS。
- 原history `history/city-window-bedroom-original-20261103` 正常前进至 `0ac33debb6a1a43a4f537a4a7330838abb94fd63`；23条真实原提交（旧19+新4）、645原关联commit/tree/blob、全部作者/时间/父链逐对象保留并远端核验。
- upstream归档分支 `archive/city-window-bedroom-r01-20261103` 从 `5e686bdba2accccefb44de184fcc1dc0ccabc07b` 追加4真实阶段映射及1说明commit。固定payload [7869bd3f219d2b188e74ab4fece3d57c4783737c](https://github.com/Shuang-su/metaxingtong/commit/7869bd3f219d2b188e74ab4fece3d57c4783737c)。本回执再加1真实当前metadata commit，不当新模型阶段。
- 503最终普通原件共721345221 B，历史最大普通blob33177728 B；388旧原件完全字节相同，只有旧README.md修改，114新增路径；旧R01/R06/R08归档600路径完全保留。
- 新空bare仓从GitHub官方HTTPS正常fetch原history，未复制本地对象、没有alternates，再正常fetchupstream分支。505新payload路径（503原件+2说明）逐大小/SHA256/Git blob一致，600旧档案路径也实际再次读字节一致；合计1105 payload路径。全部23阶段逐文件核验、645原对象逐字节核验，fsck通过，失败0。继承main的无关promisor blobs不在全量下载断言范围。
- 本回执/HANDOFF另增2路径，提交后单独正常远端fetch/readback；不在上述1105项内。本批新增507路径，候选目录合计1107路径。机器回执的files/previous_archives_files/stages/original_objects含全部身份与对照。
- 本发布端核171图片可解码、28当前视图映射、6最终叠图输入/渲染/输出hash与尺寸、4模型hash与原独立报告一致；没有建模/渲染/Blender回导/原脚本执行/深度推理或重新计算像素公式。原制作端技术验证不冒称本发布端重跑。

## 固定交付

[503普通原件目录](https://github.com/Shuang-su/metaxingtong/tree/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files) · [完整身份/阶段映射](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/provenance.json) · [机器回执](remote_verification.json)

- [CURRENT.json](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/CURRENT.json)
- [models/R09b_material.blend](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/models/R09b_material.blend)
- [models/R09b_white.blend](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/models/R09b_white.blend)
- [models/R09b_material.glb](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/models/R09b_material.glb)
- [models/R09b_white.glb](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/models/R09b_white.glb)
- [docs/R09b-report.zh.md](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/docs/R09b-report.zh.md)
- [qa/R09b-final-independent-review.md](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/qa/R09b-final-independent-review.md)
- [qa/R09b-image-mapping.json](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/qa/R09b-image-mapping.json)
- [qa/R09b-view-coverage.json](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/qa/R09b-view-coverage.json)
- [renders/R08_material/SOURCE_A.png](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/renders/R08_material/SOURCE_A.png)
- [renders/R09b_material/SOURCE_F_fan4k.png](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/renders/R09b_material/SOURCE_F_fan4k.png)
- [comparisons/R09b/white-three-view-proof.jpg](https://github.com/Shuang-su/metaxingtong/blob/7869bd3f219d2b188e74ab4fece3d57c4783737c/scenes/city-window-bedroom-stage/research/r09-20261103/files/comparisons/R09b/white-three-view-proof.jpg)

## 新原commit与归档映射

|原commit|真实原提交时间|upstream归档commit|
|---|---|---|
|[a82077222b6fd6d36a5ae0af4ac8346bd2280465](https://github.com/Shuang-su/metaxingtong/commit/a82077222b6fd6d36a5ae0af4ac8346bd2280465)|2026-11-03T13:03:43+09:00|[489292224a909a5b7d0ebf4f645266d54119f97b](https://github.com/Shuang-su/metaxingtong/commit/489292224a909a5b7d0ebf4f645266d54119f97b)|
|[a1c63b0afd4640e53b91663a5cb71d4bcef709a8](https://github.com/Shuang-su/metaxingtong/commit/a1c63b0afd4640e53b91663a5cb71d4bcef709a8)|2026-11-03T13:08:06+09:00|[8f6d7908ec63ca61408614666369f6597343db67](https://github.com/Shuang-su/metaxingtong/commit/8f6d7908ec63ca61408614666369f6597343db67)|
|[e728156c49e7251e2eb50b2add9a2ff78671c1a3](https://github.com/Shuang-su/metaxingtong/commit/e728156c49e7251e2eb50b2add9a2ff78671c1a3)|2026-11-03T13:14:25+09:00|[e2ed1e7d7a3123777478cde3af67ebd20399383b](https://github.com/Shuang-su/metaxingtong/commit/e2ed1e7d7a3123777478cde3af67ebd20399383b)|
|[0ac33debb6a1a43a4f537a4a7330838abb94fd63](https://github.com/Shuang-su/metaxingtong/commit/0ac33debb6a1a43a4f537a4a7330838abb94fd63)|2026-11-03T13:23:41+09:00|[331b15bcdb416fe819516c214ed9c27be01d9f9c](https://github.com/Shuang-su/metaxingtong/commit/331b15bcdb416fe819516c214ed9c27be01d9f9c)|

e728156同时保存R09试图与R09b初修，不拆造原commit。最终0ac33de补回独立QA和实际含14相机GLB，保留初始geometry-only导出。R09c仅计算诊断，没有R09c模型/新渲染。

## 持续限制与元数据

- R09b底缘局部姿态改善与F顶部回归同时记录；E六约束/六pose变量的近零误差不证明标定，已见诊断非盲测。全部A–F源形仍FAILED，窗/床/帘/吧台/城景代理/固定反射不合，后续不同日期同场回放缺失；不计新场景、未验收。
- 7实际新增预检图，最终R09b六direct50；D/E材质沿用R09原路径，22视图沿用R08。技术回导/公式为制作端独立报告结果，不把旧图换名称重渲染。
- [Issue100](https://github.com/Shuang-su/metaxingtong/issues/100) / [Draft PR101](https://github.com/Shuang-su/metaxingtong/pull/101)保持同一候选；R09/R09b各首次建版本记录，旧9条保持原文。R09评论6595542402、R09b评论6595544065已首次发布；两条正文及35个API HTML图片位置已读回准确，旧9条原文不变；最终head导航将在回执自身读回后更新。
- main `0ca7ae5be9892e9fc6656142682f7702cf244110` 未改；无强推、LFS、删除历史、合并/批准、认证权限修改。其它此前被拒旧PR不触碰。
- 已知GitHub浏览器证书失败路线未重试/绕过，171图片解码或API HTML不代表网页实显；0CI不称通过。
- Space临备仍保留，交由父任务独立核验后清理。
