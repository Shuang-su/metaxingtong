# 双 S 固定平面只读证据：Library version 1

原始 HEAD：`ce056043034a365549c05a38aaefa961d87c8f81`

精确诊断基线：`9df36daa8ec0be77e6a7e4e2c2ffd49d83770e14`；中间真实提交：`2465e07f1a6d107c15d2e078e9e62c33bc1f3303`。

本次仅追加 22 份原文件，不改变 380 份旧原件。完整 402 文件映射、12 提交树及原对象见同目录 provenance.json。上一版本根目录说明、原回执与所有旧路径保持原样。新回执位于 ../../publication-verification/v1/remote_verification.json。

- Read-only fixed-plane appearance evaluation and supplied independent QA; NOT APPLIED and source FAILED remain. No new model, geometry revision, rendering stage or complete scene is delivered.
- Exactly 22 files totaling 7,722,036 bytes were appended in two real commits. All 380 prior files remain byte-identical, including all production models, sources, formal renders, scripts and dependencies. New scripts under the analysis directory are retained as evidence and are not executed by this archive worker.
- The original 31-section S centerlines are not exactly planar. Fixed min/mean/max Y planes and two mutually exclusive existing source05 camera hypotheses produce 12 finite cases. Projecting observed source05 pixels back to source05 is a construction identity, not source validation. The two camera-conditioned results are not a shared recovered shape.
- Only source05 rows 150-174 and 206-275 are used. Cap-neighborhood v0 observations are retained but excluded from final controls. The mixed-identity 175-205 interval, obscured lower connections and source02 caps remain unknown. Bright-core midpoints are appearance proxies, not recovered physical axes; adjacent rows are correlated.
- Supplied independent QA records 12 cases with 95 samples each and 24 target-row checks, with missing source02 row560 coverage retained for the alternate camera. Slight exceedance of a subjective 3px band does not prove real planarity impossible or every curvature revision impossible. No tube shell was generated, so no seam, collision, support or surface acceptance is established.
- Archival verification checks original bytes, hashes, object identities, commit trees, frozen manifests and QA input bindings. It does not repeat Blender calculations, infer geometry, execute producer scripts or render. Existing failures and the intermediate 2465e07 commit are preserved.
- All old archive paths remain unchanged. New metadata and the new verification receipt are versioned append-only under versions/v1 and publication-verification/v1. Full source history is preserved on the existing diagnostic history ref; production and every other remote ref remain unchanged. Space version 1 is retained for the parent to release after readback.
