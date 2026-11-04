# 湖面巨叶舟 R06 最终冻结普通 Git 归档（来源拟合全部 FAILED）

本目录保存385原文件，共1962498688 B。R06制作与图证已冻结，但全部来源拟合仍FAILED，完整底面及全场接触/碰撞仍未验，不能写成来源或用户验收通过。

入口：[最终报告](files/docs/R06-final-evidence.zh.md)、[材质BLEND](files/models/lakeleaf-r06-material.blend)、[白模BLEND](files/models/lakeleaf-r06-white.blend)、[材质GLB](files/models/lakeleaf-r06.glb)、[白模GLB](files/models/lakeleaf-r06-white.glb)、[主图](files/renders/r06/main/HERO.png)。[GLB相机sidecar](files/models/lakeleaf-r06-cameras.json)、[恢复脚本](files/scripts/restore_glb_cameras_r06.py)与四张外部PNG均完整保留；打开BLEND须保持同级 `textures/` 相对目录，纹理未packed。raw GLB不保存离轴shift，不冒称它单独保留俯视投影、AREA灯、世界或色彩管理；详[可移植性说明](files/docs/R06-portability-and-reproduction.zh.md)。本归档端没有执行恢复脚本。

套图为26正式套图加1附加低仰，共27渲染；另有8张真正3840×2160直接50%叠图。独立QA原文保留。归档端核4模型哈希、4外部PNG、13相机sidecar及8组来源/渲染/叠图清单哈希和尺寸，未复跑全数组公式、Blender或视觉核验。低仰只诊断部分暗底/局部水线，不能冒称完整底面、精确接触或正确浮力。

输入为Library `libfile_8b90b28fd5c081919e3d9f588a9931b1` version3、455365802 B，SHA256 `cd343509920dc83276242ce90d9d420e76d4e30e4435524b8a3e15b7af69b5d3`。本执行器先从GitHub正常fetch原history到空源仓，确认精确basis `57a25532b609e65b005930a3d5e0a429562b56d2`；当前Library helper本地物化并核hash/大小/身份。bundle header唯一prerequisite就是该basis，`git bundle verify`通过后才应用单个真实Git累计增量，再明确checkout `8a6c541935aad0dbf77559547c8fd316815bc230`。这不是文件切片，合并后的原历史完整。Space保留。

同一原history `history/lake-leafboat-original-20261104` 从basis正常前进到新HEAD，保留全部9条真实原提交。归档分支 `archive/lake-leafboat-r01-20261104` 从 `47d041fa89284156e755fc04d7745bd63d421fa9` 追加5条当前阶段映射和本说明，原4条映射继承。旧R01/R04两个目录共227路径原样保留；新R06独立目录不覆盖旧原件/回执。原提交作者、时间、父链全部保留，当前映射不是伪造的旧制作时间。

相对R04源树：142旧路径字节相同，3旧路径修改，240新增，0删除。旧版本字节仍由旧目录和真实原历史保存。逐文件SHA256/Git blob、全阶段映射、依赖和输入basis证据见 `provenance.json`。

本轮只普通Git提交/推送及新空仓回读，无建模、渲染、生产脚本执行、LFS、强推、main写入、历史删除或安全修改。不创建任何Issue/PR/评论，不重试森林此前拒绝，不换工具绕路。远端机器回执随后追加到 `publication-verification/`，是归档元数据而非新模型版本；原制作报告的“未证远端”文字保留，归档结果由回执另证。
