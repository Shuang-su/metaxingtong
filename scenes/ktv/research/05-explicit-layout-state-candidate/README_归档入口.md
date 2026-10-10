# KTV 显式状态候选：共享资产入口

此目录归档状态配方、脚本、技术核验和32张图。没有新BLEND/GLB或几何版本；CURRENT未更新，来源几何、相机和真实浏览器加载器均未验收。

## 共享模型只引用既有原件

以下固定commit路径已实际读取Git blob并重算SHA256，不能用别的同名文件替代：

- [材质BLEND原件](https://github.com/Shuang-su/metaxingtong/blob/f481dd4a502c19379583b999d97a6bbb6c10e7c6/scenes/ktv/02-retain-complete-geometry/files/03_KTV_Textured_Blender--093f481eac64/models/KTV_Complete_Open_Stage.blend)：5,841,397字节，SHA256 `abf9a4d970e5a7319d64f2c10eb8c3fa822a2bd60c283bfce946ed14ff33cf94`。
- [共享GLB原件](https://github.com/Shuang-su/metaxingtong/blob/f481dd4a502c19379583b999d97a6bbb6c10e7c6/scenes/ktv/02-retain-complete-geometry/files/02_KTV_Textured_GLB--63e9d67ca063/models/KTV_Complete_Open_Stage.glb)：9,480,212字节，SHA256 `de766c72c4d6f99e9aefdfb580e4e5f83ef2d7c5a3f8584795453b92f30ceb1c`。
- [前阶段全部连续来源、115原截图和时间日志](https://github.com/Shuang-su/metaxingtong/tree/f481dd4a502c19379583b999d97a6bbb6c10e7c6/scenes/ktv/research/04-source-state-continuity)。本阶段仅复用其中两张边界图，没有新增采集区间。

## 运行条件与路径

冻结脚本保留原运行目录约定，不会因Git归档自动改写。参考[原说明](README_中文.md)和[状态manifest](layout_state_manifest.json)。本地复跑时，`--workspace` 指定的根目录须按manifest的 `workspace_relative_path` 定位上述精确字节：`ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend` 与同目录 `.glb`。可在自己的复现工作区布置这两个已有文件或相应链接，无须向仓库再提交模型副本。先重算SHA，不要覆盖未核实的同名文件。

手动诊断必须保留选择记录，例如为 `open_candidate.py` 传入 `--log /path/to/state_selection.json`，并保留命令日志。两个边界来源时刻都处于保守unknown包络，图中状态是人工按图选择，不能冒充自动timeline判断。

GLB不带可移植显隐属性。需要使用根 `scripts/layout_state_adapter.mjs` 的已验证绑定入口；先核精确原始bytes SHA、372节点和26目标原名/索引，再把同一字节交给加载器。每次切态重新核对关联；普通查看器不会自动理解本manifest。模拟loader单测和Blender实际回导通过，真实浏览器GLTFLoader仍未验收。

## 当前与历史

- 当前仅26显隐目标：18沙发＋8既有推断家具接触垫；另3望远镜垫不变。7星伙伴、10气球狗为独立动态组，GLB不含原先隐藏的狗网格。
- 根目录16图为最终候选；`historical_18_target_diagnostic/` 的16图及脚本保留最初18目标造成残垫的问题。历史脚本不是当前入口。
- 几何、UV、材质、坐标未改。同态跨18机位统一；36组合是技术检查数，不是来源独立视角数。
- unknown闭区间为 `[6626.597822,6627.396357]`（含两端），未观察时间也unknown，拒绝自动应用。无精确单帧切换结论。
- 固定01_front未对来源标定；渲染1180×664仅按画芯顶部取整放于1180×757画布y27，所有机位/尺度/角色残差保留，不能宣布还原通过。

冻结原件和清单不改；此入口补充实际仓库路径及复现约定。没有上传便利ZIP，没有替换Library、CURRENT或main。
