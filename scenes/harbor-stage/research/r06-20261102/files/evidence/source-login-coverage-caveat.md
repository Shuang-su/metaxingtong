# 原生来源登录记录覆盖：不补造证据

初始 `sources/preliminary/manifest.json` 明确记录既有登录头像、账户收藏/历史与通知等 UI 证据，未读取凭据或另行认证。

后续 `sources/official-preview/manifest.json` 的 4 帧，以及 `sources/live-companion/manifest.json` 与 `4k-supplement-manifest.json` 的 2 帧，保存了画质选择/实际解码/原生 PNG/暂停前后状态，但原 manifest 没有逐帧登录字段。采集 owner 后补的 `sources/login-evidence-audit-sidecar-20261102.json` 确认同母云 Chrome 工作流程，且其本人期间无登录/登出/账号切换/凭据访问；它绑定未改原 manifest 的 SHA。首帧有 00:45:07 账号 UI 观察，后 6 帧仍没有逐帧账号 UI 观察时间，因此仅是有限工作流连续性事实，不追认逐帧登录证明，也不由画质菜单推断会员身份。

因此不能把初始登录记录自动写成后续 6 帧均已逐帧再验证。原 manifest 与原图不重写；此项是来源记录缺口，不把 PNG 的真实尺寸/SHA/暂停状态改判为不存在，也不把菜单请求 4K 冒充实际 4K。若后续取得可靠补充，应以新的真实记录补入，不改写过去完成状态。整场仍是来源未验收候选。
