# 卧室（7.7深最终版）：原文件入口

最新授权扩展为已交付Library的HD候选v2，新阶段3待Git原文件归档；其四模型来自已保存的新包。阶段2冻结7.7模型保留完整历史。clip_start=14的外置DIAG机位只作来源诊断，普通normal_main_hd使用完整房间与clip=0.03；三张高清源属同轴族、独立平移基线为0，来源拟合未通过。legacy_v1_cutaway只作历史剖切诊断。

状态：重建候选 / 来源忠实度未验收。Issue #8，PR 保持 Draft。

## 当前模型
- textured_blend: [01_HD_candidate_material.blend](../../scenes/bedroom/03-retain-hd-candidate-library-v2/files/01_Bedroom_Material_Models--7eff91d5c1a6/models/01_HD_candidate_material.blend)
- textured_glb: [03_HD_candidate_material.glb](../../scenes/bedroom/03-retain-hd-candidate-library-v2/files/01_Bedroom_Material_Models--7eff91d5c1a6/models/03_HD_candidate_material.glb)
- white_blend: [02_HD_candidate_white.blend](../../scenes/bedroom/03-retain-hd-candidate-library-v2/files/02_Bedroom_White_Models--adf43b2b4c28/models/02_HD_candidate_white.blend)
- white_glb: [04_HD_candidate_white.glb](../../scenes/bedroom/03-retain-hd-candidate-library-v2/files/02_Bedroom_White_Models--adf43b2b4c28/models/04_HD_candidate_white.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
