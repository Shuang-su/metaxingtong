# 列车：原文件入口

阶段3为已归档r03 Library材质/白模/纹理QA版本2，来源审阅包版本0；四种主模型均使用该阶段。阶段2及更旧同名内部模型保留历史，不取本地r04/运动研究。

状态：重建候选 / 来源忠实度未验收。Issue #5，PR 保持 Draft。

## 当前模型
- textured_blend: [01_train_material.blend](../../scenes/train/03-retain-hd-r03-library-v2/files/train_hd_r03_material_models--1fee1fec6de5/01_train_material.blend)
- textured_glb: [03_train_material.glb](../../scenes/train/03-retain-hd-r03-library-v2/files/train_hd_r03_material_models--1fee1fec6de5/03_train_material.glb)
- white_blend: [02_train_white.blend](../../scenes/train/03-retain-hd-r03-library-v2/files/train_hd_r03_white_models--3f9c0f418b77/02_train_white.blend)
- white_glb: [04_train_white.glb](../../scenes/train/03-retain-hd-r03-library-v2/files/train_hd_r03_white_models--3f9c0f418b77/04_train_white.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
