# 森林蕊束只读研究与春宴来源证据

本包无新模型、无渲染、无恢复历史原件，不能报告新场或源验收成功。森林确定部分长条中心类别但没有唯一FLOWER编号映射，不修改模型。春宴两张公网页面封面仅支持局部观察，native帧数为0，未达到完整多角几何输入门槛。

forest/含只读脚本/实测数据/报告/5个派生裁切。裁切来自既有viewport截图，3倍放大仅帮助观察，不是native视频帧、不新增信息。mapping-projections.json是在停止投影分支指令前完成的反事实计算，仅留执行审计；不是匹配相机残差，不参与身份选择或拟合。

independent-qa/为独立观察与语义审查，按原字节复制。springbanquet/为本轮筛选后的来源包。

## 外部依赖与复验边界
本包不完整自带复验原图及模型。四张实际观察的森林viewport、两份建模脚本及R15材白原件留在本机既有路径，详见external-dependencies.json（绝对路径仅内部档案定位）。这些森林viewport是既有仓库保存的截图字节，不是原生视频帧。四图的既有来源出处为Git commit 2204e912a2929c032223ea011d86f5f81d331af2，引用记录来自forest-diagnostic-replay-20261104/qa/viewport-recovery-manifest.json。外部环境若没有这些文件，不能仅用本包完整重跑视觉/Blender复验，需按其独立归档取得同SHA依赖。当前本机依赖已回读可访问。

## 尺寸勘误
forest/findings.zh.md和independent-qa/review.zh.md原先写源尺寸1212×774有误，实际五张viewport均1212×799；independent-qa/evidence.json为正确实测尺寸。原报告留存不覆盖，现以此勘误为准。裁切坐标和像素本身无变化。弃用投影的内容区假设未校准，不能据其作来源误差。

MANIFEST.json列出所有负载文件相对路径/字节数/SHA256（它本身不递归自哈希）；外部冻结manifest记录真实Git HEAD、全树及bundle的独立SHA。只在新建独立仓库正常提交，不触碰既有生产Git。
