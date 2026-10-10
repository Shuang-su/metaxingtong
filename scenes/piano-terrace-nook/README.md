# 钢琴门廊：原文件入口

只有阶段1首个可核实近似候选；双模型四格式、真实源和QA分包配套。此钢琴门廊不是独立季节露台。

状态：重建候选 / 来源忠实度未验收。Issue #14，PR 保持 Draft。

## 当前模型
- textured_blend: [Piano_Nook_Textured.blend](../../scenes/piano-terrace-nook/01-retain-first-verifiable-release/files/钢琴门廊_01_完整模型_近似候选--7a9ae9c06ca4/models/Piano_Nook_Textured.blend)
- textured_glb: [Piano_Nook_Textured.glb](../../scenes/piano-terrace-nook/01-retain-first-verifiable-release/files/钢琴门廊_01_完整模型_近似候选--7a9ae9c06ca4/models/Piano_Nook_Textured.glb)
- white_blend: [Piano_Nook_White.blend](../../scenes/piano-terrace-nook/01-retain-first-verifiable-release/files/钢琴门廊_01_完整模型_近似候选--7a9ae9c06ca4/models/Piano_Nook_White.blend)
- white_glb: [Piano_Nook_White.glb](../../scenes/piano-terrace-nook/01-retain-first-verifiable-release/files/钢琴门廊_01_完整模型_近似候选--7a9ae9c06ca4/models/Piano_Nook_White.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
