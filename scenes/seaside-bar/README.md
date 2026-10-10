# 海边吧台：原文件入口

阶段2冻结完整结构四模型及QA；section_diagnostic_only.blend仅为剖切诊断。

状态：重建候选 / 来源忠实度未验收。Issue #10，PR 保持 Draft。

## 当前模型
- textured_blend: [seaside_bar_complete_textured.blend](../../scenes/seaside-bar/02-retain-complete-geometry/files/03_Seaside_Bar_Textured_Blender--cabbb18d0b4c/models/seaside_bar_complete_textured.blend)
- textured_glb: [seaside_bar_complete_textured.glb](../../scenes/seaside-bar/02-retain-complete-geometry/files/02_Seaside_Bar_Textured_GLB--9caa66d0c70f/models/seaside_bar_complete_textured.glb)
- white_blend: [seaside_bar_complete_white.blend](../../scenes/seaside-bar/02-retain-complete-geometry/files/01_Seaside_Bar_White_Model--895ab4952af6/models/seaside_bar_complete_white.blend)
- white_glb: [seaside_bar_complete_white.glb](../../scenes/seaside-bar/02-retain-complete-geometry/files/01_Seaside_Bar_White_Model--895ab4952af6/models/seaside_bar_complete_white.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
