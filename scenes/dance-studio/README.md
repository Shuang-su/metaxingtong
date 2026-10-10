# 霓虹舞房：原文件入口

阶段2 FullRoom材质/白模四模型是当前成套几何，阶段1同名总包仅历史；当前QA为完整房间审阅。

状态：重建候选 / 来源忠实度未验收。Issue #6，PR 保持 Draft。

## 当前模型
- textured_blend: [Xingtong_Neon_Stage_FullRoom.blend](../../scenes/dance-studio/02-retain-complete-geometry/files/Xingtong_Dance_Studio_Neon_3D--b181ad02d89d/Xingtong_Neon_Stage_FullRoom.blend)
- textured_glb: [Xingtong_Neon_Stage_FullRoom.glb](../../scenes/dance-studio/02-retain-complete-geometry/files/Xingtong_Dance_Studio_Neon_3D--b181ad02d89d/Xingtong_Neon_Stage_FullRoom.glb)
- white_blend: [Xingtong_Neon_Stage_FullRoom_White.blend](../../scenes/dance-studio/02-retain-complete-geometry/files/Xingtong_Dance_Studio_Neon_3D--b181ad02d89d/Xingtong_Neon_Stage_FullRoom_White.blend)
- white_glb: [Xingtong_Neon_Stage_FullRoom_White.glb](../../scenes/dance-studio/02-retain-complete-geometry/files/Xingtong_Dance_Studio_Neon_3D--b181ad02d89d/Xingtong_Neon_Stage_FullRoom_White.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
