# R00 来源接收和范围冻结

执行日期：2026-10-30 UTC；Git 使用真实系统时间。当前执行器仓库起点6ad31e4。未找到 /AGENTS.md、/workspace/AGENTS.md、仓库AGENTS.md或 .agents/skills；读取 docs/reconstruction-standard.md 全文。

现有目录16场：bedroom, castle-garden, castle-hall, classroom, dance-studio, dark-cell, hospital-room, kitchen, ktv, piano-terrace-nook, red-gold-stage, seaside-bar, seaside-scene, star-awards-stage, terrace, train。另按母线程历史排除昨日piano-seaside-exterior、校园庭院、副驾局部；它们未出现在本地基线，不声称已检查其模型字节。

采用新slug interview-whiteboard-room。对照旧classroom README与来源说明：旧场景有固定绿黑板、学生桌阵列、书架、电视与钟；本场为独立黑框白板+单桌+黑椅的灰墙角。

通过当前Library受支持的prepare_materialize与捆绑transfer helper下载3件原文件。两个原生PNG在当前执行器被实际打开；尺寸1920×1080、字节与提供SHA256均一致，详见验收脚本产物。没有沿用其他执行器路径，没有下载认证失败，没有绕过任何权限。

Library来源身份：
- 正面 libfile_fd2663386490819181f9247de78c5f82
- 斜视 libfile_dc8e2d5a5c208191a6e3f5d266be511d
- manifest libfile_c60673020784819194f31788abfafe70

母线程补查：全片UI时长1:46:35；1207.002918为办公隔间，1267.020811为棕沙发标语区，1596.141986为人物遮挡的同斜机位，未保存重复图。这里仅记录报告，不冒称本人看完整回放或跨回放查证。区域连通关系未知。

高清链限制：manifest记录1080P高清、paused=true、readyState=4以及前后相同currentTime与尺寸。未提供登录态截图和最高画质菜单的原始记录，故接收者独立能证实字节与像素，不能单凭manifest补称已独立核验最高可用画质。来源为原生解码帧，不证明上游渲染原生分辨率。

缺少：白板底脚无遮挡侧/背视，椅背与后腿，门/天花/前墙，真实尺度，跨回放同场新基线。有限闭壳全部标inferred；来源验收保持失败/待核。
