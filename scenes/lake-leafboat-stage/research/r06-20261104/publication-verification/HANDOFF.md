# 湖面巨叶舟 R06 最终冻结普通 Git 归档回执（来源拟合 FAILED）

制作/图证已冻结，不等于来源或用户验收。全部来源拟合仍FAILED，完整底面、逐处接触/全场碰撞及岸林实例未验。27图是26正式套图加1附加低仰；8张直接50%为原尺寸4K，低仰不能证明完整底面或正确浮力。本执行器未建模、渲染、执行原脚本、深度推理或重做独立QA。

## 固定交付入口

- [材质BLEND](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/models/lakeleaf-r06-material.blend) / [白模BLEND](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/models/lakeleaf-r06-white.blend) / [材质GLB](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/models/lakeleaf-r06.glb) / [白模GLB](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/models/lakeleaf-r06-white.glb)
- [最终报告](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/docs/R06-final-evidence.zh.md) / [主图](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/renders/r06/main/HERO.png) / [白模主图](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/renders/r06/white/HERO.png) / [低仰局部诊断](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/renders/r06/diagnostic/DIAG_LOW_09.png)
- [GLB相机sidecar](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/models/lakeleaf-r06-cameras.json) / [配套恢复脚本](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/scripts/restore_glb_cameras_r06.py) / [可移植性说明](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/docs/R06-portability-and-reproduction.zh.md)。raw GLB不保留离轴shift，恢复后投影和raw回导不可混称；AREA灯、世界、色彩管理也不是完全跨引擎等价。
- 四个外部PNG：[lake-colour-hypothesis.png](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/textures/lake-colour-hypothesis.png)、[leaf-tissue-albedo.png](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/textures/leaf-tissue-albedo.png)、[leaf-tissue-roughness.png](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/textures/leaf-tissue-roughness.png)、[water-wave-normal.png](https://github.com/Shuang-su/metaxingtong/blob/d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a/scenes/lake-leafboat-stage/research/r06-20261104/files/textures/water-wave-normal.png)。保留 `textures/` 与 `models/` 相对目录，BLEND纹理未packed。本执行器只保存这些依赖与恢复脚本，不执行它们。

## 输入与精确 basis

Library `libfile_8b90b28fd5c081919e3d9f588a9931b1` version3，`file_00000000e56c81f5b323392538ac5846`，455365802 B，SHA256 `cd343509920dc83276242ce90d9d420e76d4e30e4435524b8a3e15b7af69b5d3`。当前Library resolved-reference helper在本执行器物化并核大小/hash/身份xattr。

应用前先从GitHub官方HTTPS正常fetch原history到新空源仓，实得basis `57a25532b609e65b005930a3d5e0a429562b56d2`；commit正文/对象SHA及tree核验完成。bundle header的唯一prerequisite精确相同，`git bundle verify`通过后才应用单个标准Git累计增量，再明确checkout新HEAD `8a6c541935aad0dbf77559547c8fd316815bc230`。这是原历史Git增量，不是文件切片或模型拆件。输入与basis证据都在provenance和机器回执；Space保留，bundle仅运输。

## 普通 Git 与远端回读

- 固定payload `d0986a2bf3e88e5ee77cde881ebb90106cfe9b3a`。同一history `history/lake-leafboat-original-20261104` 从上述basis正常前进，全部9条原始提交、作者/时间/父链及 473 原commit/tree/blob完整保留。
- 同一归档分支 `archive/lake-leafboat-r01-20261104` 从 `47d041fa89284156e755fc04d7745bd63d421fa9` 追加5条当前原阶段映射、1条provenance说明及本回执metadata；前4映射继承，不伪造旧提交时间。
- 385最终原文件共1962498688 B，最大普通blob88123865 B。相对R04源树142旧路径完全相同、3旧路径修改、240新增、零删除；旧R01和R04两个归档目录共227路径仍原样保留，旧原文/失败不覆盖。
- 新空bare仓从GitHub正常fetch全原history再取归档链，无本地对象复制/alternates。385最终原文件、387新payload路径、227旧档案路径（共614路径）、9原/映射阶段及 473 原对象逐路径大小/SHA256/blob核验；每个唯一对象实际远端读字节比较，失败0，fsck返回0。无关main的promisor blobs不在全量下载断言范围，候选之外以树身份不变核验。
- 两份本回执另增2路径，新R06共389路径，R01+R04+R06共616路径；提交后正常fetch并独立读回两文件，证据另存执行器交接结果，避免自包含hash循环。
- 本执行器另核4模型QA哈希、4外部PNG、13相机sidecar、27渲染文件计数和8组三类图清单SHA/4K尺寸；不冒称复跑Blender、全数组叠图公式或视觉验收。
- GitHub给出10条大于建议50MB的文件提示，实际普通Git push成功，没有LFS、强推、模型拆件、main写入或历史删除。

本轮无Issue/PR/评论创建或重试，不绕过森林此前审批拒绝；无安全修改、PR批准/合并。完整机器证据见 [remote_verification.json](remote_verification.json)。原制作报告中未确认远端的表述原样保留，实际归档状态由本回执另证。
