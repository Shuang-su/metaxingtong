# 病房：原文件入口

阶段2 hospital_complete模型是当前完整房间；同名xingtong_material_models/white_models/textures_and_review压缩包不可与阶段1误合并。当前QA同样选阶段2。

状态：重建候选 / 来源忠实度未验收。Issue #4，PR 保持 Draft。

## 当前模型
- textured_blend: [hospital_complete_materials.blend](../../scenes/hospital-room/02-retain-complete-geometry/files/xingtong_material_models--fa12d5e559de/hospital_complete_materials.blend)
- textured_glb: [hospital_complete_interior.glb](../../scenes/hospital-room/02-retain-complete-geometry/files/xingtong_material_models--fa12d5e559de/hospital_complete_interior.glb)
- white_blend: [hospital_complete_white.blend](../../scenes/hospital-room/02-retain-complete-geometry/files/xingtong_white_models--f807d949bbc1/hospital_complete_white.blend)
- white_glb: [hospital_complete_white.glb](../../scenes/hospital-room/02-retain-complete-geometry/files/xingtong_white_models--f807d949bbc1/hospital_complete_white.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
