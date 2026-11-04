# 湖面巨叶舟 R04 中间版普通 Git 归档回执

R04 为未验收中间版。正式 4K 来源机位图、叠图和完整检查角在 version1 冻结时仍制作中，不能把本包预检图当正式成品。本执行器未建模、渲染、推理或执行生产脚本。

- 固定原件 payload commit：`f3e0c05f5acaed6551b95ec8eb43094d7240a99c`；原 HEAD：`57a25532b609e65b005930a3d5e0a429562b56d2`。
- 同一 history 分支 `history/lake-leafboat-original-20261104` 从 `5517af9bcfe64f7a1b8ded54ef26f9ce89114a82` 正常前进至新 HEAD，完整保留全部 4 条真实原提交、作者/时间/父链及 183 个原 commit/tree/blob。
- 同一归档分支 `archive/lake-leafboat-r01-20261104` 从 `41a14de653f1e238adcf4b9434b24e86430ec353` 追加 R02/R03/R04 三条当前阶段映射、1 条 provenance/说明，以及本回执 metadata。旧 R01 映射继承，不重写原历史。
- 旧 R01 目录 `scenes/lake-leafboat-stage/research/r01-20261104` 的全部 78 路径原样保留。新 R04 目录 `scenes/lake-leafboat-stage/research/r04-20261104` 保存 145 原文件共 721585563 B；源树相对 R01 有 72 个完全相同旧文件、仅 `.gitignore`/`README.md` 修改、71 新路径，零删除。旧版本原文仍完整可取。
- 输入 Library `libfile_8b90b28fd5c081919e3d9f588a9931b1` version1，`file_00000000d8d081f59a1d33d197e14038`，209810521 B，SHA256 `05d5301674426642b7a691d873af4f3f878fbf7134fd61f2f9546b190494b3f9`。当前 Library resolved-reference helper 已在本执行器物化并核大小/hash/身份 xattr；完整 bundle 无 prerequisite，明确 checkout `scene/lakeleaf-20261104`。Space 保留，bundle 只作运输。
- 新空 bare 仓从 GitHub 官方 HTTPS 正常 fetch，未复制本地对象、无 alternates。145 当前原文件、147 新 payload 路径、78 旧 R01 路径（合计225 payload 路径）、4 原/映射阶段及全部 183 原对象，均逐路径大小/SHA256/blob 核验；每个唯一对象实际读字节比较，失败0，fsck返回0。其它 main 内容按树身份不变核验，不声称无关 promisor blobs 全量下载。
- 本回执/HANDOFF 另增2路径，最终新增149路径，本候选 R01+R04 共227路径；提交后另行正常 fetch/readback 两回执文件，结果留在本执行器交接证据，避免回执自包含 hash 循环。
- 最大普通 blob 86328621 B；GitHub 对四个超过建议50MB的文件给出提示，正常 push 已成功，没有使用 LFS。两分支仅普通快进，无强推、main 写入、历史删除、批准/合并或安全修改。
- 本轮不创建 Issue、PR、评论，不重试森林此前拒绝动作。制作端 R03/R04 GLB 重导、薄壳审计等报告原样保留，不冒称发布端重跑；这些技术检查不等于来源、场景实例或用户验收。

逐项证据见 [remote_verification.json](remote_verification.json)。相机条件性估计、岸林程序代理、接触/尺度/运动不确定、相对深度失败、同日夜景反证及后续独立日期回放缺口全部保留。
