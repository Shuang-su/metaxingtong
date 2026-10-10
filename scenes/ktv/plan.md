# 归档计划

1. 留存最早可核实模型及说明（snapshot）
2. 记录完整有限空间几何升级（snapshot）

原始日期与当前Git提交时间分开；核对冻结包大小/SHA256/ZIP CRC，保持完整原字节。上传后比对Git blob SHA，再逐项读回远端tree。Issue追加真实commit与缺口，Draft PR保持候选状态，不合并。
