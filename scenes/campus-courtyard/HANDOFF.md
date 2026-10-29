> 当前几何仍为Stage03冻结候选，见 `stage-03-contact-qa/HANDOFF.md`。随后Stage04仅新增相机，完成更早跨BV留出失败诊断，见 `stage-04-cross-bv-holdout/qa/REPORT.md`。下文保留Stage02当时的交接及401回执，不代表最新文件已跨环境交付。

# 校园庭院本地候选交接

分支 `scene/campus-courtyard`。原文件候选 commit `647a9d6c42c4e169aa39803914a5ced0f9496358`。仅本地制作，未 push/PR/Issue/发布；未碰钢琴、main 或 archive/history。

已核验并查看四张原生图及 SOURCE_HANDOFF 原件。候选有 128 组件、材质/同几何白模、GLB 实际回导、四机位直接叠图、八角度检查、逐物体表与失败版本。候选仍未来源验收；实时/预录未知，跨回放同场验证缺失。

## 核心原文件

| 路径 | 字节 | SHA256 | Git blob SHA |
|---|---:|---|---|
| stage-02-material-candidate/campus-courtyard_material.blend | 14575200 | 026888e66d82b41701abea4baa3b12d7602541276da0c68b6687b492877f52a2 | 562bad527d48fd7edd3e819a0af41164393018dd |
| stage-02-material-candidate/campus-courtyard_white.blend | 14575840 | 70eb409014858d6fc3e2488a2b551a82b16a4628e84ad30f8b40e885e5f50909 | 242af06942604cd19d156d324e2826cb42446e2b |
| stage-02-material-candidate/campus-courtyard.glb | 9060952 | e63e1b9e8b6bf69462d6894f0f82f72073f9195564081f6309c1b035d43b6f17 | d50fc0f187de057c8d9e101dcc6113ab06b11900 |
| qa/glb_actual_reimport.blend | 5325567 | 32540d23ead1ddeddcef7ed4ee4bea5e6752fa754d309cd2f30a54d77d12ec35 | d04dd4ea95b26053cc38b18d5c406f140ee3b2e2 |
| stage-02-material-candidate/renders/MAIN.png | 4068544 | 8c9c8efc1fb76b354bd8972f4d2eba2e41c04b1774de56ec2365b2a38dfcbc57 | cd80b5ad1aef8dee08634d936f961438b2528f37 |
| stage-02-material-candidate/renders/MAIN_display_preview.jpg | 463706 | e8d540a2d96412671047dd24f5121c0cd669006e1a36df6b1fb91b4a54d31e92 | 30b9c377bbee4ac25cc9122231793dc051069d74 |

主图 JPEG 是 1920×1080、463,706B（<900KiB）展示预览，未缩放；原 PNG 未改。源/渲染/50% 叠图 PNG 为精确验证入口。

## 核验与已知问题

180 个清单原文件已读取实际本地 Git commit/tree/blob，大小、SHA256 与 Git blob SHA 全部一致。远端未推送，不能声称远端回下载。GLB 128 组件重新导入后顶点位置双向最大差异 0；白模/材质几何一致；两张贴图像素 hash 一致。有限射线、闭合基本体法线及72个踏步位置检查见 qa 原始数据。

来源机位仍条件性：手选拟合点均值约 50–57px，且非独立验证。SRC04 露出有限地面边缘；四长凳最低点约有0.0126模型单位间隙；窗角/台阶局部暗斑、窗列实例与比例、植被、光照材质等待改。不把有限QA全过写成完整几何/来源验收。

## Library 阻塞（失败，非待确认，也非结果未知）

动作：使用当前官方 Library prepared-upload helper 批量创建177个新原文件（381,650,196B）。目标为本场模型、图片、脚本、QA与历史试验。helper 在 hosted apps tools/list 返回 HTTP401，终止于发现工具阶段；无成功新Library ID，未确认任何prepare/transfer/finalize。原5个Library来源仍有效；本地物化成功不代表新模型上传成功。

未重试，未改走单文件接口，未加装软件/凭据或修改安全设置。恢复支持的helper认证后才可重试原批量。完整请求和失败回执已保留于qa/library_upload_request.json与qa/library_batch_receipt.json。不要把本地路径当已完成跨环境交付。
