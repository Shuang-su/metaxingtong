# 城堡花园：原文件入口

阶段3完整几何为当前四模型；阶段2只有开发说明，不存在可恢复模型。Garden_DIAGNOSTIC_CUTAWAY.blend只作QA。包内FINAL_独立核验_通过仅指已声明技术项目，不代表来源精确拟合通过。

状态：重建候选 / 来源忠实度未验收。Issue #11，PR 保持 Draft。

## 当前模型
- textured_blend: [Garden_Complete_Textured.blend](../../scenes/castle-garden/03-retain-complete-geometry/files/03_Garden_Textured_Blender_and_PBR--274507b59c20/models/Garden_Complete_Textured.blend)
- textured_glb: [Garden_Complete_Textured.glb](../../scenes/castle-garden/03-retain-complete-geometry/files/02_Garden_Textured_GLB--441c0a7ce427/models/Garden_Complete_Textured.glb)
- white_blend: [Garden_Complete_White.blend](../../scenes/castle-garden/03-retain-complete-geometry/files/01_Garden_White_Model--b71dbf20c2e5/models/Garden_Complete_White.blend)
- white_glb: [Garden_Complete_White.glb](../../scenes/castle-garden/03-retain-complete-geometry/files/01_Garden_White_Model--b71dbf20c2e5/models/Garden_Complete_White.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。


## 未验收研究记录

[高清v3候选、600保留检查和被否决的v4数值预检](research/20261010-hd-v3-and-rejected-v4/README.md)单独保留。它们未进入CURRENT，也没有替换Library模型。v4没有模型；盆柱布局/机位不匹配尚未唯一归因，旧600错配指标已撤回。
