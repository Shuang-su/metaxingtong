# 森林巨树花岛 R01 归档回执

R01 仍是未验收的早期粗白模；悬浮状态与时间变化仍在研究。归档不代表来源/模型/渲染验收。本执行器未建模、未渲染、未执行原生产脚本。

- 固定原件 payload commit：`009a1b5b59f1073df102f230917dffa17076fa80`，本目录是其后追加的归档元数据，不是新制作阶段。
- 原 HEAD：`55b89e69fa461f365913353cf9b7a5f49368d12a`；原 history 分支 `history/forest-flower-island-original-20261104` 保留 6 条真实原提交，作者、时间、父链和全部 59 个原关联对象逐字节一致。
- Library 输入 `libfile_5baf8a59b308819193a60a0fbc3db949` version0，`file_0000000098688230a924e32386469678`，15040738 B，SHA256 `b7b5cae032aea7007711216122103291180ec15bd4ea5f80a8b115ca266caef0`。正式 resolved-reference helper 在本执行器本地接收并验 hash，Library xattr 已核。完整 bundle 无 prerequisite，按明确原分支 checkout；Space 临备保留。
- 普通 Git 归档分支 `archive/forest-flower-island-r01-20261104`：6 条当前阶段映射、1 条 provenance/限制说明；本回执另加 1 条当前 metadata 提交。原件路径不改名，内容不修改；bundle 本体不作为仓库文件。
- 新空 bare 仓经 GitHub 官方 HTTPS 正常 fetch，无本地对象复制或 alternates。30 原文件共 18968941 B，32 payload 文件（含 README/provenance）、全部 6 个阶段与 59 原 commit/tree/blob 对象均实际读字节，大小/SHA256/Git blob 一致，失败 0，Git fsck 返回 0。继承 main 的无关 promisor blobs 不在全量下载断言内；本候选之外树内容不变。
- 最大当前原 blob 3551168 B。无 LFS、强推、main 写入、历史删除、合并或批准 PR、权限/安全设置修改。
- 原制作记录的技术审计未由发布端复跑；两张 960×540 图仅原有低采样白模预检，去噪失败日志保留。原尺寸对照、材质、完整细化、八角、独立 GLB 回导等仍待生产端完成。

完整逐项证据见 [remote_verification.json](remote_verification.json)。本回执与 HANDOFF 提交后会单独 fetch/readback，证据保存在本次执行器交接结果中，避免回执自包含哈希循环。Issue、Draft PR 和 R01 版本评论由本次归档继续建立，均保持未验收状态。
