# 2026-10-30 面试白板房 R05 本地交付

**本地候选交付已完成；来源还原未验收、用户未接受。** 独立场景`interview-whiteboard-room`，没有并入棕沙发招聘区、办公隔间、摄影区或旧教室。

模型阶段真实提交：`b650e78837744b53fcb792ae19f57470bdcf5e94`；最终QA/文件索引另作真实当前提交。所有本轮修改只在`scene/interview-whiteboard-room`分支的新场景目录，不修改旧场景、main，也没有外部发布。

## 原件入口

| 用途 | 文件 | 大小 |
|---|---|---:|
| 可编辑材质模型 | [BLEND](../models/r05/interview-room-material.blend) | 1,557,148 B |
| 同几何白模 | [BLEND](../models/r05/interview-room-white.blend) | 1,342,028 B |
| 材质跨软件导出 | [GLB](../models/r05/interview-room-material.glb) | 979,844 B |
| 白模跨软件导出 | [GLB](../models/r05/interview-room-white.glb) | 581,504 B |
| 正常主图 | [JPEG](../qa/r05/main.jpg) / [原尺寸PNG](../qa/r05/main.png) | JPEG 470,154 B |
| 两源同机位联系图 | [JPEG](../qa/r05/source-contact.jpg) | 232,700 B |
| 九角度内部检查联系图 | [JPEG](../qa/r05/inspection-contact.jpg) | 388,874 B |

三张展示JPEG均小于900KiB。原源PNG、模型、GLB、贴图、脚本、单独检查PNG、1920×1080渲染/直接50%叠图、局部裁切和失败记录全部按普通原文件保留；没有新ZIP。每项大小、SHA256与Git blob SHA在[file-index.json](../file-index.json)。

## 已实际验证

- 两张源PNG均在本执行器下载、实际打开，IHDR/解码均1920×1080，字节数和所给SHA256一致。捕获播放器时刻为1283.813032和1505.632497，不混用1283.248预览时刻。
- 61个网格物件，每个都有稳定ID与证据标记；除了有意的板面贴图平面，实体网格无边界/非流形边、无零面积面且有正体积。
- 完整有限内壳从3个点发出共6,144条射线，无漏射；所有11台源/检查相机在壳内。未知天花/前闭墙/墙厚明确推断，不添加没有依据的门窗。
- 12个支撑脚垫与地面在1e-6模型单位阈值内接触；列出的桌侧、板后和椅垫净空为正。桌、椅、白板跨物件表面三角相交为零，组内设计连接保留。非穷举所有构造/包含关系证明。
- 材质和白模GLB都实际重新导入Blender并另存。两者均10,742三角形，材质/白模世界三角坐标逐物件一致；相对原评估网格的包围盒最大偏差5.960464477539063e-08单位。两种GLB不是仅检查文件头。
- 13张正式渲染（2材质来源机位、9内部角度、2白模来源机位）全部真实生成并按记录尺寸解码；两张50%叠图逐像素等于源图与完整渲染直接混合，未warp。主图PNG与正面渲染原字节一致。
- 两张最终材质源机位、两白模、九检查原图及联系图都实际看像素；详细结果与最严重三项残差见[visual-review.md](visual-review.md)。

机器记录：[geometry-validation](../qa/r05/geometry-validation.json)、[furniture-intersections](../qa/r05/furniture-intersections.json)、[delivery-validation](../qa/r05/delivery-validation.json)、[source-byte-verification](../qa/r05/source-byte-verification.json)。

## 未通过项与阻塞

最严重三项：近景桌面侵入原图可见空地；正面桌腿落地点/截断比例不符；白板下投影与照明不符。白模预览偏亮/高光截断也已记录，不以其亮部替代几何检查。

只收到同一回放两张有效源，缺少同时间连续宽景来确认桌椅状态、底脚/背面、门顶/未知闭合端、真实尺度及后续回放同场基线；账号最高可用画质的原始界面证据未随文件传入。上述证据不足使来源验收保持未通过。

没有当前本地制作技术阻塞。**向Shuang-su/metaxingtong push、创建/更新Issue、Draft PR、评论及合并均未尝试**，因为本轮明确限于本地制作，外部发布授权仍在母线程待确认；没有把本地建模授权扩大成发布授权，没有自动审批拒绝或未知发布结果。
