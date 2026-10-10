# 城堡宴会厅：原文件入口

阶段2 FullRoom替代阶段1可见组件模型；当前原件只含材质BLEND/GLB，不能虚构白模。阶段2包中baseline嵌套ZIP指回阶段1原件，不再复制上传。

状态：重建候选 / 来源忠实度未验收。Issue #3，PR 保持 Draft。

## 当前模型
- textured_blend: [Xingtong_Castle_Hall_FullRoom.blend](../../scenes/castle-hall/02-retain-complete-geometry/files/03_Castle_Hall_Textured_Blender--c8854932dc55/models/Xingtong_Castle_Hall_FullRoom.blend)
- textured_glb: [Xingtong_Castle_Hall_FullRoom.glb](../../scenes/castle-hall/02-retain-complete-geometry/files/02_Castle_Hall_Textured_GLB--978f459d88ee/models/Xingtong_Castle_Hall_FullRoom.glb)
- white_blend: 当前归档中缺少对应格式，不用旧版/诊断副本代替。
- white_glb: 当前归档中缺少对应格式，不用旧版/诊断副本代替。

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
