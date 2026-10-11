# 教室 · 记录GLB颜色响应修复

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 独立GLB颜色响应可移植性修复
V4.1改善共享光影、木墙顶黑板颜色响应、清/磨砂玻璃及窗外三维树楼；完整房间GLB排除窗外环境。随后独立修复GLB遗漏的5项Gamma颜色响应。
原BLEND未修改；原GLB二进制buffer、已有bufferViews、全部几何/UV/法线/索引和节点变换保持；只追加颜色贴图资源并改相应baseColor引用。
修复项目：
- REVIEW lighter albedo - FloorOak：GAMMA响应固化到独立贴图，原alpha不变；旧图SHA256 `99019f44ad759256655f2d5fcbbd4c1e677046dbdc6fded56ac03e89010e3aa2` → 新图SHA256 `3b6f8da0dc92c7cb62a3fd0616bfc5b849938ab1000b901fcdda1363440159c9`。
- REVIEW lighter albedo - Plaster：GAMMA响应固化到独立贴图，原alpha不变；旧图SHA256 `aa513b3c09a2943b78f8247222ec5a58af515ccbb0ef5ea37295c760e1368ce7` → 新图SHA256 `871f7f5351a1b528596bd78bd1b520a300314d5fe4a701ce40e40f22c047448e`。
- REVIEW lighter albedo - Ceiling：GAMMA响应固化到独立贴图，原alpha不变；旧图SHA256 `b5a2faa77c1bc6a61cc0cf027f16831479fc551c6c249408d28ee1a3f7313b3e` → 新图SHA256 `ba1cfcfbbef597082a6324f61149c5989b98be483cf50589c32df405dbeae631`。
- REVIEW lighter albedo - Chalkboard：GAMMA响应固化到独立贴图，原alpha不变；旧图SHA256 `837a8c8adb33d0c485e6145444d931d1fc21554650a60384137a91c487fda2d8` → 新图SHA256 `2564b17a1f32582d860f696c984dedf7f11c1a37d7df693b5760f7c9d86229fc`。
- REVIEW lighter albedo - DeskOak：GAMMA响应固化到独立贴图，原alpha不变；旧图SHA256 `a66569e50256ccd31920b560517d66c5539dc8cebc00b6a15393ffa0213269ac` → 新图SHA256 `ff8c5f1fd702528de066d4508655cdd8e2526e94c233d9d3cdd8fe24a9262630`。
- 旧GLB：10027752字节，SHA256 `d2d1a27feb3c2ab25bb05b8dff54af74a8978a81fc8c560ab879b77040c514f7`。
- 新GLB：13038312字节，SHA256 `86282085695a0a61b2f9301d9b5dd33f6d1918125386d8aad8a029d9b5249b55`。
该修复不是新几何版本，不修复原来源拟合残差。当前文件清单中的独立GLB/GLB压缩包已是修复后交付；BLEND主包仍对应完整几何阶段。

#### 2026-10-10 逐场来源覆盖补充核验
- 新1920×1080解码；1180×757截图、1180×664裁图。
- 登录后采集：未知：未找到可关联该场有效帧的登录状态日志。
- 独立角度：至少正面/窗边/低斜等多个方向；7个模型匹配相机不能直接计作7个独立来源基线。
- 新证据使用：已找到5张高清补采；未找到该批新图进入当前完整房间修改及最终overlay的引用链。旧V4.1多视图用于共享几何拟合。。
- 跨视频后续回放：未证实：已检查记录只有单个BV；同BV更晚时间不等于后续其他回放。
- 原生1080导帧未实现。总体来源验收仍待复核。详见 `scenes/classroom/source-coverage-audit-20261010.json`。

#### 本阶段实际归档路径
- `scenes/classroom/05-retain-glb-material-portability-fix/assets/Classroom_FullRoom_Interior.glb`；13038312字节；SHA256 `86282085695a0a61b2f9301d9b5dd33f6d1918125386d8aad8a029d9b5249b55`；Git blob SHA1 `6a96349aabb01562e94e3a859d7af92cfe948511`。
- `scenes/classroom/05-retain-glb-material-portability-fix/qa/classroom_fullroom_source.png`；189757字节；SHA256 `80f63c67762134baa4f18d3cebb58c980fdc11ebc3cb21ea76da16c901352252`；Git blob SHA1 `aea4ba093d9917b89f9ba691466c215f69925b96`。
- `scenes/classroom/05-retain-glb-material-portability-fix/qa/classroom_fullroom_glb_color_only.png`；186971字节；SHA256 `d9636d9a19497bdc75c607bbfa46b3ec420848fbf9ee0f205c53b410c40c12ba`；Git blob SHA1 `303131a63f36df7f692b01fc679c082262a4323c`。
- `scenes/classroom/05-retain-glb-material-portability-fix/qa/classroom_fullroom_repaired_color_only.png`；189715字节；SHA256 `65de5134ab8ded551a605a84a566661580636369b05f2c3415b1538acc1870be`；Git blob SHA1 `25359451ec56f7d5c0f0fefafbeb81111d52eeb6`。
- `scenes/classroom/05-retain-glb-material-portability-fix/qa/classroom_fullroom_glb_materials.png`；186153字节；SHA256 `6bd453336d86de04e6a0d582a30bfbee0573c96e6aac7f5c754a8e089696d0de`；Git blob SHA1 `c75313a3c6b789f196d89125ceb471c1b776c918`。
- `scenes/classroom/05-retain-glb-material-portability-fix/qa/classroom_fullroom_repaired_all_materials.png`；189158字节；SHA256 `2fdd0c958bb0eeecca1687716ebab7c674005ea7dfeb36ca20ae26ad9306e1a6`；Git blob SHA1 `99d4bc3479e7ff03172755a3e605bf977a613f6f`。
- `scenes/classroom/05-retain-glb-material-portability-fix/qa/material-portability-evidence.json`；7875字节；SHA256 `655c30319e1dcd4e6f236829c49780aae1fc3a797d07b57fa56bcbb698cfb1f0`；Git blob SHA1 `937f4e7313b5813cceb3e9975598925f0c3d0a84`。
- `scenes/classroom/source-scope.json`；2740字节；SHA256 `b8e6b7aca84ff8cc490ad4c9a60cbb6821b008cd06bc77a790741b3a094584a7`；Git blob SHA1 `085b3f6da799784f045b0456e9e7bbdab2194ed6`。
- `scenes/classroom/source-coverage-audit-20261010.json`；2170字节；SHA256 `471677a3736cb355df93918df5a2f0906286dbec54a8313eeb2bd76a2d1bd0f9`；Git blob SHA1 `d856e41dc95d2cc131e62451ef6b7376930aa548`。
- 相同字节复用 `scenes/classroom/05-retain-glb-material-portability-fix/qa/classroom_fullroom_source.png`；SHA256 `80f63c67762134baa4f18d3cebb58c980fdc11ebc3cb21ea76da16c901352252`。

#### 日期语义
- Classroom_FullRoom_Interior.glb：library_item_created_at=2026-10-10T02:40:44.204062Z；library_item_modified_at=2026-10-10T06:06:43.426149Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
