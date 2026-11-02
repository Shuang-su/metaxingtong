# 2026-10-30 有限恢复材料：普通 Git 原件归档

本目录逐字节保存已收到的恢复快照：98 个文件，共 44,041,749 字节。包含四场景16张原生来源PNG（39,843,694字节）、3张历史派生图、有限源码候选、幸存检查脚本/日志及缺失说明。没有 BLEND/GLB/GLTF 模型；不包含 F07、M03 或其最新历史，不代表今天完成新模型或通过来源验收。

原独立根提交为 [`27bece9ae7149aa0026b95c977ef4f159909dcf9`](https://github.com/Shuang-su/metaxingtong/commit/27bece9ae7149aa0026b95c977ef4f159909dcf9)，真实作者/提交时间为 2026-10-31T05:39:54+09:00，即2026-10-30T20:39:54Z。原对象与空父链在 `history/recovery-original-20261030` 保留。本目录则在真实 upstream 分支正常提交，使用当前归档时间，不把独立根伪接为旧模型历史。

## 原件入口与来源映射

| 场景 | 来源图 | 有限恢复材料 | 既有 Issue |
| --- | --- | --- | --- |
| 街机跳舞机房间 | [5张原生图](files/recovered-source-candidates/arcade/) | [范围/缺失说明](files/reconstruction-recovery/arcade/RECOVERY_STATUS.md) | [#85](https://github.com/Shuang-su/metaxingtong/issues/85) |
| 红色摩天轮吊舱 | [5张原生图](files/recovered-source-candidates/ferris/) | [范围/缺失说明](files/reconstruction-recovery/ferris/README.md) | [#86](https://github.com/Shuang-su/metaxingtong/issues/86) |
| 沙漠营地 | [3张原生图](files/recovered-source-candidates/camp/) | [范围/缺失说明](files/reconstruction-recovery/camp/RECOVERY_STATUS.md) | [#87](https://github.com/Shuang-su/metaxingtong/issues/87) |
| 灯笼花瓣圆台 | [3张原生图](files/recovered-source-candidates/lantern/) | [范围/缺失说明](files/reconstruction-recovery/lantern/RECOVERY-REVIEW.md) | [#88](https://github.com/Shuang-su/metaxingtong/issues/88) |

[完整98文件清单](archive-manifest.json)记录逐文件路径、大小、SHA256、原Git blob、角色和场景映射。[来源路径映射](source-path-map.json)将原清单中的历史绝对路径映射到本目录；历史机器路径不代表当前仍存在。原相对目录结构保留在 `files/` 内，没有改写原代码路径或执行候选脚本。

原快照[README](files/README.md)、[97项清单](files/recovery-file-manifest.json)和[16张来源索引](files/recovered-source-candidates/RECOVERY_INDEX.json)保持原字节。原清单按设计排除自身，本次清单覆盖全部98项。历史文字中“未push”“模型不进Space”等描述保留其当时含义；当前发布与规则变化单独记录，不倒改原证据。

16张原生来源均1920×1080并可解码。营地另有两张1300×760参考裁切和一张1280×520的历史R06检查拼图，属于派生资料，不是新原生采源或本次渲染。图片解码、字节一致性不等于GitHub评论逐位置实显。

## 核验与剩余缺失

接收bundle大小、SHA256、完整历史声明、指定tip及 `git fsck --full` 均通过；原清单97项全部匹配，98文件与原提交读取字节一致。本批最大原件3,523,898字节，使用普通Git，不使用LFS。bundle仅用于传输恢复，不以bundle链接替代普通原文件。最终远端逐文件读回结果及Draft PR在既有Issue的恢复记录原位补充。

部分源码是幸存普通文件，部分是此前可见工具文本的转录候选；各自来源以原manifest为准。当前候选hash只证明这次快照，不能证明与已丢失旧脚本相同，更不能证明缺失模型可以完整重现。本次没有建模、改模、渲染、执行恢复脚本或深度估计。

四场旧模型、完整依赖与制作Git对象仍有缺口；F07、M03、后续重制模型及最新bundle不在本输入内，相关存续更正继续适用。归档成功不改变未验收状态，不合并PR，不修改CURRENT或main。Space副本由负责人在完整远端核验后处理，本次不删除。
