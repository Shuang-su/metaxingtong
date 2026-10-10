# 开放露台：原文件入口

主BLEND选阶段4 V16 CompleteSpace，独立GLB选阶段5修复材质导出。两者范围与资源近似见原说明；WithoutCity GLB不应冒称与含全部上下文的主BLEND逐对象完全一致。V15为前一历史检查点，不是当前主模型。范围内未保存当前白模。

状态：重建候选 / 来源忠实度未验收。Issue #2，PR 保持 Draft。

## 当前模型
- textured_blend: [Green_Terrace_Working_V16_CompleteSpace_REVIEW.blend](../../scenes/terrace/04-retain-complete-geometry/files/Green_Terrace_V2_REVIEW_ONLY--9f53dd8fe6b0/Green_Terrace_Working_V16_CompleteSpace_REVIEW.blend)
- textured_glb: [Terrace_CompleteSpace_WithoutCity.glb](../../scenes/terrace/05-retain-glb-material-portability-fix/files/Terrace_CompleteSpace_GLB_LZMA需兼容解压器--d2e5b9128a38/Terrace_CompleteSpace_WithoutCity.glb)
- white_blend: 当前归档中缺少对应格式，不用旧版/诊断副本代替。
- white_glb: 当前归档中缺少对应格式，不用旧版/诊断副本代替。

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
