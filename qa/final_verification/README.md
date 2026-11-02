# 最终纯验证记录

固定模型冻结HEAD：82694151a2af4f3761325ab34296bd00464322ae。
本新增commit只保存验证记录，不改任何模型、来源、渲染、深度或旧报告。

- all_249_git_object_readback.json：模型冻结HEAD的全部249跟踪文件，从真实Git对象读回并逐字与工作树比较；不是54文件单次变更子集。C05全部172旧路径仍在，缺失0，八个真实历史commits保留。
- C06_six_native_direct50_pixels.json：精确最终6张1920×1080直接叠图（源1/2/已见源3，各材质/白模），使用独立NumPy floor((uint16源RGB+uint16渲染RGB)/2)全像素重新计算。
- all_20_direct50_pixel_verification.json：扩展20张，另含C05六原尺寸图、C05/C06三焦距低清派生诊断及C06两原坐标卷毯裁图；每项标明resize/crop范围。所有通道差0，不作几何或验收证明。
- verify_frozen_delivery_original_audit_script.py：保留实际原审计脚本原文。它最初运行在工作区外部审计目录，按原相对位置执行；归档于此不悄悄改路径伪称同一执行，逻辑与报告来源可查。

原source FAIL、后顶推断、第三机位差距、后续回放缺口不因这些字节/像素回执解除。
