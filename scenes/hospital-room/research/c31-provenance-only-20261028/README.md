# C31 材质模型：2026-10-28 来源文字补全原件归档

本目录保存 C31 材质模型中 26 个对象、78 条来源字符串的补全原件，连同原说明、两份历史验证报告和两张旧开发来源图。原制作日期为 2026-10-28（来自原模型文件名及交接记录）；本次归档使用真实的 2026-10-29 当前提交时间，不回填日期。

它保持 C31 候选身份。原报告记载只从原 WHITE 同名对象复制 `C26_evidence`、`C26_uncertainty`、`C26_reference` 三个字符串属性，没有复制控制参数或驱动，没有改变几何。C31 原有床端板残差、隐藏部分和尺度等未确认项继续保留；C30/C30B 床高方案仍被拒绝。没有新拍摄/导帧、相机标定、渲染、叠图或场景验收。本文件不属于 C32。

## 原件及检查记录

| 原件 | 字节数 | 角色 |
| --- | ---: | --- |
| [MATERIAL 来源文字派生模型](files/hospital_C31_MATERIAL_PROVENANCE_ONLY_20261028.blend) | 13,066,830 | 2026-10-28 BLEND 原件 |
| [原说明 README(7).md](files/README%287%29.md) | 5,207 | 原文未改，历史相对路径说明见下文 |
| [verification.json](files/verification.json) | 146,534 | 历史生产及重开核验报告 |
| [independent_verification.json](files/independent_verification.json) | 1,097 | 历史独立只读重开核验报告 |
| [frame_1107.723.png](files/source_dependencies/frame_1107.723.png) | 1,659,074 | 恢复的旧开发来源 |
| [frame_1116.243.png](files/source_dependencies/frame_1116.243.png) | 1,841,662 | 恢复的旧开发来源 |

六个原件共 16,720,404 字节。精确 Library 身份、版本号、大小、SHA256、Git blob SHA 见 [manifest.json](manifest.json)。Library 修订号不等于场景版本。派生模型 SHA256：

```text
19c54ab8d026da0f9d911b5bf8fb79184c9caba20a913c7ab9fa9f52df72d6d4
```

[本次归档核验](archive_verification.json)核对了六个原件字节；原 MATERIAL、WHITE、C26 清单及另外五个引用文件与基线 Git 文件字节一致。两份原报告中的 26 组对应、78 个字符串、原模型/派生模型哈希、10 类语义状态摘要及对象计数相互一致。两张旧来源图的大小与哈希均与历史独立报告一致，哈希也匹配原 `c26/direction_constraints.json`，PNG 均可解码。

这些是本次字节与报告一致性检查。Blender 4.3.2 的完整语义比较和只读重开结论来自保留的历史报告；本次没有重新执行该 Blender 测试，也没有保存或重导出模型。原验证脚本尚未恢复，因此不能把报告内部一致性称为完整重现验证。旧来源图恢复不增加新的独立相机基线。

## 基线与原 README 的引用映射

本归档基于 C31 档案提交 `f1d07b92942ca4029c9e80611a5f769caaae1654`，对应 [Draft PR #74](https://github.com/Shuang-su/metaxingtong/pull/74)。本次只在新目录增加文件，不改变 `c25-c31-history` 固定历史、原 C31 MATERIAL/WHITE、CURRENT 或其他场景。

原 README 保留原生产工作区的目录叙述。其中“现已恢复”“仅本地 Git 提交”等措辞描述原生产会话，不是此后发布状态。`files/source_dependencies/` 中两张图现已按确切 Library ID 恢复。其余旧相对引用按下表定位，完整字节与路径映射见 [README_reference_map.json](README_reference_map.json)：

| 历史引用 | 本仓库基线位置 |
| --- | --- |
| `c31/hospital_C31_recess_MATERIAL_CONDITIONAL.blend` | [原 MATERIAL](../c25-c31-history/files/c31/hospital_C31_recess_MATERIAL_CONDITIONAL.blend) |
| `c31/hospital_C31_recess_WHITE_CONDITIONAL.blend` | [原 WHITE](../c25-c31-history/files/c31/hospital_C31_recess_WHITE_CONDITIONAL.blend) |
| `c26/candidate_manifest.json` | [C26 原清单](../c25-c31-history/files/c26/candidate_manifest.json) |
| `../c26/direction_constraints.json` | [原方向诊断](../c25-c31-history/files/c26/direction_constraints.json) |
| `../c26/README_C26.md`、`../c26/WHITEBOX_SCOPE.md` | [C26 原说明](../c25-c31-history/files/c26/README_C26.md)、[白模范围](../c25-c31-history/files/c26/WHITEBOX_SCOPE.md) |
| `../inputs/hospital_650.811153_native.png` | [650 原图](../c25-c31-history/files/inputs/hospital_650.811153_native.png) |
| `../inputs/hospital_658.052095_native.png` | [658 原图](../c25-c31-history/files/inputs/hospital_658.052095_native.png) |

已知原母环境曾有提交 `0e4cbe02b7733ced05fbfa4bd6b483f55b98493c`。本次六个历史 bundle 恢复出的原医院 Git 对象库中未找到该提交；只保留已知 hash，不将其写为当前提交父节点，也不声称恢复了它的树、脚本或完整历史。

## 尚未恢复的原件

以下七项由原 README 引用，本批未收到原件：

- `add_architecture_provenance.py`
- `verify_independent.py`
- `source_dependencies.json`
- `initial_correspondence_check.log`
- `initial_correspondence_diagnostic.json`
- `pre_update_correspondence_check.log`
- `recovery_failure_diagnostic.json`

本目录没有伪造或重建这些原件。新写的归档清单与路径映射不替代旧脚本、日志或依赖清单。原 README 的两条 `provenance_20261028/*.py` 命令是历史记录，在缺少原脚本的当前归档布局中不能直接复现。保留这些缺口不影响已取回原件的字节身份；归档完成不等于模型或来源验收。
