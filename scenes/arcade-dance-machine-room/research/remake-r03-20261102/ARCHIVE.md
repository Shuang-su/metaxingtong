# Nov2 第四批 arcade 归档

旧音游厅重新制作，非新scene，原R07–R10未找回。CURRENT R03只M01局部source-lit海报/新UV，未知保持灰、无inpaint；共享1134mesh和R02整场图准确继承，R03只8局部回归。R00/R01/R02失败保留。新高码率三原生帧时间独立，不冒旧帧；camera-only三焦距初始化诊断FAILED、坏pose不晋升CURRENT。来源FAIL、后续独立回放缺。

CURRENT：[原生产/调查报告](files/README.md)。本次收到的196个普通原件在 [files/](files/)，大小/SHA256/Git blob和全部真实阶段映射见 [provenance.json](provenance.json)。

原独立history `history/arcade-remake-original-20261102` tip `0f3ff79c2f7388f148ce9f87810a28d26439b874` 保留全部原始提交对象、父链、作者与真实时间；本归档在真实upstream `6ad31e4b2fe8398060c33de20fc09f5edad427a7` 上按原阶段正常新commit，不把独立根伪接为旧生产后继。既有路径和历史不变。

三个Library冻结输入size/SHA/bundle verify/fsck均已核，657最终普通原件及308图片原字节保持。三个>100MB bundle仅传输，不提交bundle/分片/LFS；当前普通原件最大10,001,620字节。发布执行器不运行输入脚本、Blender、生成、渲染或模型推理；技术/视觉报告来自原制作与独立审阅，非本执行器重跑。

本映射提交尚不宣称远端空仓字节回读；后续真实回执另记。已知GitHub浏览器证书错误路线不重试不绕过，图片解码不是网页实显。main不变、PR保持Draft、不合并/批准、不删Space，母任务完成独立核验后决定临备清理。

|原独立提交|原提交日期|当前归档提交|
|---|---|---|
|`e8b466c9790c442342b1961110d6e36e0c1852f0`|2026-11-02T12:06:32+09:00|`d6c981974a74fab64be6e02d30d91701d66e6003`|
|`a681671fdc78bc268cfd92281f0bace379057dd0`|2026-11-02T12:06:54+09:00|`9bdc5d5c43ce3af6aa752cc1e7ed77614470e020`|
|`180690364f59fb9ddcf40e1e69034fb1f6060a3c`|2026-11-02T12:15:03+09:00|`0ab8ce9af0e4944ba7003c3da36eec086dbc9c31`|
|`9c7a4b61352cb466173952e83889cf84d8ba4314`|2026-11-02T12:16:28+09:00|`c9a14021ed5e656f71f6ab4cf026657daac5c3d1`|
|`588f27afe1008e6f592780ecf317d8aa8d948468`|2026-11-02T12:19:23+09:00|`6d3601200c7499cc390be389929dd22fcedcb713`|
|`4e5a4d1aeef92b0076be1a54d2de0462d78f4659`|2026-11-02T12:29:19+09:00|`76e8c95fd09786b6bd478ed84179b6204f71850e`|
|`ff169f7e070e98a44bf6c971e898d41e4b0c33f7`|2026-11-02T12:36:29+09:00|`56bf014a1ad8460578287ef27adbf681f92f0026`|
|`cabaf79582bf92e5939a4745ec7ba72911be11ff`|2026-11-02T12:42:28+09:00|`8ba263dd8d365d2d13434429cfb89c4a59c3d092`|
|`4103d72a857a02ece928a098d024c46e7d1cebdd`|2026-11-02T12:50:31+09:00|`dfc9e66965cc078757fd881c297de46d301ba8bf`|
|`a614a54611407629874e72bdb3a9d874644e7cfa`|2026-11-02T12:55:22+09:00|`0023b07ed527e7460068b3ff95dcac2c5c7d6d67`|
|`a5596234ba0cd9b41ea2403a8ca741907efacb3b`|2026-11-02T12:58:19+09:00|`01a3d15c31f308014811a8f04013f0cc35fbb46c`|
|`0f3ff79c2f7388f148ce9f87810a28d26439b874`|2026-11-02T13:00:38+09:00|`f6503d871a908ec68f0aa28fd7836c8198028d60`|

## 当前模型与继承入口

- [models/arcade_remake_R03_material.blend](files/models/arcade_remake_R03_material.blend)。
- [models/arcade_remake_R03_white.blend](files/models/arcade_remake_R03_white.blend)。
- [models/arcade_remake_R03_material.glb](files/models/arcade_remake_R03_material.glb)。
- [models/arcade_remake_R03_white.glb](files/models/arcade_remake_R03_white.glb)。
- [qa/R03/R03_RENDER_REVIEW.md](files/qa/R03/R03_RENDER_REVIEW.md)。
- [qa/R02_FINAL_REVIEW.md](files/qa/R02_FINAL_REVIEW.md)。
- [qa/camera-new-source/RESULT.md](files/qa/camera-new-source/RESULT.md)。
