# 原文件下载与目录说明

GitHub 中优先保存可直接使用的模型、贴图、脚本、来源图片和QA文件。历史ZIP作为可选下载保留，新交付不必为了GitHub重新压缩。

每场景的 README 为入口，models/CURRENT.json 列出准确当前模型，textures、sources、qa、scripts、docs/CURRENT.json 分别列出真实原文件路径和哈希。CURRENT 仅为索引；模型本体就在对应阶段的 files/<原包名--SHA前12位>/<包内原路径>，可直接下载。

## 下载

访问场景入口中的模型链接，在文件页面下载原文件；完整资料使用标准 Git 克隆相应归档分支。例如：

```
git clone --single-branch --branch archive/classroom-history https://github.com/Shuang-su/metaxingtong.git
```

仓库保持私有，需以有权限的GitHub账户登录。未配置GitHub Pages或其他公开下载服务。每个场景都在自己的Draft PR分支中；main保存总索引，未将场景PR合并。

保留包命名目录内相对结构，不要把同名资源盲目移到一个目录。三组已查实的同路径不同内容通过原包命名空间隔离；同字节Git对象自然复用。31件早前已独立存在的普通原文件直接复用原路径，没有再复制当前模型树。嵌套ZIP、Library打包辅助脚本、运行日志没有重复展开。

## 大文件与大小口径

最大单个原文件34,076,844字节（约32.50MiB），低于GitHub普通Git的50MiB提醒与100MiB单文件阻止线。本次无需Git LFS，没有创建LFS计费或新存储权限。各场景分次push。历史原件不删除，不为减体积改写Git历史。

本轮展开2,468个普通原文件成员，总路径字节1,281,184,282；Git按内容对象去重，因此这个数字不是实际网络流量或仓库磁盘大小。模型及资料来自旧82个冻结ZIP和新增卧室5个已交付Library ZIP；5项排除有记录。旧113件/82ZIP/38阶段的独立核验记录仍保留。本轮加卧室HD v2后为39个真实阶段，35个新迁移commit；仅证据且无模型原件的阶段继续保留原记录，不虚造空模型。

Library附件仍使用小于18MB的分包交付；这是独立下载限制，不限制GitHub中的普通原文件。

## 模型依赖与使用边界

57个当前主模型已明确选定：29个BLEND仅只读打开检查依赖，28个GLB解析资源URI。未发现使用中的未打包外部图像、外链library、外部字体或GLB外部图像/缓冲URI；本轮未改模型字节。7个缺失的当前格式明确空缺，不能用旧版白模、剖切或回导诊断副本冒充当前主模型。

所有场景仍是重建候选，来源忠实度未验收。依赖自包含、几何完整和传输哈希通过不代表源视频精确重建。新卧室HD v2仍为同轴参考族，clip14仅用于来源诊断；普通主视角使用完整围护。教室D为叙事静态背景待关联，旧20桌六列不是已验证拓扑。

归档脚本保留为历史项目源代码，没有执行它们；可能含旧工作路径或前版输入，不宣称可直接零配置重跑。

官方说明：[GitHub大文件](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[仓库限制](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)。
