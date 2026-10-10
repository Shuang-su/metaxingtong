# 海滨开放场景：原文件入口

阶段2冻结四模型为当前；同名Seafront_Textured与阶段1字节不同，不能按文件名合并。剖切模型仅为QA。

状态：重建候选 / 来源忠实度未验收。Issue #12，PR 保持 Draft。

## 当前模型
- textured_blend: [Seafront_Textured.blend](../../scenes/seaside-scene/02-retain-complete-geometry/files/02_Seafront_Textured_Blender--3731925da52a/models/Seafront_Textured.blend)
- textured_glb: [Seafront_Textured.glb](../../scenes/seaside-scene/02-retain-complete-geometry/files/03_Seafront_Textured_GLB--37a1989c3d46/models/Seafront_Textured.glb)
- white_blend: [Seafront_White.blend](../../scenes/seaside-scene/02-retain-complete-geometry/files/01_Seafront_White_Models--f0c7ccfdfe5d/models/Seafront_White.blend)
- white_glb: [Seafront_White.glb](../../scenes/seaside-scene/02-retain-complete-geometry/files/01_Seafront_White_Models--f0c7ccfdfe5d/models/Seafront_White.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
