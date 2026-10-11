# 星斯卡舞台：原文件入口

只有阶段1首个可核实候选；材质/白模BLEND和GLB均来自该阶段，三源比对和九视角技术QA并列保留。

状态：重建候选 / 来源忠实度未验收。Issue #13，PR 保持 Draft。

## 当前模型
- textured_blend: [Star_Awards_Candidate.blend](../../scenes/star-awards-stage/01-retain-first-verifiable-release/files/01_材质与白模_Blender--47ddeb7e4a74/Star_Awards_Candidate.blend)
- textured_glb: [Star_Awards_Candidate.glb](../../scenes/star-awards-stage/01-retain-first-verifiable-release/files/02_材质与白模_GLB--dc9b5e6c7f22/Star_Awards_Candidate.glb)
- white_blend: [Star_Awards_White.blend](../../scenes/star-awards-stage/01-retain-first-verifiable-release/files/01_材质与白模_Blender--47ddeb7e4a74/Star_Awards_White.blend)
- white_glb: [Star_Awards_White.glb](../../scenes/star-awards-stage/01-retain-first-verifiable-release/files/02_材质与白模_GLB--dc9b5e6c7f22/Star_Awards_White.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
