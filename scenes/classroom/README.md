# 教室：原文件入口

主模型仍为阶段4完整房间历史基线。阶段5仅修复独立GLB材质可移植性；阶段6/v0为已被更正的高清QA，阶段7/v1为当前来源分类说明和QA，不更改主BLEND。拒绝位移试验和后续未归档研究不能提升为当前模型。当前同几何白模BLEND/GLB未包含在113原件范围内；阶段1白模仅为不同历史几何。

状态：重建候选 / 来源忠实度未验收。Issue #1，PR 保持 Draft。

## 当前模型
- textured_blend: [fullroom.blend](../../scenes/classroom/04-retain-complete-geometry/files/教室_完整几何房间_审阅--f43e88bbdb3d/fullroom.blend)
- textured_glb: [Classroom_FullRoom_Interior.glb](../../scenes/classroom/05-retain-glb-material-portability-fix/assets/Classroom_FullRoom_Interior.glb)
- white_blend: 当前归档中缺少对应格式，不用旧版/诊断副本代替。
- white_glb: 当前归档中缺少对应格式，不用旧版/诊断副本代替。

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
