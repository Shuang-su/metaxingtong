# 森林脚本重放失败诊断归档

这是独立失败诊断证据，不是原场景恢复、成功改模或验收。

原始诊断 HEAD：`aff7f7258a70c4d565ecd4d5467434cf6de69e9a`，独立原历史分支：`refs/heads/history/forest-replay-diagnostic-original-20261104`。
`files/` 完整保存 66 个原文件及其原 Git blob；来源及 SHA256 清单见 `provenance.json`。
原森林历史 `2204e912a2929c032223ea011d86f5f81d331af2` 和既有归档路径均保留。

本包包含 6 张 640×360 失败林圈诊断图、world hash 比较、射线敏感性记录及独立 QA。
不含原始或重放的大模型文件；17 个对象 world hash 不同，不得称整场原件已恢复。
2 倍远林平移方案已被拒绝；代表基部中心射线检查不等于全根系支撑或全场碰撞验证。
归档执行器只做接收、普通 Git 和完整性核验，没有建模、渲染或重跑生产脚本。

远端完整性核验回执将在 `publication-verification/remote_verification.json` 中追加。
