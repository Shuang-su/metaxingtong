# 2026-11-02 depth 发布归档

营地旧原生帧上的 CPU 相对逆深度工具验证，以及海港首帧初步分析。官方模型 revision/权重 SHA/配置/脚本/实际原日志保留，99 MB 权重及 venv 不在本批。924×518 为模型网格，1920/3840 显示是派生插值；掩码保留失败与未知，255 置信度掩码表示未知。不是米制测量、几何验收或新场景；海港单张裁切正面尚未达到制作门槛。

## 范围与来源

按普通 Git 原文件保存，入口为 [`files/`](files/)。原独立历史 `history/depth-harbor-original-20261102` 的 tip 为 `f20277101571cb47fb770da039aba47f3b7a5c46`；原提交对象、父链及真实时间不改写。与 main `6ad31e4b2fe8398060c33de20fc09f5edad427a7` 有真实祖先关系的当前归档提交逐阶段映射在 [provenance.json](provenance.json)。

共 31 个普通原件；bundle 仅用于传输，不替代仓库原件。当前归档工作仅接收、字节核验和 Git 发布，没有运行生成/推理脚本、Blender或渲染，也不把原生产日志误称本执行器复验。

## 真实阶段映射

|原独立提交|原保存日期|当前归档提交|
|---|---|---|
|`c7ca89d7cfeb158f373fcaa644675394919e4ae4`|2026-11-02T09:42:29+09:00|`365d8094c18fd8ecb5ef365543b2d2b14d2b1718`|
|`f20277101571cb47fb770da039aba47f3b7a5c46`|2026-11-02T09:47:00+09:00|`925d007684cb1d9ba7c60cfc7d3961acd33232c0`|

## 验证与限制

已执行：Library 大小/SHA256、bundle verify、原历史 fsck、所有文件 blob/SHA、所附制品报告哈希一致性、图片实际解码。尚未在本提交执行：远端空仓逐字节读取（后续专门回执记录）、GitHub 网页图片实显、模型或来源验收。已知 GitHub 浏览器证书错误不绕过；图像解码不当作网页实显。没有删除 Space 副本。

仓库 main 保持原样。PR92 中的最新规范及用户新指令适用于本归档；原文件内旧时点文字保持原字节，不代表当前状态。

营地输入原图的既有固定链接：[1920×1080 原图](https://github.com/Shuang-su/metaxingtong/blob/c5858089c4508b6798566f67d911def53738dcd9/docs/recovery-evidence-20261030/files/recovered-source-candidates/camp/BV169Y96rEo1_P1_1566.095177.png)，SHA256 `947229e1fc963f73b47468f371083fe876f0dcf6458b43f0623fbb7b59c2fc7b`。这是外部已归档依赖，不冒称本深度 bundle 含有该原图。海港原图由单独 Library 输入随本档案落在 `files/sources/`，与两份来源报告的大小/SHA相符；未重新采集或运行深度推理。
