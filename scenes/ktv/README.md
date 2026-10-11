# 深月KTV开放舞台：原文件入口

阶段2为有限完整开放舞台；材质与白模BLEND齐备，独立GLB仅保存材质版。不能补建室内外壳或导出新白模来冒充归档原件。

状态：重建候选 / 来源忠实度未验收。Issue #9，PR 保持 Draft。

## 当前模型
- textured_blend: [KTV_Complete_Open_Stage.blend](../../scenes/ktv/02-retain-complete-geometry/files/03_KTV_Textured_Blender--093f481eac64/models/KTV_Complete_Open_Stage.blend)
- white_blend: [KTV_Complete_Open_Stage_White.blend](../../scenes/ktv/02-retain-complete-geometry/files/03_KTV_Textured_Blender--093f481eac64/models/KTV_Complete_Open_Stage_White.blend)
- textured_glb: [KTV_Complete_Open_Stage.glb](../../scenes/ktv/02-retain-complete-geometry/files/02_KTV_Textured_GLB--63e9d67ca063/models/KTV_Complete_Open_Stage.glb)
- white_glb: 当前归档中缺少对应格式，不用旧版/诊断副本代替。

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
