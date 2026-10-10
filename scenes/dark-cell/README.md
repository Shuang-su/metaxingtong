# 暗色铁栏布景：原文件入口

只有阶段1首个可核实暗色铁栏候选。双模型四格式为主模型；QA中的回导BLEND和剖切BLEND不能替代主文件。

状态：重建候选 / 来源忠实度未验收。Issue #16，PR 保持 Draft。

## 当前模型
- textured_blend: [dark_cell_textured.blend](../../scenes/dark-cell/01-retain-first-verifiable-release/files/01_暗色铁栏布景_完整模型首版--6654e2fc89de/models/dark_cell_textured.blend)
- textured_glb: [dark_cell_textured.glb](../../scenes/dark-cell/01-retain-first-verifiable-release/files/01_暗色铁栏布景_完整模型首版--6654e2fc89de/models/dark_cell_textured.glb)
- white_blend: [dark_cell_white.blend](../../scenes/dark-cell/01-retain-first-verifiable-release/files/01_暗色铁栏布景_完整模型首版--6654e2fc89de/models/dark_cell_white.blend)
- white_glb: [dark_cell_white.glb](../../scenes/dark-cell/01-retain-first-verifiable-release/files/01_暗色铁栏布景_完整模型首版--6654e2fc89de/models/dark_cell_white.glb)

## 文件组织

- models/CURRENT.json：当前主模型及确切版本
- textures、sources、qa、scripts、docs/CURRENT.json：相应资源原文件路径
- 各真实阶段 files/<原包名--哈希>/：逐字节保留包内原相对布局
- 各阶段 assets 中已有 ZIP 保留为可选历史下载；新阶段优先原文件
- 不执行归档脚本；原脚本可能含旧工作路径，未宣称零配置可重跑

下载整个分支可用标准 Git clone；只需模型可在链接文件页下载原文件。模型内嵌资源已检查，不需要为了使用 GitHub 再打 ZIP。库内主模型和来源图仍有明确残差，文件归档通过不代表来源验收。
