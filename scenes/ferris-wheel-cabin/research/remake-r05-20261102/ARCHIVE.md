# Nov2 第四批 ferris 归档

旧摩天轮舱真实重制，非原R08b找回、非新scene。CURRENT R04几何+R05仅front条件相机，其他3source/MAIN/10CHECK准确继承R04。R01漏洞、R02/R03绕序/装配错误及exit130失败保留；R04有限支脚顶/灯座推断连接修复。176mesh技术/有限射线不证明数学水密，.001亚网格圆角等未测。R05只门平面训练，留出窗174–193px仍FAIL，前门遮挡及其余来源未通过；灰外景未做。

CURRENT：[原生产/调查报告](files/scenes/ferris-wheel-cabin-remake/docs/remake-report.md)。本次收到的207个普通原件在 [files/](files/)，大小/SHA256/Git blob和全部真实阶段映射见 [provenance.json](provenance.json)。

原独立history `history/ferris-remake-original-20261102` tip `9d779065e7b3f56fc0228e4d26f16a29564aeee1` 保留全部原始提交对象、父链、作者与真实时间；本归档在真实upstream `6ad31e4b2fe8398060c33de20fc09f5edad427a7` 上按原阶段正常新commit，不把独立根伪接为旧生产后继。既有路径和历史不变。

三个Library冻结输入size/SHA/bundle verify/fsck均已核，657最终普通原件及308图片原字节保持。三个>100MB bundle仅传输，不提交bundle/分片/LFS；当前普通原件最大10,001,620字节。发布执行器不运行输入脚本、Blender、生成、渲染或模型推理；技术/视觉报告来自原制作与独立审阅，非本执行器重跑。

本映射提交尚不宣称远端空仓字节回读；后续真实回执另记。已知GitHub浏览器证书错误路线不重试不绕过，图片解码不是网页实显。main不变、PR保持Draft、不合并/批准、不删Space，母任务完成独立核验后决定临备清理。

|原独立提交|原提交日期|当前归档提交|
|---|---|---|
|`ab44cbed30fb6eb19b85fb5eb54353fd30d96941`|2026-11-02T12:03:18+09:00|`a552be386031deff9dd4a6bc2e51be45f8ce268a`|
|`2f053bb0770f3708e364981cf137c0c69e78fe6f`|2026-11-02T12:05:02+09:00|`d4db22801cb2352cdc0f31fbcb088b3d135b0331`|
|`92457bc3a3fd0799d880b2319baffcbddc6b1835`|2026-11-02T12:08:08+09:00|`bb5b480d6979972f475b01a05f6d637d805f7e57`|
|`77b0a1c1100ce85f2a311a023592490d453fca3a`|2026-11-02T12:19:41+09:00|`977a4c872bcabfbf5285d95b5822c024e8ae0b20`|
|`a295a5ff904b98bb283b36c35351f3f3c7459b0c`|2026-11-02T12:29:43+09:00|`e0f05fa5ffb534dc4d7940e8be003a0173e2e9c2`|
|`25bdcafa6b0ec8ecdb00b371c4ca203431e29038`|2026-11-02T12:47:46+09:00|`fd099f2728ac77b5937e580f84bf2f1fc07dbfaa`|
|`9d779065e7b3f56fc0228e4d26f16a29564aeee1`|2026-11-02T12:58:10+09:00|`92f45209ac1871101de8d1733eb5d14ec3ff8ce1`|

## 当前模型与继承入口

- [scenes/ferris-wheel-cabin-remake/CURRENT.json](files/scenes/ferris-wheel-cabin-remake/CURRENT.json)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.blend](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.blend](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.glb](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.glb)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.glb](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.glb)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.blend](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.blend](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.glb](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.glb)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.glb](files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.glb)。
- [scenes/ferris-wheel-cabin-remake/docs/remake-report.md](files/scenes/ferris-wheel-cabin-remake/docs/remake-report.md)。
