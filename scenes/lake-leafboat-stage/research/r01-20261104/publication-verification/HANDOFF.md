# 湖面巨叶舟 R01 普通 Git 归档回执

R01 是首个可编辑冻结候选，早期未验收。真实 4K 来源与相关旧场排重结论来自制作端记录；归档执行器仅核四张 PNG 的 3840×2160 尺寸与采集清单 SHA256，不冒称独立视频解码或全历史排重。源机位、几何、接触、尺度和运动等仍有未证项。

- 固定原件 payload commit：`9bc53f4750272e997c3a3ed8e1b36a3b2f740a81`。原 HEAD：`5517af9bcfe64f7a1b8ded54ef26f9ce89114a82`。
- 原分支 `history/lake-leafboat-original-20261104` 保留全部 1 条真实原始提交及 84 个原 commit/tree/blob 对象，作者、时间、父链和对象逐字节一致。不拆造多阶段。
- 归档分支 `archive/lake-leafboat-r01-20261104` 从 main `0ca7ae5be9892e9fc6656142682f7702cf244110` 新增本候选目录，1 条当前阶段映射 + 1 条 provenance/限制说明；本回执再追加 1 条当前归档 metadata 提交，不当新制作版本。
- 输入 Library `libfile_8b90b28fd5c081919e3d9f588a9931b1` version0，`file_0000000081d081f5990f6f1c1d0e175f`，145354083 B，SHA256 `54cc4f29bb464bb0a53750c78193807f0c39a23d92029734affc3843c4407264`。当前 resolved-reference helper 在本执行器本地物化；字节、hash、Library xattr 已核。全量 bundle 无 prerequisite，明确 checkout `scene/lakeleaf-20261104`。
- 新空 bare 仓通过 GitHub 官方 HTTPS 正常 fetch 原 history，再 fetch 归档分支；没有本地对象复制或 alternates。74 原文件共 217538461 B；76 payload 路径、全部原/映射阶段与 84 原对象均实际读回字节，大小/SHA256/Git blob 全部一致，失败 0，Git fsck 返回 0。旧 main 的无关 promisor blobs 不在全量下载断言范围，本候选目录之外按树身份核不变。
- 最大普通原 blob 为 33177728 B。74 原件路径及内容完整保留；另有 README/provenance，回执/HANDOFF 再新增 2 路径，最终 78 路径。bundle 只作运输，不上传为仓库 payload。
- 未建模、渲染、执行原脚本或深度推理；未创建 Issue/PR/评论，未重试森林被拒动作。没有 LFS、强推、main 写入、历史删除、合并/批准或安全配置修改。Space 输入保留。

完整逐项证据见 [remote_verification.json](remote_verification.json)。本回执及 HANDOFF 提交后会另行正常 fetch/readback，结果保存在本执行器交接证据，避免自包含 hash 循环。

保留的制作限制：源机位仍初估，岸后结构和植物实例不穷尽，舟厚/曲率/水面接触及真实尺度不具测量真值；相对深度存在水面伪坡度、俯视压平、遮挡融合和未知置信度，重采样不当原生 4K 深度。渲染/叠图/八检查角、GLB AREA light 差异及独立回导仍待制作端处理；角色、鸟、水面/反射、舟漂移和夜景变化不当静态几何事实。归档通过不等于模型/来源/用户验收。
